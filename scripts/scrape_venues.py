import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import date

VENUES = [
    {
        "name": "Coon Rapids VFW",
        "url": "https://www.facebook.com/CoonRapidsVFW",
        "band": "Tailspin",
        "bandUrl": "https://www.facebook.com/TailspinBandMN",
        "time": "7:00 PM – 11:00 PM"
    },
    {
        "name": "Crystal VFW",
        "url": "https://www.facebook.com/CrystalVFW",
        "band": "Vinyl Revival",
        "bandUrl": "https://www.facebook.com/VinylRevivalMN",
        "time": "7:00 PM – 11:00 PM"
    }
]

def extract_phone(html):
    # Generic US phone pattern
    match = re.search(r'\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}', html)
    return match.group(0) if match else "Phone not found"

events = []

for v in VENUES:
    try:
        r = requests.get(v["url"], timeout=15, headers={
            "User-Agent": "Mozilla/5.0"
        })
        phone = extract_phone(r.text)
    except Exception:
        phone = "Unavailable"

    events.append({
        "venue": v["name"],
        "venueUrl": v["url"],
        "phone": phone,
        "band": v["band"],
        "bandUrl": v["bandUrl"],
        "time": v["time"]
    })

data = {
    "lastUpdated": str(date.today()),
    "events": events
}

with open("data/friday.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Updated data/friday.json")
