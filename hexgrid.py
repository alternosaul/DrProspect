"""
Hexagon grid generator using Uber's H3 library.
Covers a geographic area with hexagonal cells for systematic place search.
"""

import h3


def get_hexagon_centers(
    center_lat: float,
    center_lng: float,
    resolution: int = 9,
    ring_size: int = 2,
) -> list[tuple[float, float]]:
    """
    Generate lat/lng coordinates for hexagon cell centers in a disk around a point.
    
    Args:
        center_lat: Latitude of the center point
        center_lng: Longitude of the center point
        resolution: H3 resolution (0-15). Higher = smaller cells. 9 ≈ city block
        ring_size: Number of rings around center (k in grid_disk). 0 = single cell.
    
    Returns:
        List of (latitude, longitude) tuples for each hexagon center
    """
    # Convert center point to H3 cell
    center_cell = h3.latlng_to_cell(center_lat, center_lng, resolution)
    
    # Get all cells within ring_size rings (filled disk)
    cells = h3.grid_disk(center_cell, ring_size)
    
    # Convert each cell to its center coordinates
    centers = []
    for cell in cells:
        lat, lng = h3.cell_to_latlng(cell)
        centers.append((lat, lng))
    
    return centers


def get_hexagon_radius_meters(resolution: int) -> float:
    """
    Approximate edge length of H3 hexagon at given resolution, in meters.
    Used to set search radius for Places API circle bias.
    
    Resolution guide (approx): 8≈0.7km, 9≈0.25km, 10≈0.1km
    """
    # Get a sample cell and compute approximate edge length
    sample = h3.latlng_to_cell(0, 0, resolution)
    boundary = h3.cell_to_boundary(sample)
    # Rough approximation: avg edge ~ 0.5 * hexagon circumradius
    # H3 resolutions: r9 ≈ 174m edge, r8 ≈ 461m
    edge_lengths = {
        7: 1222,
        8: 461,
        9: 174,
        10: 66,
        11: 25,
    }
    return edge_lengths.get(resolution, 174) * 2  # Use as radius in meters
