#!/usr/bin/env python3
"""Natal chart calculator using Kerykeion (Swiss Ephemeris)."""
import sys
import json
import warnings
import os
warnings.filterwarnings("ignore")
os.environ.setdefault("KERYKEION_GEONAMES_USERNAME", "hermes_zoltar")

# Common city coordinates fallback (when GeoNames is unavailable)
CITY_COORDS = {
    "sao paulo": {"lat": -23.5505, "lng": -46.6333, "tz": "America/Sao_Paulo", "nation": "BR"},
    "rio de janeiro": {"lat": -22.9068, "lng": -43.1729, "tz": "America/Sao_Paulo", "nation": "BR"},
    "new york": {"lat": 40.7128, "lng": -74.0060, "tz": "America/New_York", "nation": "US"},
    "los angeles": {"lat": 34.0522, "lng": -118.2437, "tz": "America/Los_Angeles", "nation": "US"},
    "london": {"lat": 51.5074, "lng": -0.1278, "tz": "Europe/London", "nation": "GB"},
    "paris": {"lat": 48.8566, "lng": 2.3522, "tz": "Europe/Paris", "nation": "FR"},
    "tokyo": {"lat": 35.6762, "lng": 139.6503, "tz": "Asia/Tokyo", "nation": "JP"},
    "berlin": {"lat": 52.5200, "lng": 13.4050, "tz": "Europe/Berlin", "nation": "DE"},
    "madrid": {"lat": 40.4168, "lng": -3.7038, "tz": "Europe/Madrid", "nation": "ES"},
    "mexico city": {"lat": 19.4326, "lng": -99.1332, "tz": "America/Mexico_City", "nation": "MX"},
    "buenos aires": {"lat": -34.6037, "lng": -58.3816, "tz": "America/Argentina/Buenos_Aires", "nation": "AR"},
    "sydney": {"lat": -33.8688, "lng": 151.2093, "tz": "Australia/Sydney", "nation": "AU"},
    "mumbai": {"lat": 19.0760, "lng": 72.8777, "tz": "Asia/Kolkata", "nation": "IN"},
    "bangkok": {"lat": 13.7563, "lng": 100.5018, "tz": "Asia/Bangkok", "nation": "TH"},
}

def main():
    if len(sys.argv) < 8:
        print('Usage: natal_chart.py "Name" YYYY MM DD HH MM "City" "Nation"')
        print('Example: natal_chart.py "Alex" 1990 6 15 10 30 "Sao Paulo" "BR"')
        print("")
        print("Alternatively, pass coordinates directly:")
        print('natal_chart.py "Name" YYYY MM DD HH MM LAT LNG "Timezone"')
        print('Example: natal_chart.py "Alex" 1990 6 15 10 30 -23.55 -46.63 "America/Sao_Paulo"')
        sys.exit(1)
    
    name = sys.argv[1]
    year = int(sys.argv[2])
    month = int(sys.argv[3])
    day = int(sys.argv[4])
    hour = int(sys.argv[5])
    minute = int(sys.argv[6])
    
    from kerykeion import AstrologicalSubject
    
    subject = None
    
    # Try coordinate mode first (8th arg is a number)
    try:
        lat = float(sys.argv[7])
        lng = float(sys.argv[8])
        tz_str = sys.argv[9] if len(sys.argv) > 9 else "UTC"
        subject = AstrologicalSubject(
            name, year, month, day, hour, minute,
            city="Custom", nation="XX",
            lat=lat, lng=lng, tz_str=tz_str,
            geonames_username="hermes_zoltar"
        )
    except (ValueError, IndexError):
        pass
    
    # Try city name mode
    if subject is None:
        city = sys.argv[7]
        nation = sys.argv[8] if len(sys.argv) > 8 else "US"
        city_key = city.lower().strip()
        
        # Try GeoNames first
        try:
            subject = AstrologicalSubject(
                name, year, month, day, hour, minute, city=city, nation=nation,
                geonames_username="hermes_zoltar"
            )
        except Exception:
            # Fallback to known coordinates
            if city_key in CITY_COORDS:
                coords = CITY_COORDS[city_key]
                subject = AstrologicalSubject(
                    name, year, month, day, hour, minute,
                    city=city, nation=coords["nation"],
                    lat=coords["lat"], lng=coords["lng"],
                    tz_str=coords["tz"],
                    geonames_username="hermes_zoltar"
                )
            else:
                print(json.dumps({"error": f"Cannot resolve city '{city}'. Try coordinates: natal_chart.py \"Name\" YYYY MM DD HH MM LAT LNG \"Timezone\""}))
                sys.exit(1)
    
    raw = subject.json()
    data = json.loads(raw) if isinstance(raw, str) else raw
    
    # Extract key info
    output = {
        "name": data["name"],
        "birth_info": {
            "date": data["iso_formatted_local_datetime"],
            "city": data["city"],
            "nation": data["nation"],
            "coordinates": {"lat": data["lat"], "lng": data["lng"]},
            "zodiac_type": data["zodiac_type"],
            "houses_system": data["houses_system_name"],
        },
        "planets": {},
        "houses": {},
        "elements": {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0},
        "modalities": {"Cardinal": 0, "Fixed": 0, "Mutable": 0},
        "retrograde_planets": [],
    }
    
    planet_keys = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
    sign_names = {
        "Ari": "Aries", "Tau": "Taurus", "Gem": "Gemini", "Can": "Cancer",
        "Leo": "Leo", "Vir": "Virgo", "Lib": "Libra", "Sco": "Scorpio",
        "Sag": "Sagittarius", "Cap": "Capricorn", "Aqu": "Aquarius", "Pis": "Pisces"
    }
    
    for key in planet_keys:
        p = data.get(key, {})
        if not p:
            continue
        sign = p.get("sign", "?")
        output["planets"][key] = {
            "sign": sign_names.get(sign, sign),
            "degree": round(p.get("position", 0), 2),
            "house": p.get("house", "?"),
            "element": p.get("element", "?"),
            "quality": p.get("quality", "?"),
            "retrograde": p.get("retrograde", False),
        }
        output["elements"][p.get("element", "?")] += 1
        output["modalities"][p.get("quality", "?")] += 1
        if p.get("retrograde"):
            output["retrograde_planets"].append(key.capitalize())
    
    # Houses — Kerykeion v5 returns houses as list; each entry may be dict with sign/position
    # or just a number (the cusp degree). Handle both formats.
    raw_houses = data.get("houses", [])
    for i, h in enumerate(raw_houses[:12], 1):
        if isinstance(h, dict):
            sign = h.get("sign", "?")
            output["houses"][f"House_{i}"] = {
                "sign": sign_names.get(sign, sign),
                "degree": round(h.get("position", 0), 2),
            }
        elif isinstance(h, (int, float)):
            # Kerykeion sometimes returns just the cusp degree
            # Determine sign from degree range
            deg = h % 360
            signs_order = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
            sign_idx = int(deg // 30)
            output["houses"][f"House_{i}"] = {
                "sign": signs_order[sign_idx],
                "degree": round(h, 2),
            }
    # Also check house_X keys (Kerykeion v5 alternate format)
    for i in range(1, 13):
        key = f"house_{i}"
        if key in data and f"House_{i}" not in output["houses"]:
            h = data[key]
            if isinstance(h, dict):
                sign = h.get("sign", "?")
                output["houses"][f"House_{i}"] = {
                    "sign": sign_names.get(sign, sign),
                    "degree": round(h.get("position", 0), 2),
                }
            elif isinstance(h, (int, float)):
                deg = h % 360
                signs_order = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
                output["houses"][f"House_{i}"] = {
                    "sign": signs_order[int(deg // 30)],
                    "degree": round(h, 2),
                }
    
    # Aspects (if available in the model)
    if "aspects" in data:
        output["aspects"] = []
        for a in data["aspects"]:
            output["aspects"].append({
                "planet1": a.get("p1_name", "?"),
                "aspect": a.get("aspect", "?"),
                "planet2": a.get("p2_name", "?"),
                "orb": round(a.get("orbit", 0), 1),
            })
    
    # Ascendant from 1st house
    first_house = data.get("first_house", data.get("houses", [{}])[0] if data.get("houses") else {})
    if first_house:
        asc_sign = first_house.get("sign", "?")
        output["ascendant"] = {
            "sign": sign_names.get(asc_sign, asc_sign),
            "degree": round(first_house.get("position", 0), 2),
        }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
