# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based multiseries temporal visualizer toolkit for processing, analyzing, and visualizing multi-series temporal data (particularly vibration data). The codebase transforms raw TXT data files into synchronized datasets and generates high-quality visualizations including heatmaps, 3D surface plots, and animations.

## Core Architecture

### Workflow Overview
The system provides three main processing pathways as shown in the architectural diagram:

**Path 1: Wavelet Denoising Workflow**
- Input TXT files → `04查看某个信号小波去噪前后的对比.py` → Denoised comparison visualization

**Path 2: Standard Processing Pipeline** 
- Input TXT files → `00select_start_idx.py` → CSV files → `01sample.py` → `my_processed_data_500points.npz` → `03video.py` → Video animations

**Path 3: Full Resolution Pipeline**
- Input TXT files → `00select_start_idx.py` → CSV files → `my_processed_data_use_all_points.npz` → `02picture.py` → Static visualizations + CSV data export

### Data Processing Pipeline
The toolkit follows a sequential data processing pipeline:

1. **Raw Data Loading** (`utils/dataprocess/vibration_data_loader.py`): Converts TXT files to CSV format
2. **Wavelet Denoising** (`utils/dataprocess/wavelet_denoise.py`): Applies wavelet transforms for noise reduction  
3. **Interactive Start Selection** (`utils/dataprocess/start_idx_visualized_select.py`): GUI-based tool for selecting data start points
4. **Data Debiasing** (`utils/dataprocess/debiasing.py`): Normalizes data by setting first values to zero
5. **Grid Organization** (`utils/visualize/data_processor.py`): Organizes CSV files into synchronized grid structures
6. **Visualization Generation** (`utils/visualize/visualization_generator.py`): Creates animations and static plots

### Key Components

- **VibrationDataLoader**: Handles TXT to CSV conversion with metadata extraction
- **WaveletDenoiser**: Provides configurable wavelet-based noise reduction
- **StartIdxVisualizedSelect**: Interactive matplotlib-based GUI for data trimming
- **DataProcessor**: Synchronizes multiple time series into grid format with configurable sampling
- **VisualizationGenerator**: Creates heatmaps, 3D surfaces, and video animations

## Development Workflow

### Main Entry Points
- `main.ipynb`: Complete workflow demonstration notebook - run this for full pipeline
- `00select_start_idx.py`: Preprocessing script (TXT→CSV, wavelet denoising, start index selection, debiasing)
- `01sample.py`: Generates sampled processed data (`my_processed_data_500points.npz`) for video creation
- `02picture.py`: Generates full-resolution processed data (`my_processed_data_use_all_points.npz`) for static visualizations and CSV export
- `03video.py`: Creates video animations from sampled data
- `04查看某个信号小波去噪前后的对比.py`: Wavelet denoising comparison visualization tool

### Directory Structure
```
input/data/           # Raw TXT files organized by experiment
output/               # All generated outputs
├── data_csv/         # Converted CSV files  
├── data_csv_denoised/    # Wavelet-denoised data
├── data_csv_start-idx-reselected/  # Trimmed data
├── data_csv_*_debiased/  # Normalized data
└── *.npz            # Processed grid data for visualization
utils/
├── dataprocess/     # Data loading, denoising, preprocessing  
└── visualize/       # Grid processing and visualization
```

### Common Commands

Since this is a Python toolkit without package management files, install dependencies manually:
```bash
pip install numpy pandas matplotlib scipy tqdm loguru pywavelets
```

For video generation (requires FFmpeg):
```bash
# Windows: Download from https://ffmpeg.org/ and add to PATH
# macOS: brew install ffmpeg  
# Linux: sudo apt install ffmpeg
```

Run the complete pipeline:
```bash
jupyter notebook main.ipynb
# Or for automated processing:
python 00select_start_idx.py
```

## Data Flow Architecture

The system processes multi-experiment vibration data organized in a grid pattern:
- Input files named as `{row}{col}.txt` (e.g., `11.txt`, `12.txt`, etc.)
- Grid dimensions configurable (typically 6x6 for 36 measurement points)
- Temporal synchronization across all measurement points
- Output supports both sampled (500 points) and full-resolution data

## Visualization Capabilities

- **Heatmap Videos**: 2D intensity maps over time
- **3D Surface Animations**: Rotating or fixed-angle surface plots  
- **Profile Cross-sections**: Combined heatmap with line profiles
- **Static Snapshots**: High-resolution images at specific time points
- **Configurable Colormaps**: Supports 20+ scientific colormaps including viridis, plasma, jet

## Key Configuration Options

- Wavelet denoising: `wavelet='db6'`, `level=6`, configurable frequency retention
- Grid sampling: `sampling_points=500` or `use_all_points=True`
- Video quality: Configurable FPS, DPI, bitrate via VisualizationGenerator
- Color ranges: Global or per-visualization vmin/vmax settings
- Output formats: MP4 (preferred), GIF, HTML fallbacks

## Logging

The system uses loguru for comprehensive logging:
- Console output at INFO level
- File logging to `logs/log.log`
- Component-specific logs (e.g., `visualization_generator.log`)