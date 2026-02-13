This project aims to be a tool for prospecting using google maps api, the idea is to search for a given keyword on google maps on a selected area, or location using some sort of hexagon location system to identify potential prospects


the search tearms could be type of business for example gyms or based on keyword for example gardening and extract all of the business that match that keyword not only by name but rather industry

We want to extract the following information
1. name of business
2. Phone number
3. website
4. rating
5. reviews 
6. location

then create a csv with this data

the csv must be pragmatical in a way that allows to keep track of business already checked using some sort of checkpoint system to not contaminate the data with duplicates, and to if rerun continue where the last extraction occurred

As the project progresses this is a notebook for anotating state of the project structrure, and overall changes and proggeses, use as log and notebook 

---

## Implementation Log

### 2025-02-12 - Initial Implementation

**Structure:**
- `prospector.py` - Main entry point and CLI. Orchestrates hex grid, Places API, and CSV export.
- `hexgrid.py` - H3 hexagon grid generator. Converts center lat/lng + resolution/ring into search points.
- `places_client.py` - Google Places API (REST) client. Text Search with location bias (circle), pagination.
- `checkpoint.py` - Checkpoint and CSV management. Tracks processed place_ids and hexagons for resumability.
- `requirements.txt` - h3, requests.

**Features:**
- Search by keyword (e.g. "gyms", "gardening services") - matches industry, not just name.
- Hexagon coverage via Uber H3: `get_hexagon_centers()` + `grid_disk()`.
- Extracted fields: name, phone, website, rating, review_count, address, coordinates, reviews_preview.
- CSV output with columns for all fields.
- Checkpoint system: JSON file stores processed_place_ids and processed_hexagons.
- Deduplication: place_id used to skip duplicates across hexagons.
- Resumability: on rerun, loads checkpoint + existing CSV, continues from last state.

**Usage:**
```
set GOOGLE_PLACES_API_KEY=your_key
python prospector.py "gyms" --lat 40.7128 --lng -74.0060 --output prospects.csv
```

**API Key:** Requires Google Cloud project with Places API (New) enabled. Set env var or `--api-key`.