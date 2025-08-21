#!/usr/bin/env python3
"""
Runs YOLO analysis on the downsampled video.
Performs pose estimation and saves the results to a JSON file.
"""
import os
import json
import cv2
from ultralytics import YOLO

def run_yolo_analysis(video_path: str, pose_model_path: str, output_path: str):
    """Runs YOLO pose estimation on a video and saves the results."""
    print(f"Running YOLO analysis on {video_path}...")
    
    # Load YOLO models
    pose_model = YOLO(pose_model_path)
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Error: Could not open video {video_path}")
        return

    # Get video info
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video Info: {width}x{height} @ {fps:.2f} FPS, {frame_count} frames.")
    
    # Process video
    frame_num = 0
    analysis_results = {
        "video_info": {
            "path": video_path,
            "fps": fps,
            "width": width,
            "height": height,
            "frame_count": frame_count
        },
        "frames": []
    }
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Run pose estimation
        pose_results = pose_model(frame, verbose=False)
        
        frame_data = {"frame_number": frame_num, "pose_estimation": []}
        
        # Extract pose keypoints
        for r in pose_results:
            if r.keypoints is not None and len(r.keypoints.data) > 0:
                for person_keypoints in r.keypoints.data:
                    keypoints_list = person_keypoints.cpu().numpy().tolist()
                    frame_data["pose_estimation"].append(keypoints_list)

        analysis_results["frames"].append(frame_data)
        
        if frame_num % 10 == 0:
            print(f"Processed frame {frame_num}/{frame_count}...")
        
        frame_num += 1
        
    cap.release()
    
    # Save results to JSON
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(analysis_results, f, indent=4)
        
    print(f"✅ YOLO analysis complete. Results saved to {output_path}")

def main():
    """Main function to run YOLO analysis."""
    print("--- Step 2: Running YOLO Analysis ---")
    
    INPUT_VIDEO = "data/downsampled/soccer_demo_4fps.mp4"
    POSE_MODEL = "models/yolov8m-pose.pt"
    OUTPUT_FILE = "analysis/yolo_analysis_4fps.json"
    
    if not os.path.exists(INPUT_VIDEO):
        print(f"❌ Error: Input video not found: {INPUT_VIDEO}")
        print("Please run Step 1 (downsampling) first.")
        return
        
    run_yolo_analysis(INPUT_VIDEO, POSE_MODEL, OUTPUT_FILE)
    
    print("\n🎉 YOLO analysis finished successfully!")

if __name__ == "__main__":
    main() 