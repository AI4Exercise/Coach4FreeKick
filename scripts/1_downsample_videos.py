#!/usr/bin/env python3
"""
Downsamples the source video to multiple framerates for analysis.
"""
import subprocess
import os

def downsample_video(input_path: str, output_dir: str, fps: int):
    """Downsamples a video to a specific FPS using ffmpeg."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}_{fps}fps.mp4")
    
    print(f"Downsampling {input_path} to {fps} FPS -> {output_path}...")
    
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-r', str(fps),
        '-an',  # No audio
        '-y',   # Overwrite output
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Successfully downsampled to {fps} FPS.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error downsampling to {fps} FPS:")
        print(e.stderr)
        raise

def main():
    """Main function to run all downsampling."""
    print("--- Step 1: Downsampling Videos ---")
    
    INPUT_VIDEO = "data/soccer_demo.mov"
    DOWNSAMPLED_DIR = "data/downsampled"
    
    # Ensure the source video exists
    if not os.path.exists(INPUT_VIDEO):
        print(f"❌ Error: Source video not found at {INPUT_VIDEO}")
        print("Please make sure the input video is placed in the 'data' directory.")
        return

    # Downsample to 4 FPS for coaching analysis
    downsample_video(INPUT_VIDEO, DOWNSAMPLED_DIR, 4)
    
    # Downsample to 12 FPS for action description
    downsample_video(INPUT_VIDEO, DOWNSAMPLED_DIR, 12)
    
    print("\n🎉 All videos downsampled successfully!")

if __name__ == "__main__":
    main() 