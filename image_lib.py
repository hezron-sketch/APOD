"""
Library of useful functions for working with images.
"""

import os
import sys
import requests

def main():
    test_url = "https://apod.nasa.gov/apod/image/2303/FlamingStarComet_Roell_7504.jpg"
    print("Downloading image from URL:")
    image_data = download_image(test_url)
    if image_data:
        print("Download successful. Image size:", len(image_data), "bytes")
    else:
        print("Download failed.")

    test_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_image.jpg")
    if save_image_file(image_data, test_image_path):
        print("Image successfully saved to", test_image_path)
    else:
        print("Failed to save image.")

    if set_desktop_background_image(test_image_path):
        print("Desktop background successfully updated.")
    else:
        print("Failed to update desktop background or not supported on this OS.")

    original_size = (1920, 1080)
    new_size = scale_image(original_size)
    print(f"Original size: {original_size} -> Scaled size: {new_size}")

    return

def download_image(image_url):
    """Downloads an image from a specified URL.

    DOES NOT SAVE THE IMAGE FILE TO DISK.

    Args:
        image_url (str): URL of image

    Returns:
        bytes: Binary image data, if successful. None, if unsuccessful.
    """
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print("Error downloading image:", e)
        return None

def save_image_file(image_data, image_path):
    """Saves image data as a file on disk.
    
    DOES NOT DOWNLOAD THE IMAGE.

    Args:
        image_data (bytes): Binary image data
        image_path (str): Path to save image file

    Returns:
        bool: True, if successful. False, if unsuccessful.
    """
    if image_data is None:
        print("No image data to save.")
        return False

    try:
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        with open(image_path, 'wb') as f:
            f.write(image_data)
        return True
    except Exception as e:
        print("Error saving image file:", e)
        return False

def set_desktop_background_image(image_path):
    """Sets the desktop background image to a specific image.

    Args:
        image_path (str): Path of image file

    Returns:
        bool: True, if successful. False, if unsuccessful or not supported.
    """
    if not os.path.exists(image_path):
        print("Image path does not exist:", image_path)
        return False

    if sys.platform.startswith('win'):
        try:
            import ctypes
            SPI_SETDESKWALLPAPER = 20
            result = ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 3)
            return True if result else False
        except Exception as e:
            print("Error setting desktop background:", e)
            return False
    else:
        print("Setting desktop background is not supported on this platform.")
        return False

def scale_image(image_size, max_size=(800, 600)):
    """Calculates the dimensions of an image scaled to a maximum width
    and/or height while maintaining the aspect ratio.

    Args:
        image_size (tuple[int, int]): Original image size in pixels (width, height) 
        max_size (tuple[int, int], optional): Maximum image size in pixels (width, height). Defaults to (800, 600).

    Returns:
        tuple[int, int]: Scaled image size in pixels (width, height)
    """
    resize_ratio = min(max_size[0] / image_size[0], max_size[1] / image_size[1])
    new_size = (int(image_size[0] * resize_ratio), int(image_size[1] * resize_ratio))
    return new_size

if __name__ == '__main__':
    main()
