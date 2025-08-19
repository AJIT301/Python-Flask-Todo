import os
import re
import tempfile
import logging
import pytest

from app.sanitize_module import sanitize_input, calculate_total_score, detect_script_mix


@pytest.fixture
def log_file():
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".log") as f:
        yield f.name
    os.unlink(f.name)


@pytest.fixture(autouse=True)
def mock_logger(log_file):
    from app.sanitize_module import logger
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.WARNING)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.propagate = False
    yield logger

    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)


class TestSanitizeInput:
    def test_xss_script_tag(self):
        text = '<script>alert("XSS")</script>'
        cleaned, score, matches = sanitize_input(text)  # Uses default "balanced" mode
        assert score >= 4
        assert any("Script tag" in m[2] for m in matches)
        assert "<" not in cleaned
        assert ">" not in cleaned

    def test_sql_classic_tautology(self):
        text = "' OR 1=1 --"
        cleaned, score, matches = sanitize_input(text)
        assert score >= 6
        assert any("Classic SQLi tautology" in m[2] for m in matches)

    def test_command_injection(self):
        text = "; rm -rf /"
        cleaned, score, matches = sanitize_input(text)
        assert score >= 4
        assert any("Command injection" in m[2] for m in matches)

    def test_path_traversal(self):
        text = "../../../etc/passwd"
        cleaned, score, matches = sanitize_input(text)
        assert score >= 3
        assert any("Path traversal" in m[2] for m in matches)

    def test_html_event_handler(self):
        text = '<img src="x" onerror="alert(1)">'
        cleaned, score, matches = sanitize_input(text)  # Uses default "balanced" mode
        assert score >= 5
        assert any("HTML event handler" in m[2] for m in matches)
        assert "<" not in cleaned
        assert ">" not in cleaned

    def test_javascript_uri(self):
        text = 'javascript:alert(1)'
        cleaned, score, matches = sanitize_input(text)
        assert score >= 4
        assert any("JavaScript URI" in m[2] for m in matches)


class TestScoring:
    def test_score_accumulation(self):
        text = "' OR 1=1; DROP TABLE users--"
        score, matches = calculate_total_score(text)
        assert score >= 10
        descs = [m[2] for m in matches]
        assert "Classic SQLi tautology" in descs
        assert "-- + SQL keyword boost" in descs

    def test_contextual_boost(self):
        text = "UPDATE users SET pwd='123'--"
        score, matches = calculate_total_score(text)
        assert score >= 7
        assert any(m[2] == "-- + SQL keyword boost" for m in matches)

    def test_no_false_positives_on_safe_text(self):
        text = "I'm just saying hello, world!"
        score, matches = calculate_total_score(text)
        assert score == 1
        assert len(matches) == 1


class TestUnicodeAndScripts:
    def test_lithuanian_unicode_allowed(self):
        text = "Ąžuolas, Čiurlionis, Širvintos, Ūla"
        cleaned, score, matches = sanitize_input(text, allow_unicode=True)
        assert score == 0
        assert matches == []
        assert "Ąžuolas" in cleaned
        assert "Čiurlionis" in cleaned
        assert "Širvintos" in cleaned
        assert "Ūla" in cleaned
        # Verify all Lithuanian letters are preserved
        lithuanian_letters = "ąčęėįšųūžĄČĘĖĮŠŲŪŽ"
        for letter in lithuanian_letters:
            if letter in text:
                assert letter in cleaned, f"Lithuanian letter '{letter}' was not preserved"

    def test_lithuanian_unicode_disabled(self):
        text = "Ąžuolas, Čiurlionis"
        cleaned, score, matches = sanitize_input(text, allow_unicode=False)
        assert score == 0
        assert matches == []
        # Should still preserve Lithuanian letters even when allow_unicode=False
        # because they're in Latin Extended range
        assert "Ąžuolas" in cleaned
        assert "Čiurlionis" in cleaned

    def test_mixed_script_detection(self):
        text = "рaypal.com"  # Cyrillic 'р'
        _, score, matches = sanitize_input(text)
        assert score >= 3
        assert any("homoglyph" in m[2] for m in matches)

    def test_greek_not_allowed(self):
        text = "Δ = b² - 4ac"
        _, score, matches = sanitize_input(text)
        assert score >= 3
        assert any("homoglyph" in m[2] for m in matches)


class TestSanitizationOptions:
    def test_remove_specials_none(self):
        text = 'He said: "rm -rf /"'
        cleaned, score, _ = sanitize_input(text, remove_specials="none")
        assert cleaned == 'He said: "rm -rf /"'
        assert score >= 4

    def test_remove_specials_balanced(self):
        text = '"><script>drop</script>'
        cleaned, _, _ = sanitize_input(text, remove_specials="balanced")
        assert "<" not in cleaned
        assert ">" not in cleaned
        assert '"' in cleaned  # Quotes should remain in balanced mode

    def test_remove_specials_strict(self):
        text = '"; DROP TABLE --'
        cleaned, _, _ = sanitize_input(text, remove_specials="strict")
        assert '"' not in cleaned
        assert ";" not in cleaned
        assert "\\" not in cleaned
        assert "<" not in cleaned
        assert ">" not in cleaned


class TestOutputAndSafety:
    def test_log_escape_newlines(self, log_file):
        text = 'Hello\nDROP TABLE;\r\n--'
        sanitize_input(text)
        with open(log_file, "r", encoding="utf-8") as f:
            log_content = f.read()
        assert "\\n" in log_content
        assert "\\r" in log_content

    def test_empty_input(self):
        cleaned, score, matches = sanitize_input("")
        assert cleaned == ""
        assert score == 0
        assert matches == []

    def test_none_input(self):
        cleaned, score, matches = sanitize_input(None)
        assert cleaned == ""
        assert score == 0
        assert matches == []

    def test_only_whitespace(self):
        cleaned, score, matches = sanitize_input("   \t\n   ")
        assert cleaned == ""
        assert score == 0
        assert matches == []