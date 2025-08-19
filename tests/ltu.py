#!/usr/bin/env python3
# simple_ltu_debug.py - Simple Lithuanian debug test

print("=== Lithuanian Character Test ===")

# Test basic Lithuanian characters
lithuanian_chars = "ąčęėįšųūžĄČĘĖĮŠŲŪŽ"
test_words = ["Ąžuolas", "Čiurlionis", "Širvintos", "Ūla", "Žuvėdra"]

print("Basic character test:")
for char in lithuanian_chars:
    print(f"  '{char}' (Unicode: U+{ord(char):04X})")

print("\nWord test:")
for word in test_words:
    print(f"  '{word}' -> bytes: {word.encode('utf-8')}")

print("\nNow copy this file to the same directory as your sanitize_module.py")
print("and add this at the top:")
print()
print("# Add this line after the existing imports:")
print("from sanitize_module import sanitize_input")
print()
print("# Then add this test:")
print("test_sentence = 'Aš esu iš Lietuvos. Mano vardas Ąžuolas.'")
print("cleaned, score, matches = sanitize_input(test_sentence)")
print("print(f'Original: {test_sentence}')")
print("print(f'Cleaned:  {cleaned}')")
print("print(f'Same? {test_sentence == cleaned}')")

# If we can find the sanitize module, test it
try:
    # Try different import paths
    import sys
    import os
    
    # Try parent directory
    sys.path.insert(0, '..')
    try:
        from app.sanitize_module import sanitize_input
        found_module = True
    except ImportError:
        try:
            sys.path.insert(0, '../app')
            from app.sanitize_module import sanitize_input  
            found_module = True
        except ImportError:
            found_module = False
    
    if found_module:
        print("\n=== ACTUAL SANITIZATION TEST ===")
        test_sentence = "Aš esu iš Lietuvos. Mano vardas Žuvėdra."
        print(f"Original: '{test_sentence}'")
        
        cleaned, score, matches = sanitize_input(test_sentence)
        print(f"Cleaned:  '{cleaned}'")
        print(f"Score: {score}")
        print(f"Matches: {matches}")
        print(f"Characters preserved? {test_sentence == cleaned}")
        
        if test_sentence != cleaned:
            print("\nDifferences found:")
            for i, (orig, clean) in enumerate(zip(test_sentence, cleaned)):
                if orig != clean:
                    print(f"  Position {i}: '{orig}' -> '{clean}'")
    else:
        print("\n⚠️  Could not import sanitize_module")
        print("Please run this from the correct directory or fix the import path")
        
except Exception as e:
    print(f"\n❌ Error during testing: {e}")

print("\n" + "="*50)
print("If Lithuanian characters show as question marks or boxes,")
print("the issue is likely:")
print("1. Terminal/console encoding (try: chcp 65001)")
print("2. Database charset not set to UTF-8")
print("3. Web page missing UTF-8 meta tag")