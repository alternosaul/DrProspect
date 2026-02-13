"""
DrProspect - Map prospecting tool.
Searches Google Maps for businesses by keyword within a hexagon grid area.
Exports name, phone, website, rating, reviews, location to CSV with checkpoint.
"""

import argparse
import os
from pathlib import Path

# Load API key from .env if present
from dotenv import load_dotenv
load_dotenv()

from hexgrid import get_hexagon_centers, get_hexagon_radius_meters
from places_client import fetch_all_places_for_location
from checkpoint import (
    load_checkpoint,
    save_checkpoint,
    load_existing_place_ids_from_csv,
    append_places_to_csv,
)


def run_prospector(
    api_key: str,
    search_term: str,
    center_lat: float,
    center_lng: float,
    output_csv: Path,
    checkpoint_path: Path | None = None,
    resolution: int = 9,
    ring_size: int = 2,
    radius_meters: float | None = None,
) -> dict:
    """
    Main prospecting run: search hexagon grid, dedupe, append to CSV.
    
    Returns summary dict with counts: hexagons_searched, places_found, places_added.
    """
    # Default checkpoint next to output CSV
    if checkpoint_path is None:
        checkpoint_path = output_csv.with_suffix(".checkpoint.json")
    
    # Load checkpoint and existing CSV to know what we've already processed
    checkpoint = load_checkpoint(checkpoint_path)
    processed_place_ids = checkpoint["processed_place_ids"].copy()
    processed_hexagons = checkpoint["processed_hexagons"].copy()
    
    # Also consider places already in CSV (for resumability)
    processed_place_ids.update(load_existing_place_ids_from_csv(output_csv))
    
    # Get hexagon centers for the search area
    centers = get_hexagon_centers(center_lat, center_lng, resolution, ring_size)
    
    # Search radius: use provided value or derive from H3 resolution
    if radius_meters is None:
        radius_meters = get_hexagon_radius_meters(resolution)
    
    total_new_places = 0
    new_places_buffer = []
    total_added = 0
    
    for i, (lat, lng) in enumerate(centers):
        # Create a simple hexagon id for checkpoint (use lat,lng rounded)
        hex_id = f"{lat:.4f},{lng:.4f}"
        
        # Fetch places for this hexagon center
        places = fetch_all_places_for_location(
            api_key=api_key,
            text_query=search_term,
            lat=lat,
            lng=lng,
            radius_meters=radius_meters,
        )
        
        for place in places:
            pid = place.get("place_id", "")
            if pid and pid not in processed_place_ids:
                processed_place_ids.add(pid)
                new_places_buffer.append(place)
                total_new_places += 1
        
        # Mark hexagon as processed
        processed_hexagons.add(hex_id)
        
        # Write buffer to CSV periodically (every 10 places) to avoid data loss
        if len(new_places_buffer) >= 10:
            added = append_places_to_csv(output_csv, new_places_buffer)
            total_added += added
            new_places_buffer.clear()
            save_checkpoint(checkpoint_path, processed_place_ids, processed_hexagons)
    
    # Write remaining places
    added = append_places_to_csv(output_csv, new_places_buffer)
    total_added += added
    
    # Final checkpoint save
    save_checkpoint(checkpoint_path, processed_place_ids, processed_hexagons)
    
    return {
        "hexagons_searched": len(centers),
        "places_found": total_new_places,
        "places_added": total_added,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="DrProspect - Search Google Maps for businesses and export to CSV"
    )
    parser.add_argument(
        "search_term",
        type=str,
        help="Search keyword (e.g. 'gyms', 'gardening services', 'dentists')",
    )
    parser.add_argument(
        "--lat",
        type=float,
        required=True,
        help="Center latitude (e.g. 40.7128)",
    )
    parser.add_argument(
        "--lng",
        type=float,
        required=True,
        help="Center longitude (e.g. -74.0060)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("prospects.csv"),
        help="Output CSV path (default: prospects.csv)",
    )
    parser.add_argument(
        "--resolution",
        type=int,
        default=9,
        choices=range(7, 12),
        metavar="7-11",
        help="H3 resolution (higher=smaller cells, more API calls). Default 9",
    )
    parser.add_argument(
        "--ring-size",
        type=int,
        default=2,
        help="Number of hexagon rings around center. Default 2",
    )
    parser.add_argument(
        "--radius",
        type=float,
        default=None,
        help="Search radius in meters per hexagon (default: derived from resolution)",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.environ.get("GOOGLE_PLACES_API_KEY"),
        help="Google Places API key (or set GOOGLE_PLACES_API_KEY env var)",
    )
    
    args = parser.parse_args()
    
    if not args.api_key:
        print("Error: Google Places API key required.")
        print("Set GOOGLE_PLACES_API_KEY env var or use --api-key")
        return
    
    print(f"Searching for '{args.search_term}' near ({args.lat}, {args.lng})")
    print(f"Output: {args.output}")
    
    summary = run_prospector(
        api_key=args.api_key,
        search_term=args.search_term,
        center_lat=args.lat,
        center_lng=args.lng,
        output_csv=args.output,
        resolution=args.resolution,
        ring_size=args.ring_size,
        radius_meters=args.radius,
    )
    
    print(f"Hexagons searched: {summary['hexagons_searched']}")
    print(f"Places found: {summary['places_found']}")
    print(f"New places added to CSV: {summary['places_added']}")


if __name__ == "__main__":
    main()
