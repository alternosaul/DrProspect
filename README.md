# DrProspect

Map prospecting tool using Google Maps Places API. Searches for businesses by keyword within a hexagon grid area and exports data to CSV with checkpoint/resume support.

## Features

- **Keyword search** – Find businesses by type (e.g. "gyms") or industry (e.g. "gardening services")
- **Hexagon grid** – Uses Uber H3 to partition the search area for thorough coverage
- **Extracted data** – Name, phone, website, rating, review count, address, coordinates, reviews preview
- **Checkpoint system** – Prevents duplicates and allows resuming interrupted runs

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Get a Google Places API key:
   - Create a [Google Cloud project](https://console.cloud.google.com/)
   - Enable the **Places API (New)**
   - Create an API key and restrict it to Places API

3. Set your API key:
   ```
   set GOOGLE_PLACES_API_KEY=your_api_key
   ```
   (On macOS/Linux: `export GOOGLE_PLACES_API_KEY=your_api_key`)

## Usage

```bash
python prospector.py "gyms" --lat 40.7128 --lng -74.0060 -o prospects.csv
```

**Options:**
- `--lat`, `--lng` – Center point of the search area (required)
- `-o`, `--output` – Output CSV path (default: prospects.csv)
- `--resolution` – H3 resolution 7–11 (default: 9). Higher = smaller cells, more API calls
- `--ring-size` – Number of hexagon rings around center (default: 2)
- `--radius` – Search radius in meters per hexagon (optional, derived from resolution by default)
- `--api-key` – API key (or use GOOGLE_PLACES_API_KEY env var)

**Examples:**
```bash
# Gyms in Manhattan
python prospector.py "gyms" --lat 40.7831 --lng -73.9712 -o gyms.csv

# Gardening businesses in London
python prospector.py "gardening" --lat 51.5074 --lng -0.1278 -o gardening.csv
```

## Output

- **CSV** – `prospects.csv` (or your chosen path) with all extracted fields
- **Checkpoint** – `prospects.checkpoint.json` stores processed place IDs and hexagons

Re-running with the same output path continues from the last run and avoids duplicates.

---

## Author

Built by **Saúl Hinojosa** — portfolio: [saulhinojosa.site](https://saulhinojosa.site)

How it was built: [saulhinojosa.site/blog/drprospect/](https://saulhinojosa.site/blog/drprospect/)
