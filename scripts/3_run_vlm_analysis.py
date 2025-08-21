#!/usr/bin/env python3
"""
Runs VLM analysis for detailed action description using the 12fps video.
"""
import os
import json
import base64
import cv2
from openai import OpenAI
from dotenv import load_dotenv

def encode_frame(frame) -> str:
    """Encodes a single video frame to a base64 string."""
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode("utf-8")

def get_action_description(client, frame_b64: str) -> dict:
    """Gets action description and kick analysis from OpenAI for a single frame."""
    prompt = """
    Analyze this soccer penalty kick frame.
    1.  **Action Description**: Describe the main action. Is the player approaching the ball, kicking, or is the ball in flight? What is the goalkeeper doing? Be concise.
    2.  **Kick Analysis**: If a kick is happening, describe the player's form. What part of the foot is used?
    
    Return a JSON object with keys "action_description" and "kick_analysis".
    - "action_description": (string)
    - "kick_analysis": {"is_kick": (boolean), "foot_part": (string), "comment": (string)}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{frame_b64}",
                        },
                    ],
                }
            ],
            max_tokens=200,
        )
        content = response.choices[0].message.content
        # Basic parsing, assuming the model returns a clean JSON string
        return json.loads(content.strip("`json\n"))
    except Exception as e:
        print(f"❌ Error calling OpenAI API: {e}")
        return {
            "action_description": "Analysis could not be performed for this frame.",
            "kick_analysis": {"is_kick": False}
        }

def run_vlm_analysis(video_path: str, output_path: str):
    """Runs VLM analysis on a video and saves results to a JSON file."""
    print(f"Running VLM analysis on {video_path}...")
    
    # Load OpenAI client
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found. Please set it in a .env file.")
        return
    client = OpenAI()

    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Error: Could not open video {video_path}")
        return

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    vlm_results = {"frames": []}
    
    frame_num = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Encode frame and get analysis
        frame_b64 = encode_frame(frame)
        analysis = get_action_description(client, frame_b64)
        
        vlm_results["frames"].append({
            "frame_number": frame_num,
            **analysis
        })
        
        print(f"Analyzed frame {frame_num}/{frame_count}...")
        frame_num += 1

    cap.release()
    
    # Save results
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(vlm_results, f, indent=4)
        
    print(f"✅ VLM analysis complete. Results saved to {output_path}")

def main():
    """Main function to run VLM analysis."""
    print("--- Step 3: Running VLM Action Description Analysis ---")
    
    INPUT_VIDEO = "data/downsampled/soccer_demo_12fps.mp4"
    OUTPUT_FILE = "analysis/vlm_action_descriptions_12fps.json"

    if not os.path.exists(INPUT_VIDEO):
        print(f"❌ Error: Input video not found: {INPUT_VIDEO}")
        print("Please run Step 1 (downsampling) first.")
        return

    run_vlm_analysis(INPUT_VIDEO, OUTPUT_FILE)
    
    print("\n🎉 VLM analysis finished successfully!")

if __name__ == "__main__":
    main() 