# APOD Desktop :milky_way:

A Python application that automatically sets NASA's Astronomy Picture of the Day (APOD) as your desktop background. Features caching, SHA-256 validation, and optional GUI.

[![NASA API](https://img.shields.io/badge/Powered%20By-NASA%20API-blue.svg)](https://api.nasa.gov) 
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)

## :star2: Features

### Core Functionality
- **Date Control**: Fetch APODs from 1995-06-16 to today
- **Smart Caching**: 
  - SQLite database tracks downloaded images
  - SHA-256 hash prevents duplicates
- **Media Handling**:
  - Auto-download HD images (10MB+ support)
  - Video thumbnail support (YouTube embeds)
- **System Integration**:
  - Windows desktop background automation
  - Cross-platform path handling

### Bonus GUI Features
- Calendar date picker (1995-present)
- APOD gallery browser
- Real-time explanation viewer
- Adaptive window scaling (800x600 to 4K)

## :rocket: Quick Start

### Prerequisites
```bash
pip install requests pillow python-dateutil
