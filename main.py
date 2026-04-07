import io
import os
import requests
import geopandas as gpd
from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from shapely.geometry import Point

app = FastAPI(title="National Park Photo Checker")

# --- Constants & Data Loading ---
# --- Constants & Data Loading ---
PARKS_PATH = "nps_boundary.geojson"
parks_gdf = None

def load_parks_data():
    global parks_gdf
    try:
        if os.path.exists(PARKS_PATH):
            parks_gdf = gpd.read_file(PARKS_PATH)
        else:
            parks_gdf = gpd.GeoDataFrame(columns=['geometry', 'UNIT_NAME'])
    except Exception as e:
        parks_gdf = gpd.GeoDataFrame(columns=['geometry', 'UNIT_NAME'])


# Load data on startup
load_parks_data()

# --- Helper Functions ---

def get_decimal_from_dms(dms, ref):
    """Convert degrees/minutes/seconds to decimal degrees."""
    degrees = dms[0]
    minutes = dms[1]
    seconds = dms[2]
    
    # Handle both tuple and Fraction/float formats
    if isinstance(degrees, tuple): degrees = degrees[0] / degrees[1]
    if isinstance(minutes, tuple): minutes = minutes[0] / minutes[1]
    if isinstance(seconds, tuple): seconds = seconds[0] / seconds[1]
    
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def get_exif_data(image):
    """Extract EXIF data from PIL Image."""
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_tag = GPSTAGS.get(t, t)
                    gps_data[sub_tag] = value[t]
                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value
    return exif_data

def get_coordinates(exif_data):
    """Extract coordinates from EXIF GPSInfo."""
    if "GPSInfo" not in exif_data:
        return None
    
    gps_info = exif_data["GPSInfo"]
    
    try:
        lat_dms = gps_info.get("GPSLatitude")
        lat_ref = gps_info.get("GPSLatitudeRef")
        lon_dms = gps_info.get("GPSLongitude")
        lon_ref = gps_info.get("GPSLongitudeRef")
        
        if not all([lat_dms, lat_ref, lon_dms, lon_ref]):
            return None
            
        lat = get_decimal_from_dms(lat_dms, lat_ref)
        lon = get_decimal_from_dms(lon_dms, lon_ref)
        return lat, lon
    except Exception as e:
        print(f"Error parsing GPS data: {e}")
        return None

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"status": "ok", "message": "National Park Photo Checker is active."}

@app.post("/check-park")
async def check_park(file: UploadFile = File(...)):
    # Read image
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid image file.")

    # Extract coordinates
    exif_data = get_exif_data(image)
    coords = get_coordinates(exif_data)
    
    if not coords:
        return {
            "success": False,
            "error": "No GPS metadata found in image."
        }
    
    lat, lon = coords
    
    # Check against National Parks
    if parks_gdf is None or parks_gdf.empty:
        return {
            "success": False,
            "error": "National Park data is not available."
        }
    
    point = Point(lon, lat)  # GeoJSON is [lon, lat]
    matches = parks_gdf[parks_gdf.geometry.contains(point)]
    
    if not matches.empty:
        name_col = 'UNIT_NAME' if 'UNIT_NAME' in matches.columns else 'NAME'
        park_name = matches.iloc[0].get(name_col, 'Unknown National Park')
        return {
            "success": True,
            "is_in_park": True,
            "park_name": park_name,
            "coordinates": {"lat": lat, "lon": lon}
        }
    
    return {
        "success": True,
        "is_in_park": False,
        "park_name": None,
        "coordinates": {"lat": lat, "lon": lon}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
