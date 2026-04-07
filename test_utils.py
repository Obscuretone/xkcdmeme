import io
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import piexif

def create_image_with_gps(lat, lon, filename="test_image.jpg"):
    # Create a small white image
    img = Image.new('RGB', (100, 100), color=(255, 255, 255))
    
    # Function to convert decimal to DMS for piexif
    def decimal_to_dms(decimal):
        degrees = int(abs(decimal))
        minutes = int((abs(decimal) - degrees) * 60)
        seconds = int((abs(decimal) - degrees - minutes/60) * 3600 * 100)
        return ((degrees, 1), (minutes, 1), (seconds, 100))

    lat_dms = decimal_to_dms(lat)
    lon_dms = decimal_to_dms(lon)
    lat_ref = 'N' if lat >= 0 else 'S'
    lon_ref = 'E' if lon >= 0 else 'W'

    gps_ifd = {
        piexif.GPSIFD.GPSLatitudeRef: lat_ref,
        piexif.GPSIFD.GPSLatitude: lat_dms,
        piexif.GPSIFD.GPSLongitudeRef: lon_ref,
        piexif.GPSIFD.GPSLongitude: lon_dms,
    }

    exif_dict = {"GPS": gps_ifd}
    exif_bytes = piexif.dump(exif_dict)
    
    img.save(filename, exif=exif_bytes)
    print(f"Created {filename} with coordinates: {lat}, {lon}")

if __name__ == "__main__":
    # Yosemite Coordinates
    create_image_with_gps(37.8651, -119.5383, "yosemite.jpg")
    # Random NYC Coordinates (Not in a National Park)
    create_image_with_gps(40.7128, -74.0060, "nyc.jpg")
