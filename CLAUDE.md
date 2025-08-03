# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multiseries temporal data visualization toolkit focused on processing and visualizing time-series data from scientific experiments, particularly for swelling/expansion measurements in materials science. The project provides both Python and MATLAB implementations for data preprocessing and visualization.

## Common Development Commands

### Python Environment Setup
```bash
# Install dependencies (check requirements in individual scripts)
pip install numpy pandas matplotlib scipy pywt loguru tqdm pathlib
```

### Data Processing Workflow

#### Main Processing Pipeline
```bash
# Step 1: Select start indices for data alignment (input: 原始数据文件)
python python_数据预处理与可视化/00select_start_idx.py
# Output: 一系列csv文件 (中间数据)

# Step 2a: Generate grid data for video processing (5-point sampling)
python python_数据预处理与可视化/01sample.py
# Output: outputmy_processed_data_5_00points.npz (数据后台的数据)

# Step 2b: Generate full grid data (all points)
python python_数据预处理与可视化/01csv2npz.py  
# Output: outputmy_processed_data_use_all_points.npz (包含所有信息的处理后数据)

# Step 3a: Create visualizable videos from 5-point data
python python_数据预处理与可视化/03video.py
# Output: 可视化的视频

# Step 3b: Generate static visualizations from all-point data
python python_数据预处理与可视化/02picture.py
# Output: 某个时刻的可视化 + 该时刻的数据导出(csv)

# Step 4: Convert NPZ to MAT format for MATLAB processing
python npz_to_mat.py
# Output: matlab可用 → 可视化的视频
```

#### Optional Processing Steps
```bash
# Baseline correction (interactive GUI) - can be applied before main pipeline
python baseline_correction.py
# Output: 去偏置后可优化

# Wavelet denoising comparison
python python_数据预处理与可视化/04查看某个信号小波去噪前后的对比.py
# Output: 去噪后可视化
```

### MATLAB Workflow
```matlab
% Run main visualization scripts in matlab_数据可视化_比python精美/
main01_3d.m      % 3D surface plots
main02_heatmap.m  % Heat map visualizations  
main03_heatmapwithprofile.m  % Heat maps with cross-sectional profiles
```

## Code Architecture

### Core Data Processing Pipeline

1. **Raw Data Loading** (`vibration_data_loader.py:26-131`)
   - Loads time-series data from text files with metadata parsing
   - Handles file format validation and error recovery
   - Converts to CSV format for downstream processing

2. **Data Preprocessing** (`python_数据预处理与可视化/utils/dataprocess/`)
   - **Start Index Selection**: Interactive tool for temporal alignment
   - **Baseline Correction**: GUI-based baseline drift correction
   - **Wavelet Denoising**: Configurable wavelet packet denoising

3. **Grid Data Processing** (`data_processor.py:21-371`)
   - Converts individual time series into spatial grid format
   - Handles temporal synchronization and interpolation
   - Manages memory-efficient data structures for large datasets

4. **Visualization Generation** (`visualization_generator.py:71-1496`)
   - Creates high-quality video animations (heat maps, 3D surfaces)
   - Supports multiple color schemes and export formats
   - Handles FFmpeg integration for video encoding

### Key Data Structures

- **Grid Data Format**: 3D numpy arrays `[time, rows, cols]` for spatial-temporal data
- **Processed Data Dictionary**: Contains grid_data, time_points, signal ranges, and metadata
- **File Path Grid**: 2D array mapping spatial positions to data file paths

### Visualization Capabilities

1. **Heat Map Animations**: Time-evolving 2D color maps
2. **3D Surface Videos**: Rotating 3D surface plots over time
3. **Profile Analysis**: Cross-sectional views with heat maps
4. **Static Snapshots**: Individual time-point visualizations

## Important Implementation Details

### Memory Management
- Large datasets are processed in chunks to avoid memory overflow
- Use `use_all_points=False` in DataProcessor for memory-constrained environments
- Grid data is stored as numpy arrays for efficient operations

### File Organization
- Input CSV files should follow natural sorting order (e.g., file1.csv, file2.csv, ..., file10.csv)
- Grid positions are assigned row-major: `row = idx // cols, col = idx % cols`
- Output videos/images are saved to `./output/videos/` by default

### Visualization Configuration
- Color maps are configurable via `CLASSIC_COLORMAPS` dictionary
- Video quality controlled by bitrate and DPI settings
- FFmpeg is preferred for high-quality video output, falls back to GIF/HTML

### Cross-Platform Considerations
- Chinese font handling is platform-specific (Windows: SimHei, macOS: PingFang SC, Linux: WenQuanYi)
- File paths use pathlib for cross-platform compatibility
- GUI components require tkinter for baseline correction tool

## Data Flow

### Primary Data Processing Pipeline
1. **原始数据文件 (Raw Data)** → `00select_start_idx.py` → **一系列csv文件 (CSV Series)**
2. **CSV Series** → `01sample.py` → **outputmy_processed_data_5_00points.npz (5-point Grid)**
3. **CSV Series** → `01csv2npz.py` → **outputmy_processed_data_use_all_points.npz (Full Grid)**
4. **5-point Grid** → `03video.py` → **可视化的视频 (Visualization Videos)**
5. **Full Grid** → `02picture.py` → **某个时刻的可视化 + CSV Export**
6. **NPZ Files** → `npz_to_mat.py` → **matlab可用 (MATLAB Format)** → **可视化的视频**

### Optional Processing Branches
- **Any Stage** → `baseline_correction.py` → **去偏置后可优化 (Debiased Data)**
- **CSV Files** → `04查看某个信号小波去噪前后的对比.py` → **去噪后可视化 (Denoised Visualization)**

## Troubleshooting

### Common Issues
- **FFmpeg not found**: Install FFmpeg or use alternative output formats (GIF/HTML)
- **Memory errors**: Reduce sampling_points or use chunked processing
- **File sorting issues**: Ensure consistent naming convention for input files
- **Font rendering**: Install appropriate Chinese fonts for cross-platform compatibility

### Performance Optimization  
- Use `use_all_points=False` for faster processing with fewer time points
- Adjust `dpi` and `bitrate` settings based on quality requirements
- Process smaller grid sizes (rows × cols) for faster iteration during development