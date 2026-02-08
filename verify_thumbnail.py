from video_transcriber import VideoTranscriber
import sys

def verify():
    url = "https://firebasestorage.googleapis.com/v0/b/ciceroxxi.firebasestorage.app/o/DanteXXI%2FYTDown.com_Shorts_Cose-da-sapere-sull-Inno-d-Italia-parte-_Media_3bzIAkv3C9o_001_1080p.mp4?alt=media&token=c5f03f51-5169-4f3e-a204-ccce31ef669f"
    output_file = "test_thumbnail_verification.json"
    
    print(f"Testing thumbnail extraction for URL: {url}")
    transcriber = VideoTranscriber()
    
    # Run transcription
    success = transcriber.transcribe_audio_from_url(url, output_file)
    
    if success:
        print("Transcription successful.")
        # Check json for image field
        import json
        import os
        
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                image_path = data.get('image', '')
                print(f"Image field in JSON: {image_path}")
                
                if image_path and os.path.exists(image_path):
                    print("✅ Verification PASSED: Thumbnail file exists locally.")
                elif image_path:
                     print("⚠️ Verification PARTIAL: Image path is in JSON but file check failed (maybe it's a URL or absolute path issue?)")
                else:
                    print("❌ Verification FAILED: Image field is empty.")
        else:
            print("❌ Verification FAILED: Output file not created.")
            
    else:
        print("❌ Transcription failed.")
        
    transcriber.cleanup()

if __name__ == "__main__":
    verify()
