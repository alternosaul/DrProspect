"""
Prueba de conexión con Google Places API.
Ejecuta una búsqueda mínima para verificar que la API key funciona.
"""

import os
import sys
import requests

# Cargar .env si existe
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# URL de Text Search (Places API New)
URL = "https://places.googleapis.com/v1/places:searchText"

# Field mask mínimo para reducir costo (solo id y nombre)
FIELD_MASK = "places.id,places.displayName"


def test_connection() -> bool:
    """Ejecuta una búsqueda de prueba y devuelve True si la conexión es exitosa."""
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
    if not api_key:
        print("ERROR: No se encontró GOOGLE_PLACES_API_KEY")
        print("Configura el archivo .env o la variable de entorno")
        return False

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": FIELD_MASK,
    }
    body = {
        "textQuery": "café",
        "locationBias": {
            "circle": {
                "center": {"latitude": 40.7128, "longitude": -74.0060},
                "radius": 500.0,
            }
        },
    }

    try:
        response = requests.post(URL, json=body, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        places = data.get("places", [])
        print("[OK] Conexion exitosa con Google Places API")
        print(f"  Resultados de prueba: {len(places)} lugares encontrados")
        if places:
            nombre = places[0].get("displayName", {}).get("text", "N/A")
            print(f"  Ejemplo: {nombre}")
        return True
    except requests.exceptions.HTTPError as e:
        print(f"ERROR HTTP: {e.response.status_code}")
        if e.response.text:
            print(f"  Detalle: {e.response.text[:300]}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"ERROR de conexión: {e}")
        return False


if __name__ == "__main__":
    ok = test_connection()
    sys.exit(0 if ok else 1)
