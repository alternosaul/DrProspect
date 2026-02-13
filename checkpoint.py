"""
Checkpoint and CSV management for DrProspect.
Tracks processed places to avoid duplicates and allows resuming interrupted runs.
"""

import csv
import json
from pathlib import Path


# CSV column order for output
CSV_COLUMNS = [
    "place_id",
    "name",
    "phone",
    "website",
    "rating",
    "review_count",
    "address",
    "coordinates",
    "reviews_preview",
]


def load_checkpoint(checkpoint_path: Path) -> dict:
    """
    Load checkpoint file containing processed place_ids and optionally hexagon ids.
    Returns dict with 'processed_place_ids' (set) and 'processed_hexagons' (set).
    """
    data = {"processed_place_ids": set(), "processed_hexagons": set()}
    
    if not checkpoint_path.exists():
        return data
    
    try:
        with open(checkpoint_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        data["processed_place_ids"] = set(raw.get("processed_place_ids", []))
        data["processed_hexagons"] = set(raw.get("processed_hexagons", []))
    except (json.JSONDecodeError, IOError):
        pass  # Use empty checkpoint on error
    
    return data


def save_checkpoint(
    checkpoint_path: Path,
    processed_place_ids: set,
    processed_hexagons: set,
) -> None:
    """Persist checkpoint to JSON file."""
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    with open(checkpoint_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "processed_place_ids": list(processed_place_ids),
                "processed_hexagons": list(processed_hexagons),
            },
            f,
            indent=2,
        )


def load_existing_place_ids_from_csv(csv_path: Path) -> set:
    """
    Load place_ids from existing CSV output.
    Used for deduplication when resuming - we don't re-add places already in CSV.
    """
    ids = set()
    if not csv_path.exists():
        return ids
    
    try:
        with open(csv_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if "place_id" not in (reader.fieldnames or []):
                return ids
            for row in reader:
                pid = row.get("place_id", "").strip()
                if pid:
                    ids.add(pid)
    except (csv.Error, IOError):
        pass
    
    return ids


def ensure_csv_header(csv_path: Path) -> None:
    """Create CSV with headers if it doesn't exist."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()


def append_places_to_csv(csv_path: Path, places: list[dict]) -> int:
    """
    Append new places to CSV. Skips places already in CSV (by place_id).
    Returns count of actually written rows.
    """
    existing = load_existing_place_ids_from_csv(csv_path)
    ensure_csv_header(csv_path)
    
    written = 0
    with open(csv_path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        for place in places:
            pid = place.get("place_id", "")
            if not pid or pid in existing:
                continue
            existing.add(pid)
            writer.writerow({k: place.get(k, "") for k in CSV_COLUMNS})
            written += 1
    
    return written
