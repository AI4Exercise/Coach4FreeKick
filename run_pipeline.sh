#!/bin/bash
# This script runs the entire SoccerKickCoach analysis and visualization pipeline.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
CONDA_ENV_NAME="AI4Exercise"
SOURCE_VIDEO="data/soccer_demo.mov"
MODELS_DIR="models"
YOLO_POSE_MODEL="$MODELS_DIR/yolov8m-pose.pt"
YOLO_OBJECT_MODEL="$MODELS_DIR/yolov8m.pt"

# --- Introduction ---
echo "🚀 STARTING SOCCER KICK COACH PIPELINE 🚀"
echo "=========================================="
echo "Conda Env: $CONDA_ENV_NAME"
echo "Source Video: $SOURCE_VIDEO"
echo "=========================================="

# --- Check for Conda Environment ---
if ! conda info --envs | grep -q "$CONDA_ENV_NAME"; then
    echo "❌ Error: Conda environment '$CONDA_ENV_NAME' not found."
    echo "Please ensure the environment is created and activated using:"
    echo "conda create --name $CONDA_ENV_NAME python=3.9 -y"
    exit 1
fi
echo "✅ Conda environment found."
conda activate "$CONDA_ENV_NAME"

# --- Check for Source Video ---
if [ ! -f "$SOURCE_VIDEO" ]; then
    echo "❌ Error: Source video not found at '$SOURCE_VIDEO'"
    echo "Please make sure the input video exists in the 'data/' directory."
    exit 1
fi
echo "✅ Source video found."

# --- Check and Create .env file ---
if [ ! -f ".env" ]; then
    echo "⚠️ .env file not found. Creating .env.example."
    echo "# Example .env file" > .env.example
    echo "# Copy this to .env and fill in your API key" >> .env.example
    echo "OPENAI_API_KEY=\"YOUR_OPENAI_API_KEY_HERE\"" >> .env.example
    echo "❌ Error: Please create a .env file from .env.example and add your OpenAI API key."
    exit 1
fi
echo "✅ .env file found."

# --- Download YOLO Models if necessary ---
mkdir -p $MODELS_DIR
if [ ! -f "$YOLO_POSE_MODEL" ]; then
    echo "⚠️ YOLO pose model not found. Downloading..."
    wget -q --show-progress -O $YOLO_POSE_MODEL https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m-pose.pt
fi
if [ ! -f "$YOLO_OBJECT_MODEL" ]; then
    echo "⚠️ YOLO object model not found. Downloading..."
    wget -q --show-progress -O $YOLO_OBJECT_MODEL https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt
fi
echo "✅ YOLO models are present."


# --- Run Pipeline Steps ---
cd scripts

echo -e "\n[STEP 1/5] Downsampling videos..."
python 1_downsample_videos.py

echo -e "\n[STEP 2/5] Running YOLO analysis..."
python 2_run_yolo_analysis.py

echo -e "\n[STEP 3/5] Running VLM analysis (action descriptions)..."
python 3_run_vlm_analysis.py

echo -e "\n[STEP 4/5] Creating metadata file..."
python 4_create_metadata.py

echo -e "\n[STEP 5/5] Creating final video visualization..."
python 5_create_visualization.py

cd ..

# --- Cleanup ---
echo -e "\n[CLEANUP] Removing intermediate downsampled videos..."
rm -rf data/downsampled
echo "✅ Cleanup complete."

# --- Completion ---
echo -e "\n🎉 PIPELINE COMPLETED SUCCESSFULLY! 🎉"
echo "=========================================="
echo "✅ Final video saved in the 'output_videos' directory."
echo "➡️ You can now view the final coaching video."
echo "==========================================" 