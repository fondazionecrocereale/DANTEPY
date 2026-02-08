from video_transcriber import VideoTranscriber
import sys
import json
import os

def verify():
    # URL for "GNOCCHI di PATATE"
    url = "https://www.youtube.com/watch?v=WTlWGFYdv8Y"
    output_file = "test_gnocchi_whisper.json"
    
    print(f"Testing Whisper transcription and author extraction for URL: {url}")
    transcriber = VideoTranscriber()
    
    # Run transcription
    success = transcriber.transcribe_video(url, output_file)
    
    if success:
        print("Transcription successful.")
        
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Check Author
                author = data.get('author', '')
                print(f"Author field: {author}")
                if "youtube.com" in author or "youtu.be" in author:
                    print("✅ Verification PASSED: Author contains YouTube URL.")
                else:
                    print(f"❌ Verification FAILED/WARNING: Author field '{author}' does not look like a YouTube URL.")
                
                # Check Subtitles (briefly)
                subtitles = data.get('subtitles', [])
                if len(subtitles) > 0:
                    print(f"✅ Generated {len(subtitles)} subtitle segments.")
                    print("First segment sample:", subtitles[0]['text'])
                else:
                    print("❌ Verification FAILED: No subtitles generated.")
                    
        else:
            print("❌ Verification FAILED: Output file not created.")
            
    else:
        print("❌ Transcription failed.")
        
    transcriber.cleanup()

if __name__ == "__main__":
    verify()
