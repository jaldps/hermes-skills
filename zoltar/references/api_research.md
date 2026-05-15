# Esoteric API & Library Research (2026-05-15)

Survey of free APIs and libraries for divination/astrology skills. Tested live.

## VERIFIED WORKING

### Ohmanda Horoscope API
- URL: `https://ohmanda.com/api/horoscope/{sign}`
- Method: GET, no auth, no key
- Signs: aries, taurus, gemini, cancer, leo, virgo, libra, scorpio, sagittarius, capricorn, aquarius, pisces
- Returns: `{ "sign": "...", "date": "YYYY-MM-DD", "horoscope": "..." }`
- Scope: Daily only. No weekly/monthly. No other endpoints work (403).
- Quality: Professionally written, includes planetary transit references.

### Kerykeion (Python, PyPI)
- `pip install kerykeion` — v5.12.8
- Swiss Ephemeris-based natal chart calculations
- Features: planet positions, signs, houses (Placidus), elements, modalities, retrograde detection
- Key quirks:
  - `.json()` returns a JSON **string** not dict — must `json.loads()`
  - Parameter is `nation=` not `country=`
  - GeoNames username required for city lookup (default gets 401'd)
  - Pass `lat=`, `lng=`, `tz_str=` to bypass GeoNames entirely
  - `aspects` attribute not available in v5 AstrologicalSubject (removed from model)

### iching (Python, PyPI)
- `pip install iching` — v3.8.2
- WARNING: `from iching import iching; oracle = iching()` raises TypeError — module is NOT callable
- The package exists but the API surface is broken/undocumented
- Workaround: `scripts/iching_reading.py` implements coin-casting independently with all 64 hexagram names

### PanchangaAPI (Vedic Astrology MCP Server)
- GitHub: degen0root/panchanga_api
- 24 MCP tools, Swiss Ephemeris, Lahiri ayanamsha
- v4.1: KP System, 300+ Yogas, Panchanga Search, Vrata Calendar
- Could be integrated as an MCP server for Vedic astrology readings

### Celestine (TypeScript/NPM)
- `npm install celestine`
- Birth charts, transits, progressions
- Validated against NASA, JPL Horizons, Swiss Ephemeris
- Powers Cosmolytic.com (live planetary positions, moon phases)

### i-ching (Node.js, NPM)
- `npm install i-ching` — v0.3.5
- Working hexagram casting with `iChing.ask('question')`
- Returns hexagram number, character, names, changing lines

### The Numerology API (RapidAPI)
- 203+ endpoints across numerology, cycles, identity, horoscope, tarot
- Available on RapidAPI (freemium)
- Docs: https://docs.numerologyapi.com/

## DEAD / NOT WORKING

### Aztro API (aztro.sameer.space)
- Returns empty response on both POST and GET. Appears defunct.
- Was the go-to free horoscope API — now dead.

### Heroku-hosted APIs
- `rws-cards-api.herokuapp.com` — "No such app" (Heroku free tier killed)
- `horoscope-api.herokuapp.com` — 404
- `tarot-hq.herokuapp.com` — Dead
- LESSON: Never rely on Heroku free tier for production skill references.

### tarotapi.dev
- Returns empty. Not operational.

### Astrologico API (api.astrologico.org)
- Returns empty. Not operational.

## NOT TESTED BUT PROMISING

### sweph-wasm (NPM)
- Swiss Ephemeris compiled to WASM for browser/Node
- Could enable client-side astro calculations without Python

### Kerykeion SVG Chart Generation
- Kerykeion can generate SVG natal chart diagrams
- Not yet integrated into the skill but available if visual output is needed
