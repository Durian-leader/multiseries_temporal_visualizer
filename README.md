# Multiseries Temporal Visualizer

- [简体中文](README_CN.md)

A comprehensive Python toolkit for processing, analyzing, and visualizing multi-series temporal data. This tool specializes in transforming vibration data or other time-series datasets into high-quality visualizations and animations.

Demo:
- https://youtu.be/eMQt-ECYRZA
- https://youtu.be/zs1seIiErXs
- https://youtu.be/VFoZmemtraI

## Features

- **Data Processing Pipeline**: Transform raw data files into synchronized, analysis-ready formats
- **Interactive Data Selection**: Visually select starting points and regions of interest in your data
- **High-Quality Visualizations**: Generate heatmaps, 3D surface plots, and cross-sectional profile plots
- **Video Generation**: Create smooth animations showing data evolution over time
- **Flexible Configuration**: Customize colors, resolutions, and visual styles
- **Data Extraction**: Extract data at specific time points for detailed analysis

## Project Structure

```
multiseries_temporal_visualizer/
├── python_数据预处理与可视化/    # Main processing scripts
│   ├── 00select_start_idx.py   # Interactive start point selection
│   ├── 01sample.py             # Generate 5-point sampling data
│   ├── 01csv2npz.py            # Convert CSV to NPZ (all points)
│   ├── 02picture.py            # Generate static visualizations
│   ├── 03video.py              # Generate video animations
│   ├── 04查看某个信号小波去噪前后的对比.py  # Wavelet denoising comparison
│   ├── utils/                  # Utility modules
│   │   ├── dataprocess/        # Data processing utilities
│   │   │   ├── vibration_data_loader.py     # Raw data loading
│   │   │   ├── start_idx_visualized_select.py  # Start point selection
│   │   │   ├── debiasing.py    # Baseline correction
│   │   │   └── wavelet_denoise.py  # Wavelet denoising
│   │   └── visualize/          # Visualization utilities
│   │       ├── data_processor.py    # Data grid processing
│   │       └── visualization_generator.py  # Video/image generation
│   └── main.ipynb              # Jupyter notebook for interactive use
├── matlab_数据可视化_比python精美/  # MATLAB visualization scripts
│   ├── main01_3d.m             # 3D surface visualizations
│   ├── main02_heatmap.m        # Heatmap visualizations
│   └── main03_heatmapwithprofile.m  # Heatmap with profiles
│   ├── baseline_correction.py  # Interactive baseline correction
│   └── npz_to_mat.py          # Convert NPZ to MATLAB format
├── CLAUDE.md                  # Development guide
├── INSTALLATION.md            # Installation instructions
└── README.md                  # This file
```

## Data Processing Workflow

### Quick Start Pipeline

**Step 1: Select start indices for data alignment**
```bash
python python_数据预处理与可视化/00select_start_idx.py
```
- Interactive GUI to select starting points for each data file
- Output: CSV files with aligned start points

**Step 2: Choose your processing path**

**Path A - Video Generation (5-point sampling):**
```bash
python python_数据预处理与可视化/01sample.py
python python_数据预处理与可视化/03video.py
```

**Path B - Detailed Analysis (all points):**
```bash
python python_数据预处理与可视化/01csv2npz.py
python python_数据预处理与可视化/02picture.py
```

**Step 3 (Optional): Convert to MATLAB format**
```bash
python python_数据预处理与可视化/npz_to_mat.py
```

### Optional Processing Steps

**Baseline Correction:**
```bash
python python_数据预处理与可视化/baseline_correction.py
```
- Interactive GUI for baseline drift correction
- Can be applied at any stage of the pipeline

**Wavelet Denoising:**
```bash
python python_数据预处理与可视化/04查看某个信号小波去噪前后的对比.py
```
- Compare signals before and after wavelet denoising
- Configurable wavelet parameters

### Advanced Usage

**Using Jupyter Notebooks:**
Open `python_数据预处理与可视化/main.ipynb` for interactive data exploration and processing.

**MATLAB Integration:**
1. Run `python_数据预处理与可视化/npz_to_mat.py` to convert processed data
2. Use MATLAB scripts in `matlab_数据可视化_比python精美/`:
   - `main01_3d.m` - 3D surface plots
   - `main02_heatmap.m` - Heat map visualizations
   - `main03_heatmapwithprofile.m` - Heat maps with profiles

## Output Formats and Visualizations

### Video Outputs (from 03video.py)
- **Heatmap animations**: Time-evolving 2D color maps (.mp4)
- **3D surface videos**: Rotating 3D surface plots (.mp4)
- **Combined visualizations**: Heatmap with cross-sectional profiles (.mp4)

### Static Outputs (from 02picture.py)
- **Time-point visualizations**: Heatmaps at specific time points (.png)
- **Data exports**: CSV files with data at selected time points
- **Grid visualizations**: Spatial arrangement of measurement points

### MATLAB Outputs
- **High-quality 3D surfaces**: Professional-grade 3D visualizations
- **Enhanced heatmaps**: Publication-ready heat map visualizations
- **Profile analysis**: Cross-sectional analysis with detailed profiles

## Color Mapping Options

The toolkit supports numerous color mapping options for visualizations:

- **Continuous Data**: viridis, plasma, inferno, magma, cividis, turbo
- **Classic Gradients**: jet, rainbow, ocean, terrain
- **High Contrast**: hot, cool, copper
- **Scientific Data**: RdBu, coolwarm, seismic, spectral
- **Single Color Gradients**: Blues, Reds, Greens, YlOrRd, BuPu
- **Colorblind-Friendly**: cividis, viridis

## Dependencies

- Python 3.7+
- numpy
- pandas
- matplotlib
- scipy
- pywt (PyWavelets)
- tqdm
- loguru
- pathlib
- FFmpeg (for video generation)
- MATLAB (optional, for enhanced visualizations)

For detailed installation instructions, see [INSTALLATION.md](INSTALLATION.md).