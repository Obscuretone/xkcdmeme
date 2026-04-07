import os
import pytest
import httpx
from httpx import AsyncClient, ASGITransport
from main import app, load_parks_data
from test_utils import create_image_with_gps

@pytest.mark.asyncio
async def test_check_park_yosemite():
    # Ensure data is loaded
    load_parks_data()
    
    # Create a test image in Yosemite
    img_path = "yosemite_test.jpg"
    create_image_with_gps(37.8651, -119.5383, img_path)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with open(img_path, "rb") as f:
            files = {"file": (img_path, f, "image/jpeg")}
            response = await ac.post("/check-park", files=files)
    
    if os.path.exists(img_path):
        os.remove(img_path)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["is_in_park"] is True
    assert "Yosemite" in data["park_name"]

@pytest.mark.asyncio
async def test_check_park_nyc():
    # Ensure data is loaded
    load_parks_data()
    
    # Create a test image in NYC (Not a National Park)
    img_path = "nyc_test.jpg"
    create_image_with_gps(40.7128, -74.0060, img_path)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with open(img_path, "rb") as f:
            files = {"file": (img_path, f, "image/jpeg")}
            response = await ac.post("/check-park", files=files)
    
    if os.path.exists(img_path):
        os.remove(img_path)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["is_in_park"] is False

@pytest.mark.asyncio
async def test_check_park_no_gps():
    # Create a test image without GPS
    from PIL import Image
    img_path = "no_gps.jpg"
    img = Image.new('RGB', (100, 100), color=(255, 255, 255))
    img.save(img_path)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with open(img_path, "rb") as f:
            files = {"file": (img_path, f, "image/jpeg")}
            response = await ac.post("/check-park", files=files)
    
    if os.path.exists(img_path):
        os.remove(img_path)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "No GPS metadata" in data["error"]
