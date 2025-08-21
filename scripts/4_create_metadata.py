#!/usr/bin/env python3
"""
Creates a comprehensive metadata file by combining all analysis outputs.
This file is the single source of truth for the visualization script.
"""
import json
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class ShotInfo:
    """Dataclass to hold information about a single shot."""
    shot_num: int
    made: bool
    kick_frame_12fps: int
    result_frame_12fps: int
    foot_contact: str
    location: str
    details: str
    kick_frame_original: int = 0
    result_frame_original: int = 0

@dataclass
class ShotStatus:
    """Dataclass for the status of a shot at a given frame."""
    status: str
    shot_num: int = 0
    shot_data: Dict[str, Any] = None

def get_shot_status(frame_num_original: int, shots: List[ShotInfo]) -> ShotStatus:
    """Determines the shot status for a given original frame number."""
    for shot in shots:
        pre_shot_start = shot.kick_frame_original - 45
        post_result_end = shot.result_frame_original + 30

        if pre_shot_start <= frame_num_original < shot.kick_frame_original:
            return ShotStatus("pre_shot", shot.shot_num, asdict(shot))
        if shot.kick_frame_original <= frame_num_original < shot.result_frame_original:
            return ShotStatus("in_flight", shot.shot_num, asdict(shot))
        if shot.result_frame_original <= frame_num_original < post_result_end:
            return ShotStatus("post_result", shot.shot_num, asdict(shot))
            
    return ShotStatus("idle")

def create_metadata_file():
    """Generates the final meta_data.json file."""
    print("--- Step 4: Creating Metadata File ---")

    # --- Configuration ---
    YOLO_ANALYSIS_PATH = "analysis/yolo_analysis_4fps.json"
    VLM_ANALYSIS_PATH = "analysis/vlm_action_descriptions_12fps.json"
    OUTPUT_PATH = "analysis/meta_data.json"
    
    ORIGINAL_FPS = 30
    ANALYSIS_FPS_YOLO = 4
    ANALYSIS_FPS_VLM = 12

    # --- Load Analysis Files ---
    print("Loading analysis files...")
    for path in [YOLO_ANALYSIS_PATH, VLM_ANALYSIS_PATH]:
        if not os.path.exists(path):
            print(f"❌ Error: Analysis file not found at {path}")
            print("Please run the prerequisite analysis steps first.")
            return

    with open(YOLO_ANALYSIS_PATH, 'r') as f:
        yolo_data = json.load(f)
    with open(VLM_ANALYSIS_PATH, 'r') as f:
        vlm_data = json.load(f)

    # --- Define Shot Information ---
    print("Defining shot data...")
    shots = [
        ShotInfo(1, True, 3, 13, "Right", "Top-left corner", "Goalkeeper stationary"),
        ShotInfo(2, False, 16, 22, "Right", "Top-right, middle", "Goalkeeper saves"),
        ShotInfo(3, True, 32, 38, "Right", "Center", "Ball deflects in"),
        ShotInfo(4, True, 44, 52, "Right", "Low center", "Fast shot, deflects in"),
        ShotInfo(5, True, 60, 68, "Right", "Top-right corner", "Curved shot, keeper gives up"),
    ]

    # Convert shot timings from analysis FPS to original 30fps
    for shot in shots:
        shot.kick_frame_original = int(shot.kick_frame_12fps * (ORIGINAL_FPS / ANALYSIS_FPS_VLM))
        shot.result_frame_original = int(shot.result_frame_12fps * (ORIGINAL_FPS / ANALYSIS_FPS_VLM))

    # --- Create Timeline Mappings ---
    print("Creating timeline mappings...")
    num_original_frames = int(yolo_data['video_info']['frame_count'] * (ORIGINAL_FPS / ANALYSIS_FPS_YOLO))
    timeline_mappings = []

    for i in range(num_original_frames):
        yolo_frame_index = int(i * (ANALYSIS_FPS_YOLO / ORIGINAL_FPS))
        vlm_frame_index = int(i * (ANALYSIS_FPS_VLM / ORIGINAL_FPS))

        # Clamp indices to prevent out-of-bounds errors
        yolo_frame_index = min(yolo_frame_index, len(yolo_data['frames']) - 1)
        vlm_frame_index = min(vlm_frame_index, len(vlm_data['frames']) - 1)

        shot_status = get_shot_status(i, shots)

        mapping = {
            "original_frame": i,
            "yolo_analysis": yolo_data['frames'][yolo_frame_index],
            "vlm_analysis": vlm_data['frames'][vlm_frame_index],
            "shot_status": asdict(shot_status)
        }
        timeline_mappings.append(mapping)
    
    print(f"Mapped {len(timeline_mappings)} original frames.")

    # --- Assemble Final Metadata ---
    print("Assembling final metadata object...")
    made_shots = sum(1 for shot in shots if shot.made)
    meta_data = {
        "video_info": {
            "original_fps": ORIGINAL_FPS,
            "original_frame_count": num_original_frames,
            "analysis_fps": {"yolo": ANALYSIS_FPS_YOLO, "vlm": ANALYSIS_FPS_VLM},
        },
        "shot_info": {
            "total_shots": len(shots),
            "made_shots": made_shots,
            "missed_shots": len(shots) - made_shots,
            "shots": [asdict(s) for s in shots]
        },
        "timeline_mappings": timeline_mappings
    }

    # --- Save Metadata File ---
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(meta_data, f, indent=4)

    print(f"✅ Metadata file created successfully at {OUTPUT_PATH}")
    print("\n🎉 Metadata creation finished successfully!")

if __name__ == "__main__":
    create_metadata_file() 