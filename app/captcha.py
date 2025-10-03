import random

# Visual CAPTCHA system - each CAPTCHA has an id, question, and correct answer
CAPTCHA_CHALLENGES = [
    {
        'id': 1,
        'question': 'How many circles do you count? [• • • •]',
        'answer': '4'
    },
    {
        'id': 2,
        'question': 'What color are the circles? [🔵 🟡 🔵 🟡]',
        'answer': 'blue yellow blue yellow'
    },
    {
        'id': 3,
        'question': 'Which shape is missing? [□ △ ? △]',
        'answer': 'square'
    },
    {
        'id': 4,
        'question': 'How many squares are here? [☑ ▪ ▪ ☑]',
        'answer': '4'
    },
    {
        'id': 5,
        'question': 'Which animal is shown? [🐱 🐶 🐢]',
        'answer': 'cat dog turtle'
    },
]

def get_random_visual_captcha():
    """Returns a random visual CAPTCHA challenge"""
    challenge = random.choice(CAPTCHA_CHALLENGES)
    return challenge

def validate_visual_captcha(captcha_id, user_answer):
    """Validates the user's CAPTCHA answer"""
    try:
        captcha_id = int(captcha_id)
        challenge = next((c for c in CAPTCHA_CHALLENGES if c['id'] == captcha_id), None)
        if challenge:
            # Case-insensitive matching, allow minor typos
            user_answer_lower = user_answer.lower().strip()
            expected_lower = challenge['answer'].lower()
            return user_answer_lower == expected_lower or user_answer_lower in expected_lower.split()
        return False
    except (ValueError, TypeError):
        return False
