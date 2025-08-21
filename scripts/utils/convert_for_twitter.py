#!/usr/bin/env python3
"""
Convert video to Twitter-compatible format
Twitter video requirements:
- MP4 format (H264 video codec, AAC audio)
- Maximum 512MB
- Maximum 2:20 duration (140 seconds)
- Minimum resolution: 32x32
- Maximum resolution: 1920x1200 (and 1200x1900)
- Aspect ratios: 1:2.39 - 2.39:1
- Maximum frame rate: 40fps
- Maximum bitrate: 25Mbps
"""

import subprocess
import sys
import os

def convert_video_for_twitter(input_path, output_path=None):
    """Convert video to Twitter-compatible format."""
    
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        return
    
    # Generate output filename if not provided
    if output_path is None:
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = f"{base_name}_twitter.mp4"
    
    print(f"Converting video for Twitter...")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    
    # FFmpeg command for Twitter compatibility
    # Using H.264 codec with AAC audio, limiting bitrate and ensuring compatibility
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-c:v', 'libx264',      # H.264 video codec
        '-preset', 'slow',       # Better compression
        '-crf', '23',           # Quality setting (lower = better, 23 is good)
        '-c:a', 'aac',         # AAC audio codec
        '-b:a', '128k',        # Audio bitrate
        '-movflags', '+faststart',  # Optimize for streaming
        '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
        '-vf', 'scale=1280:720',  # Scale to 720p for good quality and smaller size
        '-r', '30',            # Frame rate 30fps
        '-maxrate', '5M',      # Maximum bitrate 5Mbps (well under Twitter's 25Mbps limit)
        '-bufsize', '10M',     # Buffer size
        '-y',                  # Overwrite output
        output_path
    ]
    
    try:
        print("\nRunning FFmpeg conversion...")
        subprocess.run(cmd, check=True)
        
        # Check output file size
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"\n✅ Conversion complete!")
        print(f"Output file: {output_path}")
        print(f"File size: {file_size_mb:.1f} MB")
        
        if file_size_mb > 512:
            print("⚠️ Warning: File size exceeds Twitter's 512MB limit!")
            print("Consider reducing quality or duration.")
        else:
            print("✅ File size is within Twitter's limits!")
            
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
        return None
    except FileNotFoundError:
        print("Error: ffmpeg not found. Please install ffmpeg:")
        print("  sudo apt-get install ffmpeg")
        return None
    
    return output_path

def main():
    """Main function."""
    # Default to the latest video if no argument provided
    if len(sys.argv) > 1:
        input_video = sys.argv[1]
    else:
        # Find the latest video in demo_videos
        demo_dir = "../demo_videos"
        videos = [f for f in os.listdir(demo_dir) if f.endswith('.mp4')]
        if videos:
            videos.sort()
            input_video = os.path.join(demo_dir, videos[-1])
            print(f"Using latest video: {input_video}")
        else:
            print("No videos found in demo_videos directory")
            return
    
    convert_video_for_twitter(input_video)

if __name__ == "__main__":
    main() 