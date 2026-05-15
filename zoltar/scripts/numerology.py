#!/usr/bin/env python3
"""Pythagorean Numerology Calculator."""
import sys
import json

# Pythagorean letter-number mapping
LETTER_VALUES = {
    'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9,
    'j': 1, 'k': 2, 'l': 3, 'm': 4, 'n': 5, 'o': 6, 'p': 7, 'q': 8, 'r': 9,
    's': 1, 't': 2, 'u': 3, 'v': 4, 'w': 5, 'x': 6, 'y': 7, 'z': 8,
}

VOWELS = set('aeiou')

NUMBER_MEANINGS = {
    1: "Leadership, Independence, Individuality, Initiative, Pioneering spirit",
    2: "Cooperation, Sensitivity, Diplomacy, Balance, Partnership, Receptivity",
    3: "Creativity, Self-Expression, Communication, Optimism, Joy, Sociability",
    4: "Stability, Discipline, Work, Structure, Foundation, Practicality, Order",
    5: "Freedom, Change, Adventure, Versatility, Curiosity, Sensory experience",
    6: "Responsibility, Love, Nurturing, Harmony, Service, Domesticity, Healing",
    7: "Spirituality, Analysis, Wisdom, Introspection, Research, Seeking truth",
    8: "Power, Material mastery, Authority, Achievement, Business, Abundance",
    9: "Humanitarianism, Completion, Compassion, Universal love, Selflessness",
    11: "Master Intuitive, Illumination, Spiritual insight, Inspiration, Idealism",
    22: "Master Builder, Visionary creation, Practical idealism, Great achievement",
    33: "Master Teacher, Spiritual upliftment, Compassionate service, Healing mastery",
}

def reduce(n):
    """Reduce to single digit, preserving master numbers."""
    if n in (11, 22, 33):
        return n
    while n > 9:
        n = sum(int(d) for d in str(n))
        if n in (11, 22, 33):
            return n
    return n

def name_to_number(name, filter_func=None):
    """Convert name to number using Pythagorean system."""
    total = 0
    for ch in name.lower():
        if ch.isalpha() and ch in LETTER_VALUES:
            if filter_func is None or filter_func(ch):
                total += LETTER_VALUES[ch]
    return reduce(total)

def main():
    if len(sys.argv) < 5:
        print('Usage: numerology.py "Full Name" YYYY MM DD')
        print('Example: numerology.py "Alex Morgan" 1990 6 15')
        sys.exit(1)
    
    full_name = sys.argv[1]
    year = int(sys.argv[2])
    month = int(sys.argv[3])
    day = int(sys.argv[4])
    
    # Life Path Number
    life_path = reduce(reduce(month) + reduce(day) + reduce(sum(int(d) for d in str(year))))
    
    # Expression (Destiny) Number — all letters
    expression = name_to_number(full_name, filter_func=None)
    
    # Soul Urge (Heart's Desire) — vowels only
    soul_urge = name_to_number(full_name, filter_func=lambda ch: ch in VOWELS)
    
    # Personality Number — consonants only
    personality = name_to_number(full_name, filter_func=lambda ch: ch not in VOWELS and ch.isalpha())
    
    # Birthday Number
    birthday_num = reduce(day)
    
    # Maturity Number
    maturity = reduce(life_path + expression)
    
    # Pinnacle cycles (4 periods in life)
    # 1st pinnacle: month + day reduced, 2nd: day + year, 3rd: 1st+2nd, 4th: month + year
    p1 = reduce(reduce(month) + reduce(day))
    p2 = reduce(reduce(day) + reduce(sum(int(d) for d in str(year))))
    p3 = reduce(p1 + p2)
    p4 = reduce(reduce(month) + reduce(sum(int(d) for d in str(year))))
    
    # Pinnacle ages (based on life path)
    if life_path in (11, 22, 33):
        base_age = 36 - (life_path % 9)
    else:
        base_age = 36 - life_path
    
    output = {
        "full_name": full_name,
        "birth_date": f"{year}-{month:02d}-{day:02d}",
        "system": "Pythagorean",
        "core_numbers": {
            "life_path": {"number": life_path, "meaning": NUMBER_MEANINGS.get(life_path, "?")},
            "expression": {"number": expression, "meaning": NUMBER_MEANINGS.get(expression, "?")},
            "soul_urge": {"number": soul_urge, "meaning": NUMBER_MEANINGS.get(soul_urge, "?")},
            "personality": {"number": personality, "meaning": NUMBER_MEANINGS.get(personality, "?")},
            "birthday": {"number": birthday_num, "meaning": NUMBER_MEANINGS.get(birthday_num, "?")},
            "maturity": {"number": maturity, "meaning": NUMBER_MEANINGS.get(maturity, "?")},
        },
        "pinnacle_cycles": {
            "first": {"number": p1, "ages": f"0 to {base_age}", "meaning": NUMBER_MEANINGS.get(p1, "?")},
            "second": {"number": p2, "ages": f"{base_age+1} to {base_age+9}", "meaning": NUMBER_MEANINGS.get(p2, "?")},
            "third": {"number": p3, "ages": f"{base_age+10} to {base_age+18}", "meaning": NUMBER_MEANINGS.get(p3, "?")},
            "fourth": {"number": p4, "ages": f"{base_age+19}+", "meaning": NUMBER_MEANINGS.get(p4, "?")},
        },
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
