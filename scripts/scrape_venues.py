import json
import re
import requests
from datetime import date
from pathlib import Path

DATA_FILE = Path("data/friday.json")

def extract_phone(html):
    match = re.search(r'\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}', html)
    return match.group(0) if match else "Phone not found"

# Load existing data
with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

events = []

for event in data.get("events", []):
    phone = event.get("phone", "Phone not found")

    try:
        r = requests.get(
            event["venueUrl"],
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        phone = extract_phone(r.text)
    except Exception:
        pass  # keep existing phone if scrape fails

    event["phone"] = phone
    events.append(event)

# Write back updated data
output = {
    "lastUpdated": str(date.today()),
    "events": events
}

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(f"Updated {len(events)} venues")
