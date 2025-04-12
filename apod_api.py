"""
Library for interacting with NASA's Astronomy Picture of the Day API.
"""

import requests
from datetime import date


API_KEY = 'DEMO_KEY'
APOD_API_URL = "https://api.nasa.gov/planetary/apod"


def main():
    test_date = date.today().isoformat()  
    print(f"Fetching APOD info for {test_date}")
    apod_info = get_apod_info(test_date)
    if apod_info:
        print("APOD Info:")
        print(apod_info)
        image_url = get_apod_image_url(apod_info)
        print("APOD Image URL:")
        print(image_url)
    else:
        print("Failed to retrieve APOD information.")


def get_apod_info(apod_date):
    """Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    Args:
        apod_date (date or str): APOD date (Can also be a string formatted as YYYY-MM-DD)

    Returns:
        dict: Dictionary of APOD info, if successful. None if unsuccessful.
    """
    
    if not isinstance(apod_date, str):
        try:
            apod_date = apod_date.isoformat()
        except Exception as e:
            print(f"Error converting date: {e}")
            return None

    params = {
        'api_key': API_KEY,
        'date': apod_date,
        'thumbs': True,  
    }

    try:
        response = requests.get(APOD_API_URL, params=params)
        response.raise_for_status()
        apod_data = response.json()
        return apod_data
    except requests.exceptions.RequestException as e:
        print("Error fetching APOD info:", e)
        return None


def get_apod_image_url(apod_info_dict):
    """Gets the URL of the APOD image from the dictionary of APOD information.

    If the APOD is an image, gets the URL of the high definition image.
    If the APOD is a video, gets the URL of the video thumbnail.

    Args:
        apod_info_dict (dict): Dictionary of APOD info from API

    Returns:
        str: APOD image URL if available, otherwise None.
    """
    if not apod_info_dict:
        return None

    media_type = apod_info_dict.get('media_type', 'image')
    if media_type == 'video':
        return apod_info_dict.get('thumbnail_url', apod_info_dict.get('url'))
    else:
        return apod_info_dict.get('hdurl', apod_info_dict.get('url'))


if __name__ == '__main__':
    main()
