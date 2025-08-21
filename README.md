# Soccer Kick Coach AI

This project provides a comprehensive AI-powered analysis of a soccer penalty kick video. It uses a combination of Computer Vision and Vision-Language Models (VLMs) to generate a detailed, frame-by-frame coaching video.

The final output is a split-screen video that shows the original footage alongside a real-time analysis panel with shot tracking, pose estimation, and AI-generated action descriptions.

## 🎯 Key Features

- **🤖 AI-Powered Analysis**: Uses YOLOv8 for pose detection and OpenAI GPT-4o for action descriptions
- **⚡ Modular Pipeline**: 5-step process that separates AI analysis from video rendering
- **📊 Shot Tracking**: Automatically tracks 5 penalty shots with detailed outcomes
- **🎨 Professional Visualization**: Split-screen layout with real-time overlays
- **🔄 Reproducible**: One-command pipeline execution with automatic setup
- **🐦 Social Media Ready**: Built-in Twitter video conversion utility

## 🏗️ Architecture

The pipeline is designed to be modular and reproducible. It separates the AI analysis from the final video rendering by using an intermediate `meta_data.json` file. This allows for rapid iteration on the visualization without re-running expensive AI models.

### Pipeline Flow:
1. **Downsampling** → Creates 4fps (pose analysis) and 12fps (VLM descriptions) versions
2. **YOLO Analysis** → Extracts pose keypoints from 4fps video
3. **VLM Analysis** → Generates action descriptions from 12fps video using GPT-4o
4. **Metadata Creation** → Combines all analysis into a master timeline file
5. **Visualization** → Renders final video using only the metadata (no AI models)

## 📁 Project Structure

```
SoccerKickCoach/
├── 📂 data/
│   └── soccer_demo.mov           # Original input video (17.6s, 30fps)
├── 📂 models/
│   ├── yolov8m-pose.pt           # YOLO pose estimation model (~52MB)
│   └── yolov8m.pt                # YOLO object detection model (~50MB)
├── 📂 scripts/
│   ├── 1_downsample_videos.py    # Step 1: Create 4fps and 12fps versions
│   ├── 2_run_yolo_analysis.py    # Step 2: Extract pose keypoints
│   ├── 3_run_vlm_analysis.py     # Step 3: Generate action descriptions
│   ├── 4_create_metadata.py     # Step 4: Combine all analysis data
│   ├── 5_create_visualization.py # Step 5: Render final video
│   └── 📂 utils/
│       └── convert_for_twitter.py # Twitter-optimized video conversion
├── 📂 analysis/                  # Generated analysis files (gitignored)
├── 📂 output_videos/             # Final rendered videos (gitignored)
├── .env.example                  # Template for API keys
├── .gitignore                    # Keeps repo clean
├── README.md                     # This file
├── requirements.txt              # Python dependencies
└── run_pipeline.sh               # 🚀 Master script (run this!)
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** (recommended: 3.9)
- **Conda** for environment management
- **ffmpeg** for video processing
- **OpenAI API key** with GPT-4o access

### One-Command Setup & Execution

```bash
# 1. Clone and enter the repository
git clone <repository_url>
cd SoccerKickCoach

# 2. Create conda environment
conda create --name AI4Exercise python=3.9 -y
conda activate AI4Exercise

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your OpenAI API key
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY="sk-your-key-here"

# 5. Run the entire pipeline!
bash run_pipeline.sh
```

That's it! The script will:
- ✅ Verify your setup (conda env, source video, API key)
- ✅ Download YOLO models automatically (~100MB total)
- ✅ Run all 5 pipeline steps in sequence
- ✅ Clean up intermediate files
- ✅ Output final video to `output_videos/`

## 📋 Detailed Setup Instructions

### 1. System Requirements

**Install ffmpeg:**
```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install ffmpeg

# macOS (with Homebrew)
brew install ffmpeg

# Verify installation
ffmpeg -version
```

### 2. Environment Setup

**Create and activate conda environment:**
```bash
conda create --name AI4Exercise python=3.9 -y
conda activate AI4Exercise
```

**Install Python dependencies:**
```bash
pip install -r requirements.txt
```

### 3. API Configuration

**Create `.env` file:**
```bash
# Copy the example
cp .env.example .env

# Edit with your favorite editor
nano .env
```

**Add your OpenAI API key:**
```env
OPENAI_API_KEY="sk-proj-your-actual-key-here"
```

### 4. Verify Setup

**Check that everything is ready:**
```bash
# Verify conda environment
conda info --envs | grep AI4Exercise

# Verify ffmpeg
ffmpeg -version

# Verify source video exists
ls -la data/soccer_demo.mov

# Verify API key is set
cat .env
```

## 🔧 Pipeline Details

### Step 1: Video Downsampling
- **Input**: `data/soccer_demo.mov` (30fps, ~17.6 seconds)
- **Output**: 
  - `data/downsampled/soccer_demo_4fps.mp4` (for pose analysis)
  - `data/downsampled/soccer_demo_12fps.mp4` (for VLM analysis)
- **Purpose**: Optimize for different AI models and reduce processing time

### Step 2: YOLO Analysis
- **Input**: 4fps downsampled video
- **Model**: YOLOv8-medium pose estimation
- **Output**: `analysis/yolo_analysis_4fps.json`
- **Contains**: Pose keypoints for each frame

### Step 3: VLM Analysis
- **Input**: 12fps downsampled video
- **Model**: OpenAI GPT-4o Vision
- **Output**: `analysis/vlm_action_descriptions_12fps.json`
- **Contains**: Detailed action descriptions and kick analysis

### Step 4: Metadata Creation
- **Input**: All analysis JSON files
- **Output**: `analysis/meta_data.json`
- **Purpose**: Master timeline mapping every original frame to analysis data
- **Contains**: Shot timings, status tracking, complete frame mappings

### Step 5: Visualization
- **Input**: Original video + metadata file
- **Output**: `output_videos/soccer_coach_final_TIMESTAMP.mp4`
- **Features**: Split-screen layout, pose overlays, shot tracking, action descriptions

## 📊 Analysis Results

The system analyzes **5 penalty shots** with the following results:
- **Total Shots**: 5
- **Goals**: 4 (80% success rate)
- **Saves**: 1
- **Shot Locations**: Top-left, top-right, center, low center, top-right corner
- **Analysis Depth**: Frame-by-frame pose estimation and action descriptions

## 🛠️ Advanced Usage

### Running Individual Steps

If you want to run steps individually (for development or debugging):

```bash
cd scripts

# Step 1: Downsample videos
python 1_downsample_videos.py

# Step 2: YOLO analysis
python 2_run_yolo_analysis.py

# Step 3: VLM analysis (requires OpenAI API)
python 3_run_vlm_analysis.py

# Step 4: Create metadata
python 4_create_metadata.py

# Step 5: Generate final video
python 5_create_visualization.py
```

### Twitter Conversion

Convert your final video for Twitter sharing:
```bash
cd scripts
python utils/convert_for_twitter.py ../output_videos/soccer_coach_final_TIMESTAMP.mp4
```

### Customization

- **Modify shot data**: Edit `scripts/4_create_metadata.py` to change shot timings or details
- **Adjust visualization**: Modify `scripts/5_create_visualization.py` for different overlay styles
- **Change analysis parameters**: Update prompts in `scripts/3_run_vlm_analysis.py`

## 🚨 Troubleshooting

### Common Issues

**"Conda environment not found"**
```bash
conda create --name AI4Exercise python=3.9 -y
conda activate AI4Exercise
```

**"ffmpeg not found"**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

**"OpenAI API key required"**
- Ensure `.env` file exists in project root
- Check that your API key is correct and has GPT-4o access
- Verify format: `OPENAI_API_KEY="sk-proj-..."`

**"YOLO models not found"**
- The pipeline automatically downloads them
- If download fails, manually download from:
  - [yolov8m-pose.pt](https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m-pose.pt)
  - [yolov8m.pt](https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt)

**"Video file not found"**
- Ensure `data/soccer_demo.mov` exists
- Check file permissions and format

### Performance Notes

- **Processing Time**: ~5-10 minutes total (depends on API response times)
- **Memory Usage**: ~2-4GB during processing
- **Storage**: ~500MB for all generated files
- **API Costs**: ~$0.50-1.00 per full run (GPT-4o Vision calls)

## 🎉 Expected Output

After successful completion, you'll find:
- **Final Video**: `output_videos/soccer_coach_final_TIMESTAMP.mp4`
- **Video Features**:
  - Split-screen layout (original left, analysis right)
  - Real-time pose skeleton overlay
  - Shot tracking with goal/save indicators
  - AI-generated action descriptions
  - Professional styling and colors

## 🤝 Contributing

This project demonstrates a complete AI video analysis pipeline. Feel free to:
- Adapt for other sports or video types
- Improve the visualization design
- Add new analysis models
- Optimize performance

## 📄 License

See `LICENSE` file for details.

---

**Built with**: YOLOv8 • OpenAI GPT-4o • OpenCV • Python • ⚽

