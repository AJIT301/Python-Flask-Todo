# sanitize_module.py

import logging
import os
import re
import unicodedata
import html
from html import unescape
from urllib.parse import unquote_plus

# === Logging Setup ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE_PATH = os.path.join(SCRIPT_DIR, "..", "suspicious_input.log")

logger = logging.getLogger("InputSanitizer")
logger.setLevel(logging.WARNING)

if not logger.handlers:
    file_handler = logging.FileHandler(LOG_FILE_PATH, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.WARNING)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False
    logger.warning("Logger initialized - log file location: " + LOG_FILE_PATH)


# === Suspicious Patterns: (regex, severity, description) ===
SUSPICIOUS_PATTERNS = [
    # === SQL Injection ===
    (r"(?i)\b(select|insert|update|delete|drop|truncate|create|alter|exec|execute)\b", 2, "SQL keyword"),
    (r"(?i)\b(select|union).+?(from|where|join)", 4, "SQL clause structure"),
    (r"(?i)('|\")\s*(or|and)\s*['\"]?(1|a|a')\s*=\s*['\"]?(1|a|a')", 4, "Classic SQLi tautology"),
    (r"(?i);(?:\s*(drop|delete|shutdown|exec|system|cmd))", 4, "Stacked query + dangerous command"),
    (r"--|#|/\*.*?\*/", 3, "SQL comment"),

    # === XSS ===
    (r"(?i)<script[^>]*>.*?</script>", 4, "Script tag"),
    (r"(?i)javascript:", 4, "JavaScript URI"),
    (r"(?i)on\w+\s*=", 3, "HTML event handler"),
    (r"(?i)<iframe|<img.*?onerror", 4, "Malicious iframe/img"),
    (r"(?i)vbscript:", 3, "VBScript URI"),

    # === Command Injection ===
    (r";\s*(rm|cat|ls|ps|whoami|nc|bash|sh|wget|curl)\b", 4, "Command injection"),
    (r"(rm|cat|ls|ps|whoami|nc|bash|sh|wget|curl)\s*[-/]", 3, "Suspicious command with flags"),

    # === Path Traversal ===
    (r"\.\./|\.\.\\", 3, "Path traversal"),

    # === Dangerous Chars (contextual) ===
    (r"[<>]", 2, "HTML angle brackets"),
    (r"[\"']", 1, "Quotes (low severity alone)"),
    (r"[;&|`$]", 2, "Shell metacharacters"),
]

SUSPICIOUS_PATTERNS.sort(key=lambda x: x[1], reverse=True)


def normalize_payload(text: str) -> str:
    """
    Normalize common encodings to detect obfuscated payloads.
    """
    # Decode URL encoding
    text = unquote_plus(text)
    # Decode HTML entities
    text = unescape(text)
    return text


def calculate_total_score(text: str) -> tuple[int, list[tuple[str, int, str]]]:
    """
    Analyze text for suspicious patterns and return total score and matches.
    """
    if not isinstance(text, str) or not text.strip():
        return 0, []

    # Normalize payload before scoring
    normalized = normalize_payload(text)

    matched = []
    score = 0

    for pattern, severity, desc in SUSPICIOUS_PATTERNS:
        if re.search(pattern, normalized, re.DOTALL | re.IGNORECASE):
            score += severity
            matched.append((pattern, severity, desc))

    # Contextual boost: SQL keyword + comment
    has_sql_kw = any(re.search(p, normalized, re.I) for p in [r"\b(update|drop|select|insert|delete)\b"])
    has_comment = bool(re.search(r"--|#|/\*", normalized))
    if has_sql_kw and has_comment:
        score += 2
        matched.append(("contextual_boost", 2, "-- + SQL keyword boost"))

    return score, matched


def detect_script_mix(text: str) -> bool:
    """
    Detect mixed scripts (e.g., Latin + Cyrillic) – possible homoglyph attack.
    Allows Latin with diacritics (e.g., Lithuanian: ąčęėįšųū).
    """
    cyrillic = re.compile(r"[\u0400-\u04FF]")
    other_scripts = re.compile(r"[\u0370-\u03FF\u0530-\u058F\u0600-\u06FF]")

    has_cyrillic = bool(cyrillic.search(text))
    has_other_script = bool(other_scripts.search(text))

    if (has_cyrillic or has_other_script) and re.search(r"[a-zA-Z]", text):
        return True

    return False


def sanitize_input(
    text: str,
    *,
    allow_unicode: bool = True,
    escape_html: bool = False,
    compress_whitespace: bool = True,
    remove_specials: str = "balanced",  # "none", "balanced", "strict"
    log_suspicious: bool = True,
    max_length: int = 5000,  # Prevent DoS
    context: dict = None,  # Optional metadata (e.g., IP, user)
) -> tuple[str, int, list[tuple[str, int, str]]]:
    """
    Enhanced input sanitizer with scoring, normalization, and logging.
    """
    if not isinstance(text, str):
        return "", 0, []

    # Truncate overly long inputs
    if len(text) > max_length:
        text = text[:max_length]
        logger.warning(f"Input truncated to {max_length} chars")

    original_text = text.strip()
    if not original_text:
        return "", 0, []

    # === 1. Normalize Payload ===
    normalized_text = normalize_payload(original_text)

    # === 2. Calculate Score ===
    total_score, matched_patterns = calculate_total_score(normalized_text)

    # === 3. Detect Mixed Scripts ===
    if detect_script_mix(normalized_text):
        total_score += 3
        matched_patterns.append(("mixed_script", 3, "Possible homoglyph attack (mixed scripts)"))

    # === 4. Log Suspicious Input ===
    if log_suspicious and total_score > 0:
        safe_log_text = (
            repr(normalized_text)
            .replace("\\n", "\\\\n")
            .replace("\\r", "\\\\r")
            .replace("\\t", "\\\\t")
        )
        log_msg = f"Suspicious input detected: {safe_log_text} | Score={total_score} | Matches={[desc for _, _, desc in matched_patterns]}"
        if context:
            log_msg += f" | Context={context}"
        logger.warning(log_msg)
        for handler in logger.handlers:
            handler.flush()

    # === 5. Sanitization Pipeline ===
    text = original_text

    # Unicode handling
    if not allow_unicode:
        allowed_chars = []
        for char in text:
            code_point = ord(char)
            if (code_point <= 0x024F) or char.isspace():
                allowed_chars.append(char)
        text = ''.join(allowed_chars)
    else:
        text = unicodedata.normalize("NFC", text)

    # Remove control characters
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

    if compress_whitespace:
        text = re.sub(r"\s+", " ", text).strip()

    # Remove special characters based on policy
    if remove_specials == "strict":
        dangerous_chars = ['"', "'", '\\', '<', '>', '`', '|', ';', '&', '$', '(', ')', '[', ']', '{', '}']
        for char in dangerous_chars:
            text = text.replace(char, '')
    elif remove_specials == "balanced":
        dangerous_chars = ['\\', '<', '>', '`', '|', ';', '&', '$']
        for char in dangerous_chars:
            text = text.replace(char, '')

    if escape_html:
        text = html.escape(text)

    return text, total_score, matched_patterns