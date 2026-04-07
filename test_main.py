import os
import pytest
import httpx
from httpx import AsyncClient, ASGITransport
from main import app, load_parks_data
from test_utils import create_image_with_gps
from PIL import Image
import io

@pytest.fixture(scope="module", autouse=True)
def setup_data():
    load_parks_data()

def create_bird_image(filename="bird.jpg", lat=None, lon=None):
    # This won't actually look like a bird, but we can't easily generate one
    # So we'll just test that the pipeline runs. 
    # To TRULY test bird detection, we'd need a real bird image.
    # For now, we just ensure the endpoint doesn't crash.
    img = Image.new('RGB', (224, 224), color=(135, 206, 235)) # Sky blue
    
    if lat is not None and lon is not None:
        import piexif
        def decimal_to_dms(decimal):
            degrees = int(abs(decimal))
            minutes = int((abs(decimal) - degrees) * 60)
            seconds = int((abs(decimal) - degrees - minutes/60) * 3600 * 100)
            return ((degrees, 1), (minutes, 1), (seconds, 100))

        exif_dict = {"GPS": {
            piexif.GPSIFD.GPSLatitudeRef: 'N' if lat >= 0 else 'S',
            piexif.GPSIFD.GPSLatitude: decimal_to_dms(lat),
            piexif.GPSIFD.GPSLongitudeRef: 'E' if lon >= 0 else 'W',
            piexif.GPSIFD.GPSLongitude: decimal_to_dms(lon),
        }}
        exif_bytes = piexif.dump(exif_dict)
        img.save(filename, exif=exif_bytes)
    else:
        img.save(filename)
    return filename

@pytest.mark.asyncio
async def test_check_photo_yosemite():
    img_path = create_bird_image("yosemite_bird.jpg", 37.8651, -119.5383)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with open(img_path, "rb") as f:
            files = {"file": (img_path, f, "image/jpeg")}
            response = await ac.post("/check-photo", files=files)
    
    if os.path.exists(img_path):
        os.remove(img_path)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # Location check
    assert data["location"]["is_in_park"] is True
    assert "Yosemite" in data["location"]["park_name"]
    # Bird check (might be false because it's a blue square, but it shouldn't error)
    assert "is_bird" in data

@pytest.mark.asyncio
async def test_check_photo_nyc():
    img_path = create_bird_image("nyc_test.jpg", 40.7128, -74.0060)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with open(img_path, "rb") as f:
            files = {"file": (img_path, f, "image/jpeg")}
            response = await ac.post("/check-photo", files=files)
    
    if os.path.exists(img_path):
        os.remove(img_path)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["location"]["is_in_park"] is False

@pytest.mark.asyncio
async def test_check_photo_no_gps():
    img_path = create_bird_image("no_gps.jpg")
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with open(img_path, "rb") as f:
            files = {"file": (img_path, f, "image/jpeg")}
            response = await ac.post("/check-photo", files=files)
    
    if os.path.exists(img_path):
        os.remove(img_path)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["location"]["error"] == "No GPS metadata found in image."
