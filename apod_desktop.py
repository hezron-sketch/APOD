"""
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py [apod_date]

Parameters:
  apod_date = APOD date (format: YYYY-MM-DD)
"""
import argparse
import datetime
import os
import re
import sqlite3
import sys
import hashlib
import requests
from datetime import date, datetime
from pathlib import Path
import image_lib


script_dir = os.path.dirname(os.path.abspath(__file__))
image_cache_dir = os.path.join(script_dir, 'images')
image_cache_db = os.path.join(image_cache_dir, 'image_cache.db')


NASA_API_KEY = 'DEMO_KEY' 
NASA_API_URL = 'https://api.nasa.gov/planetary/apod'
FIRST_APOD_DATE = datetime(1995, 6, 16).date()

def main():
    apod_date = get_apod_date()    
    init_apod_cache()
    apod_id = add_apod_to_cache(apod_date)
    apod_info = get_apod_info(apod_id)
    if apod_id != 0:
        image_lib.set_desktop_background_image(apod_info['file_path'])

def get_apod_date():
    """Gets and validates the APOD date from command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument('date', nargs='?', help='APOD date (YYYY-MM-DD)')
    args = parser.parse_args()
    
    if args.date:
        try:
            apod_date = date.fromisoformat(args.date)
        except ValueError:
            sys.exit(f"Error: Invalid date format; Invalid isoformat string: '{args.date}'")
    else:
        apod_date = date.today()
    
    if apod_date < FIRST_APOD_DATE:
        sys.exit(f"Error: Date cannot be before {FIRST_APOD_DATE.isoformat()}")
    if apod_date > date.today():
        sys.exit("Error: APOD date cannot be in the future")
    
    return apod_date

def init_apod_cache():
    """Initializes the image cache directory and database."""
    os.makedirs(image_cache_dir, exist_ok=True)
    
    conn = sqlite3.connect(image_cache_db)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS apod
                 (id INTEGER PRIMARY KEY,
                  title TEXT NOT NULL,
                  explanation TEXT NOT NULL,
                  file_path TEXT NOT NULL UNIQUE,
                  sha256 TEXT NOT NULL UNIQUE)''')
    conn.commit()
    conn.close()

def add_apod_to_cache(apod_date):
    """Adds APOD to cache and returns record ID."""
    print(f"APOD date: {apod_date.isoformat()}")
    
    
    apod_info = get_apod_info_from_nasa(apod_date)
    if not apod_info:
        return 0
    
   
    if apod_info['media_type'] == 'video':
        image_url = apod_info['thumbnail_url']
    else:
        image_url = apod_info['url']
    
    
    image_data = image_lib.download_image(image_url)
    if not image_data:
        return 0
    
    
    sha256 = hashlib.sha256(image_data).hexdigest()
    apod_id = get_apod_id_from_db(sha256)
    
    if apod_id:
        print("APOD image is already in cache.")
        return apod_id
    
    
    file_path = determine_apod_file_path(apod_info['title'], image_url)
    if image_lib.save_image_file(image_data, file_path):
        print(f"Saving image file as {file_path}...success")
    else:
        return 0
    
   
    apod_id = add_apod_to_db(apod_info['title'], apod_info['explanation'], file_path, sha256)
    return apod_id

def get_apod_info_from_nasa(apod_date):
    """Retrieves APOD information from NASA API."""
    params = {
        'api_key': NASA_API_KEY,
        'date': apod_date.isoformat(),
        'thumbs': True
    }
    try:
        response = requests.get(NASA_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        print(f"Getting {apod_date} APOD information from NASA...success")
        return {
            'title': data['title'],
            'explanation': data['explanation'],
            'url': data.get('url', ''),
            'media_type': data['media_type'],
            'thumbnail_url': data.get('thumbnail_url', '')
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching APOD data: {e}")
        return None

def add_apod_to_db(title, explanation, file_path, sha256):
    """Adds APOD metadata to the database."""
    conn = sqlite3.connect(image_cache_db)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO apod (title, explanation, file_path, sha256) VALUES (?, ?, ?, ?)',
                  (title, explanation, file_path, sha256))
        conn.commit()
        print("Adding APOD to image cache DB...success")
        return c.lastrowid
    except sqlite3.IntegrityError:
        return 0
    finally:
        conn.close()

def get_apod_id_from_db(sha256):
    """Returns APOD ID if exists in database."""
    conn = sqlite3.connect(image_cache_db)
    c = conn.cursor()
    c.execute('SELECT id FROM apod WHERE sha256=?', (sha256,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def determine_apod_file_path(image_title, image_url):
    """Generates valid file path for APOD image."""
    
    clean_title = re.sub(r'[^\w\s-]', '', image_title.strip())
    clean_title = re.sub(r'\s+', '_', clean_title)
    
    
    ext = Path(image_url).suffix.split('?')[0]
    
    
    file_name = f"{clean_title}{ext}"
    return os.path.join(image_cache_dir, file_name)

def get_apod_info(image_id):
    """Retrieves APOD info from database."""
    conn = sqlite3.connect(image_cache_db)
    c = conn.cursor()
    c.execute('SELECT title, explanation, file_path FROM apod WHERE id=?', (image_id,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return {
            'title': result[0],
            'explanation': result[1],
            'file_path': result[2]
        }
    return {'file_path': ''}

def get_all_apod_titles():
    """Returns list of all APOD titles in cache."""
    conn = sqlite3.connect(image_cache_db)
    c = conn.cursor()
    c.execute('SELECT title FROM apod')
    results = c.fetchall()
    conn.close()
    return [result[0] for result in results]

if __name__ == '__main__':
    main()