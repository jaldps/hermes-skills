# Hermes Skills

Custom skills for [Hermes Agent](https://hermes-agent.nousresearch.com/).

## Skills

### 🔮 Zoltar — Expert Esoteric Divination Engine

Real astrology, tarot, I Ching, numerology, and runes. Uses verified calculation engines (Swiss Ephemeris via Kerykeion), live horoscope APIs, structured tarot/I Ching datasets, and documented esoteric traditions. No roleplay — real data, real interpretation.

**Modes:**
- Natal Chart / Birth Chart Analysis (Kerykeion + Swiss Ephemeris)
- Daily Horoscope (Ohmanda API)
- Tarot Reading (78-card Rider-Waite-Smith dataset)
- I Ching Divination (traditional coin-casting method)
- Numerology (Pythagorean system)
- Rune Casting (24 Elder Futhark runes)

### 🎭 Antiscammer — Anti-Scammer Toolkit

Script-bomb WhatsApp/Telegram/Discord contacts with endless text, and reply to scam emails with impossibly verbose bureaucratic nonsense.

**Modes:**
- **WhatsApp Script Bomb** — flood a WhatsApp Web chat with Shrek script, Bee Movie script, or custom text, sent line-by-line (keeps going even after they close the convo)
- **Telegram/Discord Script Bomb** — same concept for Telegram Web and Discord browser
- **Scam Email Replier** — generate 2000-3000 word replies in the style of a pretentious professor + corrupt lawyer + government bureaucrat. Output only — you copy-paste the text yourself.

### 🪞 Book Mirror — Personalized Chapter-by-Chapter Book Analysis

Takes any book + everything the AI knows about you → produces a personalized two-column analysis. Left column: what the author says (detailed enough to skip the book). Right column: how it applies to your specific life, using your actual words, situations, people, and patterns.

Concept by [Garry Tan](https://x.com/garrytan/status/2049059060427952164) (President & CEO of Y Combinator).

**Pipeline:**
1. Extract text from PDF or EPUB
2. Split into chapters
3. Build context pack from memory (bio, patterns, relationships, quotes)
4. Per-chapter two-column analysis
5. Fact-check personal claims
6. Generate styled HTML report

## Installation

Copy any skill folder to `~/.hermes/skills/`:

```bash
# All skills
cp -r zoltar antiscammer book-mirror ~/.hermes/skills/

# Individual
cp -r book-mirror ~/.hermes/skills/
```

### Dependencies

```bash
# Zoltar
pip install kerykeion iching

# Book Mirror
pip install pymupdf ebooklib beautifulsoup4 reportlab

# Antiscammer — no dependencies (runs in browser)
```

## License

MIT
