
import yt_dlp
import os

def test_quality_selection():
    # Test URL (shorter video preferred, but we'll use --simulate)
    url = "https://www.youtube.com/watch?v=aqz-KE-bpKQ" # Rick Astley - Never Gonna Give You Up (classic test)
    
    print(f"Testing quality selection for {url}...")
    
    # 1. Test format for download_video_file logic
    ydl_opts_video = {
        'format': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best[height<=480]/best',
        'simulate': True,
        'quiet': True,
    }
    
    print("\n[1] Testing video download format selection:")
    with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            print(f"Selected format ID: {info.get('format_id')}")
            print(f"Resolution: {info.get('width')}x{info.get('height')}")
            print(f"Extension: {info.get('ext')}")
            
            if info.get('height', 0) <= 480:
                print("✅ Quality is <= 480p")
            else:
                print(f"❌ Quality is > 480p ({info.get('height')}p)")
        except Exception as e:
            print(f"Error testing video format: {e}")

    # 2. Test format for download_youtube_video fallback logic
    # In download_youtube_video, fmt is 'bestvideo[height<=480]+bestaudio/best[height<=480]/best'
    fmt_fallback = 'bestvideo[height<=480]+bestaudio/best[height<=480]/best'
    ydl_opts_fallback = {
        'format': fmt_fallback,
        'simulate': True,
        'quiet': True,
    }
    
    print("\n[2] Testing fallback format selection:")
    with yt_dlp.YoutubeDL(ydl_opts_fallback) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            print(f"Selected format ID: {info.get('format_id')}")
            print(f"Resolution: {info.get('width')}x{info.get('height')}")
            
            if info.get('height', 0) <= 480:
                print("✅ Quality is <= 480p")
            else:
                print(f"❌ Quality is > 480p ({info.get('height')}p)")
        except Exception as e:
            print(f"Error testing fallback format: {e}")

if __name__ == "__main__":
    test_quality_selection()
