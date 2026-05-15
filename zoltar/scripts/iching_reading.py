#!/usr/bin/env python3
"""I Ching reading using the iching Python package (coin method)."""
import sys
import json
import random

HEXAGRAM_NAMES = {
    1: "The Creative (Qian)", 2: "The Receptive (Kun)", 3: "Difficulty at the Beginning (Zhun)",
    4: "Youthful Folly (Meng)", 5: "Waiting (Xu)", 6: "Conflict (Song)",
    7: "The Army (Shi)", 8: "Holding Together (Bi)", 9: "The Taming Power of the Small (Xiao Xu)",
    10: "Treading (Li)", 11: "Peace (Tai)", 12: "Standstill (Pi)",
    13: "Fellowship (Tong Ren)", 14: "Great Possession (Da You)", 15: "Modesty (Qian)",
    16: "Enthusiasm (Yu)", 17: "Following (Sui)", 18: "Work on What Has Been Spoiled (Gu)",
    19: "Approach (Lin)", 20: "Contemplation (Guan)", 21: "Biting Through (Shi He)",
    22: "Grace (Bi)", 23: "Splitting Apart (Bo)", 24: "Return (Fu)",
    25: "Innocence (Wu Wang)", 26: "The Taming Power of the Great (Da Xu)",
    27: "Corners of the Mouth (Yi)", 28: "Preponderance of the Great (Da Guo)",
    29: "The Abysmal Water (Kan)", 30: "The Clinging Fire (Li)",
    31: "Influence (Xian)", 32: "Duration (Heng)", 33: "Retreat (Dun)",
    34: "The Power of the Great (Da Zhuang)", 35: "Progress (Jin)",
    36: "Darkening of the Light (Ming Yi)", 37: "The Family (Jia Ren)",
    38: "Opposition (Kui)", 39: "Obstruction (Jian)", 40: "Deliverance (Jie)",
    41: "Decrease (Sun)", 42: "Increase (Yi)", 43: "Breakthrough (Guai)",
    44: "Coming to Meet (Gou)", 45: "Gathering Together (Cui)",
    46: "Pushing Upward (Sheng)", 47: "Oppression (Kun)", 48: "The Well (Jing)",
    49: "Revolution (Ge)", 50: "The Caldron (Ding)", 51: "The Arousing Thunder (Zhen)",
    52: "Keeping Still Mountain (Gen)", 53: "Development (Jian)",
    54: "The Marrying Maiden (Gui Mei)", 55: "Abundance (Feng)", 56: "The Wanderer (Lu)",
    57: "The Gentle Wind (Xun)", 58: "The Joyous Lake (Dui)",
    59: "Dispersion (Huan)", 60: "Limitation (Jie)", 61: "Inner Truth (Zhong Fu)",
    62: "Preponderance of the Small (Xiao Guo)", 63: "After Completion (Ji Ji)",
    64: "Before Completion (Wei Ji)"
}

TRIGRAMS = {
    "yang_yang_yang": "Qian (Heaven/Creative)",
    "yin_yin_yin": "Kun (Earth/Receptive)",
    "yang_yang_yin": "Dui (Lake/Joyous)",
    "yang_yin_yin": "Zhen (Thunder/Arousing)",
    "yin_yang_yang": "Xun (Wind/Gentle)",
    "yin_yin_yang": "Gen (Mountain/Keeping Still)",
    "yang_yin_yang": "Li (Fire/Clinging)",
    "yin_yang_yin": "Kan (Water/Abysmal)",
}

def cast_coins():
    """Cast three coins to determine a line (coin method)."""
    # Heads=3 (yang), Tails=2 (yin)
    coins = [random.choice([2, 3]) for _ in range(3)]
    total = sum(coins)
    # 6=old yin (changing), 7=young yang, 8=young yin, 9=old yang (changing)
    return total

def cast_hexagram():
    """Cast a full hexagram (6 lines, bottom to top)."""
    lines = []
    changing = []
    for i in range(6):
        value = cast_coins()
        if value == 6:
            lines.append("yin")
            changing.append(i)  # old yin changes to yang
        elif value == 7:
            lines.append("yang")
        elif value == 8:
            lines.append("yin")
        elif value == 9:
            lines.append("yang")
            changing.append(i)  # old yang changes to yin
    return lines, changing

def lines_to_number(lines):
    """Convert 6 lines to hexagram number using binary encoding."""
    # Bottom line is least significant bit
    binary = 0
    for i, line in enumerate(lines):
        if line == "yang":
            binary |= (1 << i)
    return binary + 1  # 1-indexed

def main():
    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "general guidance"
    
    lines, changing = cast_hexagram()
    hex_num = lines_to_number(lines)
    
    output = {
        "question": question,
        "hexagram_number": hex_num,
        "hexagram_name": HEXAGRAM_NAMES.get(hex_num, f"Hexagram {hex_num}"),
        "lines": lines,  # bottom to top
        "changing_lines": changing,
        "has_changing": len(changing) > 0,
    }
    
    # If changing lines exist, calculate the relating hexagram
    if changing:
        new_lines = lines.copy()
        for i in changing:
            new_lines[i] = "yang" if new_lines[i] == "yin" else "yin"
        relating_num = lines_to_number(new_lines)
        output["relating_hexagram"] = {
            "number": relating_num,
            "name": HEXAGRAM_NAMES.get(relating_num, f"Hexagram {relating_num}"),
        }
        output["changing_line_positions"] = [i + 1 for i in changing]  # 1-indexed for humans
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
