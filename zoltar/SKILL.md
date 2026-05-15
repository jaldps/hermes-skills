---
name: zoltar
version: 1.3.0
description: Expert esoteric divination skill — real astrology, tarot, I Ching, numerology, runes. Uses verified APIs and calculation libraries, not roleplay.
category: esoteric
trigger: When the user asks for a horoscope, tarot reading, natal chart, I Ching hexagram, numerology report, rune casting, or any esoteric/divination guidance.
---

# Zoltar — Expert Esoteric Divination Engine

A grounded, theory-backed divination skill. Every reading draws from real calculation engines (Swiss Ephemeris via Kerykeion), live horoscope APIs, structured tarot/I Ching datasets, and documented esoteric traditions. No roleplay — real data, real interpretation.

## Divination Modes

### 1. Natal Chart / Birth Chart Analysis
**Engine:** Kerykeion (Python) — Swiss Ephemeris-based, Placidus houses, tropical zodiac.

**Requirements from user:**
- Date of birth (YYYY-MM-DD)
- Time of birth (HH:MM, 24h)
- City + Country of birth (or latitude/longitude + timezone)

**Steps:**
1. Run the calculation script (see `scripts/natal_chart.py`):
   ```
   python3 ~/.hermes/skills/zoltar/scripts/natal_chart.py "Name" YYYY MM DD HH MM "City" "NationCode"
   ```
   Example: `python3 ~/.hermes/skills/zoltar/scripts/natal_chart.py "Alex" 1990 6 15 10 30 "Sao Paulo" "BR"`
   
   If GeoNames fails (common), pass coordinates directly:
   ```
   python3 ~/.hermes/skills/zoltar/scripts/natal_chart.py "Name" YYYY MM DD HH MM LAT LNG "Timezone"
   ```
   Example: `python3 ~/.hermes/skills/zoltar/scripts/natal_chart.py "Alex" 1990 6 15 10 30 -23.55 -46.63 "America/Sao_Paulo"`
   
   The script has fallback coordinates for: Sao Paulo, Rio de Janeiro, New York, Los Angeles, London, Paris, Tokyo, Berlin, Madrid, Mexico City, Buenos Aires, Sydney, Mumbai, Bangkok.
2. The script outputs: all planet positions (sign + degree + house), house cusps, elements modalities summary, retrograde planets, and aspect list.
3. Interpret the raw data using established astrological theory:
   - **Sun sign** = core identity, ego, vitality
   - **Moon sign** = emotional nature, instincts, inner self
   - **Ascendant (Rising)** = outward personality, physical appearance, first impressions
   - **Mercury** = communication style, thinking patterns
   - **Venus** = love language, aesthetic preferences, values
   - **Mars** = drive, aggression, sexuality, action style
   - **Jupiter** = growth areas, luck, expansion, philosophy
   - **Saturn** = restrictions, lessons, discipline, karma
   - **Uranus/Neptune/Pluto** = generational influences, transformation
   - **House placements** = life areas where energies manifest
   - **Aspects** = how planetary energies interact (conjunction=blending, opposition=tension, trine=harmony, square=challenge, sextile=opportunity)
4. Cite the specific planetary positions and aspects that justify each interpretation. Example: "With Moon in Pisces in the 7th House trine Venus, your emotional nature is deeply empathetic and seeks spiritual connection in partnerships."

### 2. Daily Horoscope
**Engine:** Ohmanda Horoscope API (free, no key required, live daily horoscopes).

**Steps:**
1. Fetch the horoscope:
   ```
   curl -sL "https://ohmanda.com/api/horoscope/{sign}"
   ```
   Valid signs: aries, taurus, gemini, cancer, leo, virgo, libra, scorpio, sagittarius, capricorn, aquarius, pisces
2. The API returns: `{ "sign": "...", "date": "YYYY-MM-DD", "horoscope": "..." }`
3. Present the horoscope text as-is (it's already professionally written), then add your own brief commentary connecting it to current planetary transits if relevant.

### 3. Tarot Reading
**Engine:** Structured tarot dataset embedded in `references/tarot_cards.json` — 78 cards (22 Major Arcana + 56 Minor Arcana) with traditional meanings (Rider-Waite-Smith system).

**Spread types:**

**Single Card Draw:**
- Quick answer / daily guidance
- Shuffle: pick a random card from the full 78
- Present: card name, number, suit, upright meaning, reversed meaning
- Ask user if they want to consider reversal

**Three Card Spread (Past / Present / Future):**
- Most versatile spread
- Draw 3 cards without replacement
- Interpret each in its position context

**Celtic Cross (10 cards):**
- For deep, comprehensive readings
- Positions: 1=Present, 2=Challenge, 3=Foundation, 4=Past, 5=Outcome, 6=Near Future, 7=Self, 8=Environment, 9=Hopes/Fears, 10=Final Outcome
- Draw 10 cards without replacement

**Steps:**
1. Read the tarot data: `cat ~/.hermes/skills/zoltar/references/tarot_cards.json`
2. Use Python to draw random cards:
   ```python
   import json, random
   cards = json.load(open('~/.hermes/skills/zoltar/references/tarot_cards.json'))
   drawn = random.sample(cards, N)  # N = number of cards for the spread
   ```
3. For each card, present: name, position in spread, upright or reversed (50/50 chance), and the corresponding meaning from the dataset.
4. Synthesize a reading that connects the cards into a coherent narrative, citing the specific traditional meanings.

### 4. I Ching Divination
**Engine:** `iching` Python package (v3.8.2) — implements the traditional Shicao (yarrow stalk) method from the Book of Changes.

**Steps:**
1. Run the I Ching script:
   ```
   python3 ~/.hermes/skills/zoltar/scripts/iching_reading.py "the user's question"
   ```
2. The script performs the coin-casting method and returns the hexagram number, name, Chinese character, and changing lines.
3. Interpret using the I Ching text (the Judgment, Image, and changing line texts for the specific hexagram).
4. If there are changing lines, also interpret the second (relating) hexagram.
5. Reference the hexagram by its traditional name and number. Ground interpretation in the specific text, not generic wisdom.

### 5. Numerology
**Engine:** Pure Python calculation (Pythagorean system — the most widely used Western numerology method).

**Calculations:**
- **Life Path Number:** Sum of all digits in full birth date, reduced to single digit (except master numbers 11, 22, 33)
  - Example: 1990-06-15 → 1+9+9+0+0+6+1+5 = 31 → 3+1 = 4
- **Expression (Destiny) Number:** Full name converted to numbers (A=1, B=2... I=9, J=1...), summed and reduced
- **Soul Urge (Heart's Desire):** Vowels only in full name
- **Personality Number:** Consonants only in full name
- **Birthday Number:** Day of birth reduced (15 → 1+5 = 6)
- **Maturity Number:** Life Path + Expression, reduced

**Steps:**
1. Run: `python3 ~/.hermes/skills/zoltar/scripts/numerology.py "Full Name" YYYY MM DD`
2. The script outputs all core numbers with their traditional meanings.
3. Interpret each number using the standard Pythagorean meanings:
   - 1=Leadership/Independence, 2=Cooperation/Sensitivity, 3=Creativity/Expression, 4=Stability/Work, 5=Freedom/Change, 6=Responsibility/Love, 7=Spirituality/Analysis, 8=Power/Material, 9=Humanitarian/Completion
   - 11=Intuition/Illumination, 22=Master Builder, 33=Master Teacher

### 6. Rune Casting
**Engine:** Structured rune dataset in `references/runes_elder_futhark.json` — 24 Elder Futhark runes with traditional Norse/Icelandic meanings.

**Casting methods:**
- **Single Rune:** Quick guidance
- **Three Rune Spread (Norn Spread):** Past (Urd) / Present (Verdandi) / Future (Skuld)
- **Five Rune Cross:** Similar layout to Tarot Celtic Cross adapted for runes

**Steps:**
1. Read rune data: `cat ~/.hermes/skills/zoltar/references/runes_elder_futhark.json`
2. Draw randomly, considering merkstave (reversed) position with ~30% probability
3. Present: rune name, Anglo-Saxon rune poem excerpt, upright/reversed meaning
4. Interpret within the Norse tradition framework — runes are oracular, not deterministic

## General Interpretation Guidelines

1. **Always cite your sources.** When interpreting a natal chart, reference the specific planet-sign-house combination. When reading tarot, reference the card's traditional meaning. When casting runes, reference the rune poem.

2. **Be honest about limitations.** Astrology, tarot, I Ching, and runes are contemplative tools, not predictive instruments. Frame readings as "areas of focus" or "archetypal patterns," not as fortune-telling or medical/financial advice.

3. **Synthesize, don't list.** A reading should tell a story, not enumerate data points. Connect the dots between different elements.

4. **Respect the tradition.** Each system has its own internal logic:
   - Western astrology: elements (fire/earth/air/water), modalities (cardinal/fixed/mutable), dignities (rulership/exaltation/detriment/fall)
   - Tarot: RWS system with Major/Minor arcana, elemental associations (Wands=Fire, Cups=Water, Swords=Air, Pentacles=Earth)
   - I Ching: yin/yang, the eight trigrams, the sequence of the King Wen arrangement
   - Numerology: Pythagorean letter-number correspondence, core vs. cycle numbers
   - Runes: Elder Futhark three aettir, rune poems as primary source

5. **Language:** Respond in the user's preferred language (English or Spanish). Technical terms can be given in both languages (e.g., "Ascendente / Ascendant").

## Pitfalls

- **Kerykeion `.json()` returns a STRING, not a dict.** Always do `data = json.loads(raw) if isinstance(raw, str) else raw`. The natal_chart.py script handles this already.
- **Kerykeion uses `nation` not `country`** as the keyword argument. Passing `country=` raises TypeError.
- **Kerykeion requires GeoNames** for city lookup. The default shared username gets 401'd quickly. The script uses `hermes_zoltar` as fallback and has a CITY_COORDS dict for 14 major cities. If GeoNames fails, pass coordinates directly: `python3 natal_chart.py "Name" YYYY MM DD HH MM LAT LNG "Timezone"`. Users can get a free GeoNames username at https://www.geonames.org/login and set `KERYKEION_GEONAMES_USERNAME`.
- **Ohmanda API** returns only daily horoscopes, no weekly/monthly. Don't try other endpoints — they 403. Only endpoint: `https://ohmanda.com/api/horoscope/{sign}`.
- **I Ching `iching` PyPI package** — the module is NOT callable (`iching()` raises TypeError). Don't try `from iching import iching; oracle = iching()`. The custom `scripts/iching_reading.py` implements coin-casting independently with all 64 hexagram names.
- **Tarot JSON keys** — `tarot_cards.json` uses `upright` and `reversed` as keys for meanings. There is NO `description` key. If you try `card['description']` you'll get a KeyError. Use `card.get('upright', '')` and `card.get('reversed', '')` safely.
- **Tarot meanings** are from the Rider-Waite-Smith tradition. Don't mix in Thoth or Marseille system meanings without telling the user.
- **Numerology** has multiple systems (Pythagorean, Chaldean, Kabbalah). This skill uses Pythagorean. If the user asks for Chaldean, calculate differently (Chaldean uses 1-8 not 1-9, and number assignments differ).
- **Runes merkstave** (reversed) doesn't apply to all runes — some are symmetric and can't be reversed (Gebo, Hagalaz, Isa, Jera, Eihwaz, Sowilo, Ingwaz, Dagaz). The dataset marks these with `can_reverse: false`.
- **NEVER give medical, financial, or legal advice** through divination. If someone asks "should I invest in X" or "will my illness cure," redirect: "Divination is a reflective tool, not a substitute for professional advice."
- **Publishing to GitHub** — always check push permissions with `gh api repos/{owner}/{repo} --jq '.permissions'` before attempting `git push`. If `push: false`, fork first (`gh repo fork`) then push to the fork and create a PR. The `gh auth` token may belong to a different account than the repo owner.
- **Kerykeion v5 houses** — the `.json()` output may return houses as numeric cusp degrees instead of dicts with `sign` keys. The natal_chart.py script handles both formats (dict with sign/position, or bare number interpreted as degree). If houses still come back empty, check `house_1` through `house_12` keys as an alternate format.

## Generating HTML Reports

When the user asks for a "report", "document", "PDF", or "HTML" of their reading, generate a styled HTML file.

**Steps:**
1. Run all divination scripts first (natal chart, horoscope, numerology, tarot, runes).
2. Use the HTML template in `templates/reading-report.html` as the base structure.
3. Replace placeholder content with the actual reading data and interpretations.
4. Customize the color scheme: use `--gold`/`--purple` accents for masculine energy, `--rose`/`--rose-light` for feminine energy, or let the user pick.
5. Save to `~/Desktop/Hermes/zoltar-{name}-reading.html` (English) or `zoltar-{name}-lectura.html` (Spanish).
6. Open in browser to verify: `open file:///Users/jose/Desktop/Hermes/zoltar-{name}-reading.html`.

**Language:** If the user communicates in Spanish or asks for the reading in Spanish, produce the entire HTML report in Spanish. Technical terms can be bilingual (e.g., "Ascendente / Ascendant").

**Template:** See `templates/reading-report.html` for the full CSS + structure skeleton. Copy it and replace placeholders with actual reading content.

**Color schemes** — uncomment the CSS variable block at the top:
- Gold/Purple (default/masculine): `--accent:#c9a84c; --accent-alt:#4a2d6e`
- Rose/Gold (feminine): `--accent:#c95a7c; --accent-alt:#a04268`
- Emerald (neutral): `--accent:#4eca8b; --accent-alt:#2d6e4e`

**Key design principles:**
- Dark background (#0a0a12), serif headings (Cinzel), serif body (Cormorant Garamond) for readings, sans-serif (Raleway) for labels.
- Cover page with subject name, birth info, and date of reading.
- One section per divination mode (natal chart, horoscope, numerology, tarot, runes) + synthesis section.
- Print-ready CSS included (white background for print, page breaks between sections).
- No interactive elements needed — this is a static document.

**Alternate output:** If the user wants a PDF, tell them to open the HTML in a browser and use Cmd+P → "Save as PDF". The print CSS handles the conversion automatically.

## Data Sources

See `references/api_research.md` for the full survey of free esoteric APIs, verified endpoints, and dead alternatives.

See `references/publishing-checklist.md` for sanitization and GitHub publishing procedures when sharing this skill publicly.
