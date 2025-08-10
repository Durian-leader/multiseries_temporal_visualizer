# Installation Guide

- [简体中文](INSTALLATION_CN.md)

This guide provides step-by-step instructions for installing all dependencies required to run the Multiseries Temporal Visualizer toolkit.

## System Requirements

- **Python**: 3.7 or newer
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 4GB+ RAM recommended for large datasets
- **Storage**: 1GB+ free space for processing outputs

## Quick Installation

### Option 1: Using pip (Recommended)

```bash
# Clone or download the repository
cd multiseries_temporal_visualizer

# Install core dependencies
pip install -r requirements.txt

# Verify installation
python -c "import numpy, pandas, matplotlib, scipy, pywt, loguru, tqdm; print('✓ All packages installed successfully')"
```

### Option 2: Manual Installation

```bash
# Core scientific computing libraries
pip install numpy pandas scipy

# Visualization libraries
pip install matplotlib

# Wavelet analysis
pip install PyWavelets

# Logging and progress bars
pip install loguru tqdm

# Optional: Enhanced plotting (if needed)
pip install plotly>=5.0.0
```

## Virtual Environment Setup (Recommended)

Using a virtual environment helps avoid package conflicts:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Deactivate when done (optional)
deactivate
```

## FFmpeg Installation (Essential for Video Generation)

FFmpeg is **highly recommended** for generating high-quality MP4 videos. Without it, the system will fall back to lower-quality GIF or HTML formats.

### Windows

**Method 1: Using winget (Windows 10/11)**
```bash
winget install ffmpeg
```

**Method 2: Manual Installation**
1. Download FFmpeg from [FFmpeg's official website](https://ffmpeg.org/download.html#build-windows) or [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
2. Download the "release" build (not static) and extract to `C:\ffmpeg`
3. Add FFmpeg to your PATH:
   - Press `Win + X` and select "System"
   - Click "Advanced system settings" → "Environment Variables"
   - Find "Path" in "System variables", click "Edit"
   - Click "New" and add: `C:\ffmpeg\bin`
   - Click "OK" to save all changes
4. **Restart your command prompt/PowerShell**
5. Verify installation: `ffmpeg -version`

### macOS

**Method 1: Using Homebrew (Recommended)**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install FFmpeg
brew install ffmpeg
```

**Method 2: Using MacPorts**
```bash
sudo port install ffmpeg
```

### Linux

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Fedora:**
```bash
sudo dnf install ffmpeg
```

**CentOS/RHEL:**
```bash
# Enable EPEL repository first
sudo yum install epel-release
sudo yum install ffmpeg
```

**Arch Linux:**
```bash
sudo pacman -S ffmpeg
```

## Jupyter Notebook Setup

For the integrated pipeline experience:

```bash
# Install Jupyter
pip install jupyter notebook

# Optional: Install JupyterLab for enhanced interface
pip install jupyterlab

# Start Jupyter Notebook
jupyter notebook

# OR start JupyterLab
jupyter lab
```

## GUI Dependencies

The toolkit includes interactive GUI tools for baseline correction and start point selection.

### tkinter (Usually Pre-installed)

Most Python installations include tkinter by default. If not:

**Ubuntu/Debian:**
```bash
sudo apt install python3-tk
```

**Fedora:**
```bash
sudo dnf install tkinter
```

**macOS/Windows:** Usually pre-installed with Python

## Font Support for Non-English Characters

For proper Chinese character rendering in visualizations:

### Windows
Default fonts supported:
- SimHei (黑体)
- Microsoft YaHei (微软雅黑)  
- SimSun (宋体)

**If characters don't display correctly:**
1. Go to Settings → Time & Language → Language
2. Add Chinese (Simplified) or Chinese (Traditional)
3. Install language pack when prompted

### macOS
Default fonts supported:
- PingFang SC (苹方-简)
- Heiti SC (黑体-简)
- STHeiti (华文黑体)

**If needed:**
```bash
# Install additional Chinese fonts via Homebrew
brew install --cask font-source-han-sans
```

### Linux

**Ubuntu/Debian:**
```bash
sudo apt install fonts-wqy-microhei fonts-wqy-zenhei
sudo apt install fonts-noto-cjk  # Alternative comprehensive font pack
```

**Fedora:**
```bash
sudo dnf install wqy-microhei-fonts wqy-zenhei-fonts
sudo dnf install google-noto-sans-cjk-fonts  # Alternative
```

**Arch Linux:**
```bash
sudo pacman -S wqy-microhei wqy-zenhei
```

## MATLAB Integration (Optional)

For enhanced 3D visualizations and publication-quality figures:

1. **Install MATLAB** R2018b or newer
2. **Ensure MATLAB is in your system PATH**
3. **Verify installation:**
   ```bash
   matlab -batch "disp('MATLAB is working')"
   ```
4. **Test MAT file compatibility:**
   ```matlab
   % In MATLAB command window
   data = load('my_processed_data.mat');
   disp(fieldnames(data));
   ```

## Verification and Testing

### Basic Verification

```bash
# Test core Python packages
python -c "
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy
import pywt
import loguru
import tqdm
print('✓ All core packages working')
"
```

### FFmpeg Verification

```bash
# Check FFmpeg installation
ffmpeg -version

# Test matplotlib FFmpeg integration
python -c "
import matplotlib.animation as animation
writers = animation.writers.list()
print('Available writers:', writers)
if 'ffmpeg' in writers:
    print('✓ FFmpeg integration working')
else:
    print('⚠ FFmpeg not available - videos will use fallback formats')
"
```

### Font Verification

```python
# Test Chinese font support
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# List available fonts
fonts = [f.name for f in fm.fontManager.ttflist if 'SimHei' in f.name or 'PingFang' in f.name or 'WenQuanYi' in f.name]
print("Available Chinese fonts:", fonts)

# Test plot with Chinese characters
plt.figure(figsize=(6, 4))
plt.plot([1, 2, 3], [1, 4, 2])
plt.title('测试中文显示')
plt.xlabel('时间')
plt.ylabel('信号')
plt.savefig('font_test.png', dpi=150, bbox_inches='tight')
print("✓ Font test saved as 'font_test.png'")
```

### GUI Testing

```python
# Test tkinter availability
try:
    import tkinter as tk
    root = tk.Tk()
    root.title("GUI Test")
    tk.Label(root, text="✓ GUI working").pack()
    print("✓ GUI test window should appear")
    # Uncomment next line to show window
    # root.mainloop()
    root.destroy()
except ImportError:
    print("⚠ tkinter not available - GUI features will not work")
```

## Quick Start Test

Test the complete installation by running a minimal workflow:

```bash
# Navigate to project directory
cd multiseries_temporal_visualizer

# Test data loading (assuming you have sample data)
python -c "
from python_dataprepare_visualize.utils.dataprocess.vibration_data_loader import VibrationDataLoader
print('✓ Data loader working')
"

# Test Jupyter notebook (will open in browser)
jupyter notebook main.ipynb
```

## Troubleshooting

### Common Issues and Solutions

**"No module named 'X'" Errors:**
```bash
# Ensure you're in the correct environment
pip list | grep package_name

# Reinstall missing package
pip install --upgrade package_name
```

**FFmpeg Not Found:**
```bash
# Windows: Restart command prompt after PATH changes
# macOS/Linux: Check PATH
echo $PATH | grep ffmpeg

# Verify FFmpeg location
which ffmpeg  # macOS/Linux
where ffmpeg  # Windows
```

**Memory Errors During Processing:**
- Reduce grid size (e.g., use 4×6 instead of 6×6)
- Enable sampling mode in processing scripts
- Close other applications to free memory

**GUI Not Displaying:**
- Ensure X11 forwarding is enabled for SSH connections
- On WSL, install an X server like VcXsrv
- Check tkinter installation

**Slow Video Generation:**
- Reduce DPI setting (e.g., 100 instead of 150)
- Lower frame rate (e.g., 24 fps instead of 30)
- Use shorter video clips for testing

**Chinese Characters Not Displaying:**
- Install appropriate fonts for your platform
- Clear matplotlib font cache: `rm ~/.matplotlib/fontlist-v*.json`
- Restart Python after font installation

### Performance Optimization Tips

1. **Use SSD storage** for faster I/O operations
2. **Increase RAM** for larger datasets (8GB+ recommended)
3. **Enable GPU acceleration** if using MATLAB visualizations
4. **Use sampling mode** for initial testing and development

### Platform-Specific Notes

**Windows Subsystem for Linux (WSL):**
- Install Windows-based FFmpeg for better integration
- Use VcXsrv for GUI applications
- Mount Windows drives for data access

**macOS Apple Silicon (M1/M2):**
- Use conda or mamba for better ARM64 support
- Some packages may require Rosetta 2

**Linux Server/Headless:**
- Use `matplotlib.use('Agg')` backend
- Install virtual framebuffer: `sudo apt install xvfb`
- Run GUI tools with: `xvfb-run python script.py`

## Advanced Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Optional environment variables
MATPLOTLIB_BACKEND=TkAgg
NUMEXPR_MAX_THREADS=4
OMP_NUM_THREADS=4
```

### Custom Configuration

Modify default settings in your scripts:

```python
# In your processing scripts
import matplotlib
matplotlib.rcParams['font.size'] = 12
matplotlib.rcParams['figure.dpi'] = 150
matplotlib.rcParams['savefig.dpi'] = 300
```

## Getting Help

If you encounter issues:

1. **Check the troubleshooting section** in this guide
2. **Review error messages** carefully - they often contain solutions
3. **Test individual components** using the verification scripts above
4. **Check system resources** (memory, disk space, CPU usage)

## Next Steps

Once installation is complete:

1. **Read** [README.md](README.md) for usage instructions
2. **Try** the integrated Jupyter notebook: `jupyter notebook main.ipynb`
3. **Process sample data** using the quick start commands
4. **Explore** advanced features and MATLAB integration

Your installation is now complete and ready for scientific data visualization!