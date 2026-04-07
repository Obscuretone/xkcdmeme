![xkcd: Tasks](https://imgs.xkcd.com/comics/tasks.png)

# National Park Bird Verification Service

A high-performance FastAPI service designed to solve the classic challenge of simultaneous geographical verification and biological classification in photography. This service processes image uploads to determine if a photo was taken within the boundaries of a U.S. National Park and identifies whether the subject of the photo is a bird.

## Features

- **Automated Geofencing**: Utilizes `GeoPandas` and `Shapely` to perform high-precision spatial queries against official National Park Service (NPS) administrative boundaries.
- **EXIF Metadata Extraction**: Automatically extracts and parses GPS metadata (Degrees, Minutes, Seconds) from image files into decimal coordinates.
- **Computer Vision Classification**: Leverages a pre-trained Vision Transformer (ViT) via Hugging Face `transformers` to identify avian subjects with high confidence.
- **Unified API**: Provides a single, robust REST endpoint for comprehensive photo analysis.

## Tech Stack

- **Framework**: FastAPI
- **Geospatial**: GeoPandas, Shapely, Pyogrio
- **ML/CV**: PyTorch, Transformers (ViT)
- **Image Processing**: Pillow (PIL), Piexif
- **Data Source**: [NPS Administrative Boundaries](http://gstore.unm.edu/apps/rgisarchive/datasets/7bbe8af5-029b-4adf-b06c-134f0dd57226/nps_boundary.derived.geojson) (Derived version via UNM RGIS)

## Installation

### Prerequisites
- Python 3.9+
- [Git LFS](https://git-lfs.github.com/) (recommended for handling large GeoJSON datasets)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/Obscuretone/xkcdmeme.git
   cd xkcdmeme
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure `nps_boundary.geojson` is present in the root directory.

## Usage

### Starting the Service
Run the server using Uvicorn:
```bash
python3 main.py
```
The service will be available at `http://localhost:8000`.

### API Documentation
Once the service is running, interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs"
- Redoc: `http://localhost:8000/redoc"

### Example Request
```bash
curl -X POST "http://localhost:8000/check-photo" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@path/to/your/photo.jpg"
```

### Example Response
```json
{
  "success": true,
  "is_bird": true,
  "bird_confidence": 0.9842,
  "location": {
    "is_in_park": true,
    "park_name": "Yosemite National Park",
    "coordinates": {
      "lat": 37.8651,
      "lon": -119.5383
    },
    "error": null
  }
}
```

## Testing
The project includes a comprehensive test suite that simulates both geographical and classification scenarios:
```bash
python3 -m pytest test_main.py
```

## Background
This project was vibe coded in approximately 30 minutes, providing a modern implementation of a historically "complex" software engineering problem. It proves that what was once a five-year research task is now achievable with robust open-source tools and pre-trained models.

## License
MIT
