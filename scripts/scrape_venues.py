import os
import json
import requests
import time
from datetime import date

# -----------------------------
# CONFIG
# -----------------------------

API_KEY = os.environ["GOOGLE_MAPS_API_KEY"]
OUTPUT_FILE = "data/friday.json"

SEARCH_QUERIES = [
    "VFW live music Minnesota",
    "American Legion live music Minnesota",
    "VFW Friday night band Minnesota",
    "American Legion Friday live music",
    "live music VFW Twin Cities",
    "live music American Legion Twin Cities"
]

# -----------------------------
# HELPERS
# -----------------------------

def is_target_venue(name: str) -> bool:
    """
    Only allow VFW and American Legion venues
    """
    if not name:
        return False

    name = name.lower()
    return (
        "vfw" in name
        or "american legion" in name
        or "legion post" in name
    )


def search_places_all_pages(query: str):
    """
    Google Places Text Search with pagination
    """
    all_results = []
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    params = {
        "query": query,
        "key": API_KEY
    }

    while True:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()

        results = data.get("results", [])
        all_results.extend(results)

        next_token = data.get("next_page_token")
        if not next_token:
            break

        # Google requires delay before using next_page_token
        time.sleep(2)
        params["pagetoken"] = next_token

    return all_results


def get_place_details(place_id: str):
    """
    Fetch detailed info for a place
    """
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,formatted_phone_number,website,formatted_address",
        "key": API_KEY
    }

    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json().get("result", {})


# -----------------------------
# MAIN
# -----------------------------

def main():
    seen_place_ids = set()
    events = []

    for query in SEARCH_QUERIES:
        print(f"Searching: {query}")
        places = search_places_all_pages(query)

        for place in places:
            place_id = place.get("place_id")
            if not place_id or place_id in seen_place_ids:
                continue

            seen_place_ids.add(place_id)

            details = get_place_details(place_id)
            venue_name = details.get("name", "")

            # 🔴 FILTER HERE
            if not is_target_venue(venue_name):
                continue

            events.append({
                "venue": venue_name,
                "venueUrl": details.get("website", ""),
                "phone": details.get("formatted_phone_number", "Phone not listed"),
                "address": details.get("formatted_address", ""),
                "band": "TBD",
                "bandUrl": "",
                "time": "Check venue"
            })

    output = {
        "lastUpdated": str(date.today()),
        "events": sorted(events, key=lambda x: x["venue"])
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Discovered {len(events)} venues")


if __name__ == "__main__":
    main()
