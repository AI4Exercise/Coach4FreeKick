#!/usr/bin/env python3
"""
Creates the final coaching video by overlaying analysis from meta_data.json.
"""
import cv2
import numpy as np
import json
import os
from datetime import datetime
from typing import Dict, List

class VideoVisualizer:
    """Creates the final video visualization from metadata."""
    
    def __init__(self, metadata_path: str, video_path: str, output_dir: str):
        print("--- Step 5: Creating Final Video Visualization ---")
        self.metadata_path = metadata_path
        self.video_path = video_path
        self.output_dir = output_dir

        self.load_metadata()
        self.setup_video()
        self.setup_styles()

    def load_metadata(self):
        """Loads the metadata file."""
        print(f"Loading metadata from {self.metadata_path}...")
        if not os.path.exists(self.metadata_path):
            raise FileNotFoundError(f"Metadata file not found: {self.metadata_path}")
        with open(self.metadata_path, 'r') as f:
            self.metadata = json.load(f)
        self.timeline = self.metadata['timeline_mappings']

    def setup_video(self):
        """Sets up video capture and writer."""
        print(f"Setting up video from {self.video_path}...")
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            raise IOError(f"Could not open video file: {self.video_path}")
        
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.metadata['video_info']['original_fps']
        self.panel_width = self.width
        self.combined_width = self.width + self.panel_width

        os.makedirs(self.output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_path = os.path.join(self.output_dir, f"soccer_coach_final_{timestamp}.mp4")
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter(self.output_path, fourcc, self.fps, (self.combined_width, self.height))

    def setup_styles(self):
        """Defines colors and styles for the overlay."""
        self.colors = {
            'text': (255, 255, 255), 'bg_panel': (20, 20, 30),
            'accent': (255, 215, 0), 'secondary': (180, 180, 180),
            'goal': (0, 255, 100), 'save': (255, 50, 50),
            'in_progress': (0, 165, 255), 'pose': (255, 255, 0)
        }
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def wrap_text(self, text: str, width: int, font, font_scale, thickness) -> List[str]:
        """Wraps text to fit within a specified pixel width."""
        lines = []
        words = text.split(' ')
        while words:
            line = ''
            while words and cv2.getTextSize(line + words[0], font, font_scale, thickness)[0][0] < width:
                line += words.pop(0) + ' '
            lines.append(line.strip())
        return lines

    def draw_pose_skeleton(self, img: np.ndarray, keypoints: List) -> np.ndarray:
        """Draws a pose skeleton on the image."""
        connections = [
            (5, 6), (5, 7), (7, 9), (6, 8), (8, 10), (5, 11), (6, 12), 
            (11, 12), (11, 13), (13, 15), (12, 14), (14, 16)
        ]
        for start_idx, end_idx in connections:
            if keypoints[start_idx][2] > 0.5 and keypoints[end_idx][2] > 0.5:
                pt1 = (int(keypoints[start_idx][0]), int(keypoints[start_idx][1]))
                pt2 = (int(keypoints[end_idx][0]), int(keypoints[end_idx][1]))
                cv2.line(img, pt1, pt2, self.colors['pose'], 2)
        return img

    def create_analysis_panel(self, frame_data: Dict) -> np.ndarray:
        """Creates the right-side analysis panel."""
        panel = np.full((self.height, self.panel_width, 3), self.colors['bg_panel'], dtype=np.uint8)
        y_pos = 40

        # --- Action Description ---
        cv2.putText(panel, "ACTION DESCRIPTION", (20, y_pos), self.font, 0.7, self.colors['accent'], 2)
        y_pos += 30
        desc = frame_data['vlm_analysis']['action_description']
        desc_lines = self.wrap_text(desc, self.panel_width - 40, self.font, 0.5, 1)
        for line in desc_lines[:3]:
            cv2.putText(panel, line, (20, y_pos), self.font, 0.5, self.colors['text'], 1)
            y_pos += 20
        y_pos += 20
            
        # --- Shot Status ---
        status_info = frame_data['shot_status']
        if status_info['status'] != 'idle':
            shot_data = status_info['shot_data']
            color = self.colors['goal'] if shot_data['made'] else self.colors['save']
            
            if status_info['status'] == 'in_flight':
                status_text = f"SHOT #{status_info['shot_num']} IN PROGRESS"
                color = self.colors['in_progress']
            elif status_info['status'] == 'post_result':
                status_text = f"SHOT #{status_info['shot_num']}: {'GOAL!' if shot_data['made'] else 'SAVED!'}"
            else: # pre_shot
                status_text = f"SHOT #{status_info['shot_num']} PREPARING..."
            
            cv2.putText(panel, status_text, (20, y_pos), self.font, 0.7, color, 2)
            y_pos += 30
            
            details_lines = self.wrap_text(f"{shot_data['location']} - {shot_data['details']}", self.panel_width-40, self.font, 0.5, 1)
            for line in details_lines:
                cv2.putText(panel, line, (20, y_pos), self.font, 0.5, self.colors['secondary'], 1)
                y_pos += 20

        return panel

    def run(self):
        """Main loop to process video and generate output."""
        frame_num = 0
        while True:
            ret, frame = self.cap.read()
            if not ret or frame_num >= len(self.timeline):
                break
            
            processed_frame = frame.copy()
            frame_data = self.timeline[frame_num]
            
            # Draw pose on original video
            poses = frame_data['yolo_analysis']['pose_estimation']
            if poses:
                processed_frame = self.draw_pose_skeleton(processed_frame, poses[0])

            # Create analysis panel
            panel = self.create_analysis_panel(frame_data)
            
            # Combine and write frame
            combined_frame = np.hstack([processed_frame, panel])
            self.out.write(combined_frame)

            if frame_num % 60 == 0:
                print(f"Processed frame {frame_num}/{len(self.timeline)}...")
            frame_num += 1

        self.cap.release()
        self.out.release()
        print(f"\n✅ Video visualization created successfully!")
        print(f"Output saved to: {self.output_path}")
        print("\n🎉 Pipeline finished successfully!")

def main():
    """Main function to run the visualization pipeline."""
    visualizer = VideoVisualizer(
        metadata_path="analysis/meta_data.json",
        video_path="data/soccer_demo.mov",
        output_dir="output_videos"
    )
    visualizer.run()

if __name__ == "__main__":
    main() 