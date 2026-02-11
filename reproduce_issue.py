import yt_dlp
import sys

url = "https://youtube.com/shorts/1ECn1wri3X4"

ydl_opts = {
    'format': 'bestaudio/best',
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'no_warnings': False,
    'quiet': False,
    'verbose': True, # Enable verbose to see more details
    'geo_bypass': True,
    'geo_bypass_country': 'US',
    'source_address': '0.0.0.0',
    'extractor_args': {
        'youtube': {
            'player_client': ['web', 'android'],
        }
    }
}

print(f"Testing download for: {url}")
try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url, download=False)
    print("SUCCESS: Video info extracted.")
except Exception as e:
    print(f"FAILURE: {e}")
