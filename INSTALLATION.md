# Installation Guide

- [简体中文](INSTALLATION_CN.md)

This guide provides instructions for installing all dependencies required to run the Multiseries Temporal Visualizer.

## Python Requirements

The project requires Python 3.7 or newer. We recommend using a virtual environment for installation.

### Creating a Virtual Environment (Optional but Recommended)

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Basic Dependencies

Install the required Python packages:

```bash
pip install numpy pandas matplotlib scipy tqdm loguru
```

## FFmpeg Installation

FFmpeg is required to generate high-quality MP4 animations. If FFmpeg is not installed, the system will fall back to alternative formats (GIF or HTML).

### Windows

1. Download FFmpeg from [FFmpeg's official website](https://ffmpeg.org/download.html) or [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
2. Download the "ffmpeg-release-full" version and extract it to your desired location (e.g., `C:\FFmpeg`)
3. Add FFmpeg's bin directory to your system PATH:
   - Right-click "This PC" → "Properties" → "Advanced system settings" → "Environment Variables"
   - Find "Path" under "System variables", click "Edit"
   - Add the path to FFmpeg's bin directory, e.g., `C:\FFmpeg\bin`
   - Click "OK" to save changes
4. Restart your command prompt or PowerShell for the PATH changes to take effect
5. Verify the installation by running:
   ```
   ffmpeg -version
   ```

### macOS

Use Homebrew to install FFmpeg:

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install FFmpeg
brew install ffmpeg
```

### Ubuntu/Debian Linux

```bash
sudo apt update
sudo apt install ffmpeg
```

### Fedora Linux

```bash
sudo dnf install ffmpeg
```

### CentOS/RHEL Linux

```bash
sudo yum install epel-release
sudo yum install ffmpeg
```

## Verifying the Installation

You can verify that matplotlib is correctly configured to use FFmpeg by running the following Python code:

```python
import matplotlib.animation as animation
print("Available animation writers:", animation.writers.list())
```

If 'ffmpeg' appears in the output, the configuration is correct.

## Font Support for Non-English Characters (Optional)

If you need to display non-Latin characters (like Chinese) in your visualizations:

### Windows
Default support for:
- SimHei
- Microsoft YaHei
- SimSun

### macOS
Default support for:
- PingFang SC
- Heiti SC
- STHeiti

### Linux
You may need to install:

Ubuntu/Debian:
```bash
sudo apt install fonts-wqy-microhei fonts-wqy-zenhei
```

Fedora:
```bash
sudo dnf install wqy-microhei-fonts wqy-zenhei-fonts
```

## Troubleshooting

If you encounter errors related to video generation:

1. Confirm FFmpeg is correctly installed and added to your PATH
2. Check if matplotlib can find FFmpeg using the verification script above
3. Try forcing a different output format by modifying the file extension:
   - `.gif` for GIF format (using Pillow)
   - `.html` for HTML animation

If you see matplotlib-related errors, try installing a specific version:

```bash
pip install matplotlib==3.5.3
```

## Advanced Configuration

For advanced users who want to specify custom FFmpeg encoding parameters, you can use command line arguments when running visualizations:

```python
viz_gen = VisualizationGenerator(
    processed_data=processed_data,
    fps=30,               # Control frame rate
    dpi=150,              # Control resolution
    colormap="viridis",   # Set color scheme
    output_folder="./output/videos"
)

# Generate high-quality video
viz_gen.generate_heatmap_video(
    output_file="heatmap.mp4",
    title="Signal Intensity",
    bitrate="8000k"       # Control video quality
)
```