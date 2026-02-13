"""
Google Places API client for searching businesses.
Uses REST API with API key authentication.
"""

import os
import time
import requests

# Base URL for Places API (New)
PLACES_TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

# Field mask for Text Search - request all fields we need for prospecting
# Essentials + Pro + Enterprise for phone, website, rating, reviews
FIELD_MASK = (
    "places.id,places.displayName,places.formattedAddress,"
    "places.location,places.rating,places.userRatingCount,"
    "places.internationalPhoneNumber,places.nationalPhoneNumber,"
    "places.websiteUri,places.reviews"
)


def search_places_near_location(
    api_key: str,
    text_query: str,
    lat: float,
    lng: float,
    radius_meters: float = 500.0,
    page_token: str | None = None,
    language_code: str = "en",
) -> dict:
    """
    Search for places matching text query near a lat/lng point.
    
    Args:
        api_key: Google Places API key
        text_query: Search term (e.g. "gyms", "gardening services")
        lat: Center latitude
        lng: Center longitude
        radius_meters: Search radius in meters (max 50000)
        page_token: For pagination, pass nextPageToken from previous response
        language_code: Results language
    
    Returns:
        API response dict with 'places' list and optional 'nextPageToken'
    """
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": FIELD_MASK,
    }
    
    body = {
        "textQuery": text_query,
        "languageCode": language_code,
        "locationBias": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": min(radius_meters, 50000.0),
            }
        },
    }
    
    if page_token:
        body["pageToken"] = page_token
    
    # Rate limit: avoid hitting API too fast
    time.sleep(0.1)
    
    response = requests.post(PLACES_TEXT_SEARCH_URL, json=body, headers=headers)
    response.raise_for_status()
    return response.json()


def extract_place_data(place: dict) -> dict | None:
    """
    Extract prospecting fields from a Places API place object.
    Returns None if place has no valid id (skip).
    """
    # Place id is in format "places/ChIJ..." - we use the full name for dedup
    place_id = place.get("id") or place.get("name")
    if not place_id:
        return None
    
    # Get display name text
    display_name = place.get("displayName", {})
    name = display_name.get("text", "") if isinstance(display_name, dict) else str(display_name)
    
    # Phone: prefer international, fallback to national
    phone = place.get("internationalPhoneNumber") or place.get("nationalPhoneNumber") or ""
    
    # Website
    website = place.get("websiteUri") or ""
    
    # Rating and review count
    rating = place.get("rating")
    rating_str = str(rating) if rating is not None else ""
    review_count = place.get("userRatingCount", 0)
    
    # Location as address
    address = place.get("formattedAddress") or ""
    
    # Lat/lng if available
    location = place.get("location", {})
    lat = location.get("latitude", "")
    lng = location.get("longitude", "")
    coords = f"{lat},{lng}" if lat != "" and lng != "" else ""
    
    # Reviews: get text from first few reviews if available
    # Structure: Review has "text" (LocalizedText) with "text" property
    reviews_raw = place.get("reviews", [])
    reviews_text = []
    for r in reviews_raw[:3]:  # Up to 3 reviews
        if not isinstance(r, dict):
            continue
        text_obj = r.get("text") or r.get("originalText")
        if isinstance(text_obj, dict):
            reviews_text.append(text_obj.get("text", ""))
        elif isinstance(text_obj, str):
            reviews_text.append(text_obj)
    reviews_str = " | ".join(reviews_text) if reviews_text else ""
    
    return {
        "place_id": place_id,
        "name": name,
        "phone": phone,
        "website": website,
        "rating": rating_str,
        "review_count": review_count,
        "address": address,
        "coordinates": coords,
        "reviews_preview": reviews_str,
    }


def fetch_all_places_for_location(
    api_key: str,
    text_query: str,
    lat: float,
    lng: float,
    radius_meters: float = 500.0,
    max_pages: int = 3,
) -> list[dict]:
    """
    Fetch all places for a location, following pagination.
    Text Search returns max 60 results total across pages.
    """
    results = []
    page_token = None
    pages = 0
    
    while pages < max_pages:
        resp = search_places_near_location(
            api_key=api_key,
            text_query=text_query,
            lat=lat,
            lng=lng,
            radius_meters=radius_meters,
            page_token=page_token,
        )
        
        places = resp.get("places", [])
        for place in places:
            extracted = extract_place_data(place)
            if extracted:
                results.append(extracted)
        
        page_token = resp.get("nextPageToken")
        pages += 1
        if not page_token:
            break
    
    return results
