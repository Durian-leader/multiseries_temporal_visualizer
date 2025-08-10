# Multiseries Temporal Visualizer

- [简体中文](README_CN.md)

A comprehensive Python and MATLAB toolkit for processing, analyzing, and visualizing multi-series temporal data from scientific experiments, particularly for vibration/expansion measurements in materials science.

## Demo Videos
- https://youtu.be/eMQt-ECYRZA
- https://youtu.be/zs1seIiErXs  
- https://youtu.be/VFoZmemtraI

## Key Features

### 🔄 Complete Data Processing Pipeline
- **Raw Data Loading**: Convert TXT files to CSV with metadata parsing
- **Wavelet Denoising**: Configurable wavelet packet denoising with db6 wavelets
- **Interactive Start Point Selection**: Visual GUI for temporal alignment with Vg signal support
- **Baseline Correction**: Automatic and manual baseline drift correction
- **Grid Data Organization**: Convert individual time series into spatial grid format
- **Format Conversion**: NPZ to MATLAB MAT format for cross-platform compatibility

### 📊 Advanced Visualization
- **High-Quality Video Generation**: Heat maps, 3D surface plots, and cross-sectional profiles
- **Static Visualization**: Time-point snapshots and data exports
- **MATLAB Integration**: Professional-grade visualizations using MATLAB scripts
- **Multiple Color Schemes**: 20+ scientific color maps including viridis, plasma, turbo
- **Interactive Controls**: Zoom, pan, and reset functionality

### 🛠 User-Friendly Interface
- **Integrated Jupyter Notebook**: Complete pipeline with progress tracking and error handling
- **Command-Line Interface**: Flexible scripting with extensive configuration options
- **GUI Tools**: Interactive baseline correction and start point selection
- **Real-time Preview**: Data validation and visualization during processing

## Quick Start

### Method 1: Integrated Jupyter Notebook (Recommended)
```bash
jupyter notebook main.ipynb
```
The notebook provides a complete, interactive pipeline with:
- Real-time progress tracking
- Comprehensive error handling
- Data validation at each step
- Built-in visualization preview

### Method 2: Command Line Pipeline
```bash
# Step 1: Data preprocessing (TXT→CSV with denoising and alignment)
python python_dataprepare_visualize/00select_start_idx.py \
  --input-dir ./input/data \
  --output-dir ./output/processed_csv \
  --rows 4 --cols 6

# Step 2: Optional baseline correction
python python_dataprepare_visualize/00_5_manual_baseline_correction.py \
  -i ./output/processed_csv \
  -o ./output/baseline_corrected_csv \
  -a  # Auto mode, or -m for manual GUI

# Step 3: Convert to NPZ format
python python_dataprepare_visualize/01csv2npz.py \
  --input-folder ./output/baseline_corrected_csv \
  --output-file ./output/my_processed_data.npz \
  --rows 4 --cols 6

# Step 4: Generate MATLAB file
python python_dataprepare_visualize/npz_to_mat.py \
  --input-file ./output/my_processed_data.npz \
  --output-file ./my_processed_data.mat
```

### Method 3: Individual Processing Scripts
```bash
# For video generation (5-point sampling)
python python_dataprepare_visualize/01sample.py
python python_dataprepare_visualize/03video.py

# For detailed analysis (all data points)
python python_dataprepare_visualize/02picture.py
```

## Project Architecture

```
multiseries_temporal_visualizer/
├── main.ipynb                          # 🎯 Integrated pipeline notebook
├── python_dataprepare_visualize/       # Core processing scripts
│   ├── 00select_start_idx.py          # Data preprocessing pipeline
│   ├── 00_5_manual_baseline_correction.py  # Baseline correction
│   ├── 01sample.py                     # 5-point sampling
│   ├── 01csv2npz.py                    # CSV to NPZ conversion
│   ├── 02picture.py                    # Static visualizations
│   ├── 03video.py                      # Video generation
│   ├── npz_to_mat.py                   # NPZ to MATLAB conversion
│   └── utils/                          # Core utilities
│       ├── dataprocess/                # Data processing tools
│       │   ├── vibration_data_loader.py      # TXT/CSV data loader
│       │   ├── start_idx_visualized_select.py # Interactive start point selection
│       │   ├── baseline_correction.py         # GUI baseline correction
│       │   ├── wavelet_denoise.py             # Wavelet denoising
│       │   └── debiasing.py                   # Baseline drift correction
│       └── visualize/                  # Visualization tools
│           ├── data_processor.py              # Grid data processing
│           ├── visualization_generator.py     # Video/image generation
│           └── extract_timepoint.py           # Time-point extraction
├── matlab_数据可视化_比python精美/      # MATLAB visualization scripts
│   ├── main01_3d.m                     # 3D surface plots
│   ├── main02_heatmap.m                # Heat map visualizations
│   └── main03_heatmapwithprofile.m     # Heat maps with profiles
├── input/data/                         # Raw data files (TXT format)
├── output/                             # Processing outputs
└── logs/                              # Processing logs
```

## Data Processing Workflow

### Core Pipeline
1. **Raw Data (TXT files)** → `00select_start_idx.py` → **CSV files with alignment**
2. **Aligned CSV** → `00_5_manual_baseline_correction.py` → **Baseline-corrected CSV**
3. **Corrected CSV** → `01csv2npz.py` → **NPZ grid data**
4. **NPZ data** → `npz_to_mat.py` → **MATLAB MAT file**
5. **MAT file** → **MATLAB scripts** → **High-quality visualizations**

### Key Processing Features
- **Vg Signal Support**: Automatic time delay compensation (default: 2.5ms)
- **Grid Organization**: Configurable spatial arrangement (e.g., 4×6 grid)
- **Memory Efficiency**: Chunked processing for large datasets
- **Data Validation**: Comprehensive error checking and recovery

## Advanced Features

### Interactive Start Point Selection
- **Dual-Signal Display**: Vg voltage and original signal comparison on synchronized subplots
- **Visual Alignment**: What-you-see-is-what-you-get time alignment with configurable Vg delay
- **Time Delay Compensation**: Automatic Vg signal offset (default: 2.5ms) for proper alignment
- **Advanced Zoom Controls**:
  - Mouse wheel zoom centered on cursor position
  - X-axis synchronized between both signal plots
  - Independent Y-axis scaling for each signal
- **Precise Navigation**:
  - Shift+drag or middle mouse button for panning
  - 'r' key or Reset View button to restore original view
  - Smart zoom maintains selected start point markers
- **Keyboard Shortcuts**: 'n' for next, 'k' to skip, 'r' to reset view
- **Hardware Delay Compensation**: Configurable Vg delay (0-10ms) for measurement system alignment

### Baseline Correction Modes
- **Automatic Mode**: Linear correction using first and last points
- **Manual Mode**: Interactive GUI for custom baseline point selection
- **Skip Mode**: Bypass correction when not needed

### Wavelet Denoising
- **Configurable Wavelets**: Default db6, customizable levels
- **Selective Filtering**: Keep specific frequency components
- **Before/After Comparison**: Visual validation of denoising effectiveness

### Visualization Options
- **Heat Map Animations**: Time-evolving 2D color maps
- **3D Surface Videos**: Rotating 3D surface plots with customizable angles
- **Profile Analysis**: Cross-sectional views with heat maps
- **Static Snapshots**: High-resolution images at specific time points
- **Multiple Export Formats**: MP4, GIF, PNG, CSV data export

### Color Mapping Options
- **Scientific Color Maps**: viridis, plasma, inferno, magma, cividis, turbo
- **Classic Gradients**: jet, rainbow, ocean, terrain, hot, cool
- **Diverging Schemes**: RdBu, coolwarm, seismic, spectral
- **Single Color Gradients**: Blues, Reds, Greens, YlOrRd, BuPu
- **Colorblind-Friendly**: cividis, viridis optimized for accessibility

## MATLAB Visualization

After generating the MAT file, use MATLAB scripts for enhanced visualizations:

```matlab
% Load the processed data
data = load('my_processed_data.mat');

% Run visualization scripts
main01_3d          % 3D surface animations
main02_heatmap     % Heat map visualizations  
main03_heatmapwithprofile  % Heat maps with cross-sectional profiles
```

## Configuration Options

### Grid Setup
- **Flexible Dimensions**: Configurable rows × cols (e.g., 4×6, 6×6)
- **Natural File Sorting**: Automatic handling of file naming patterns
- **Missing File Handling**: Graceful handling of incomplete grids

### Processing Parameters
- **Wavelet Settings**: Type (db6), decomposition levels (6), node selection
- **Vg Signal Alignment**:
  - Default delay: 2.5ms for hardware compensation
  - Configurable range: 0-10ms for different measurement systems
  - Real-time application during file loading for WYSIWYG alignment
  - Automatic detection of Vg files (files ending with 'V.txt' or 'V.csv')
- **Temporal Settings**: Signal truncation options, sampling rate handling
- **Memory Management**: All-points vs. sampled processing modes
- **Output Control**: Flexible file naming and directory structure

### Video Generation
- **Quality Settings**: Configurable DPI (150), bitrate, frame rate (30 fps)
- **Format Options**: MP4 (FFmpeg), GIF (Pillow), HTML fallbacks
- **Visual Enhancements**: Timestamps, color bars, custom titles
- **View Controls**: Fixed or rotating 3D views, elevation/azimuth settings

## Advanced Usage Examples

### Vg Signal Delay Configuration

```python
from python_dataprepare_visualize.utils.dataprocess.start_idx_visualized_select import StartIdxVisualizedSelect

# Default 2.5ms delay for most measurement systems
processor = StartIdxVisualizedSelect(
    input_folder="./input/data",
    output_folder="./output/processed",
    vg_delay=0.0025  # 2.5ms default
)

# Custom delay for specific hardware setup
processor = StartIdxVisualizedSelect(
    input_folder="./input/data", 
    output_folder="./output/processed",
    vg_delay=0.003  # 3ms for slower response systems
)

# No delay for pre-aligned data
processor = StartIdxVisualizedSelect(
    input_folder="./input/data",
    output_folder="./output/processed", 
    vg_delay=0.0  # No delay compensation
)

processor.run()
```

### Interactive Start Point Selection Workflow

1. **Initial Overview**: View complete signal traces for both Vg and original data
2. **Zoom to Region**: Use mouse wheel to zoom into time region of interest
3. **Fine-tune Position**: Shift+drag to pan and center the critical transition point  
4. **Precise Selection**: Click to select start point with pixel-level accuracy
5. **Verify Selection**: Press 'r' to reset view and confirm the selection looks correct
6. **Save and Continue**: Press 'n' to save trimmed data and move to next file

### Mouse and Keyboard Controls

| Control | Action |
|---------|--------|
| Left Click | Select start point |
| Mouse Wheel | Zoom in/out centered on cursor |
| Shift + Drag | Pan view (X-axis synchronized, Y-axis independent) |
| Middle Mouse + Drag | Alternative pan method |
| 'r' Key | Reset to original view |
| 'n' Key | Save selection and process next file |
| 'k' Key | Skip current file |

## System Requirements

### Core Dependencies
- Python 3.7+
- NumPy, pandas, matplotlib, scipy
- PyWavelets (wavelet analysis)
- loguru (logging), tqdm (progress bars)
- tkinter (GUI components)

### Optional Dependencies
- **FFmpeg**: High-quality MP4 video output (recommended)
- **MATLAB**: Enhanced visualizations (optional)

### Platform Support
- **Cross-Platform**: Windows, macOS, Linux
- **Font Handling**: Automatic Chinese font selection per platform
- **Path Compatibility**: Uses pathlib for cross-platform paths

## Performance Optimization

### Memory Management
- **Chunked Processing**: Handles large datasets without memory overflow
- **Sampling Options**: 5-point sampling vs. all-points processing
- **Efficient Data Structures**: NumPy arrays for optimal performance

### Processing Speed
- **Parallel Operations**: Efficient data loading and processing
- **Progress Tracking**: Real-time progress bars and logging
- **Error Recovery**: Robust handling of data format variations

## Troubleshooting

### Common Issues
- **FFmpeg Installation**: Install for high-quality videos (see INSTALLATION.md)
- **Memory Errors**: Use sampling mode or reduce grid size
- **Font Rendering**: Install platform-specific Chinese fonts
- **File Format**: Ensure consistent file naming conventions

### Performance Tips
- **Grid Size**: Start with smaller grids (4×6) for testing
- **Sampling**: Use 5-point sampling for faster iteration
- **Video Quality**: Adjust DPI/bitrate based on requirements
- **Batch Processing**: Process multiple experiments efficiently

For detailed installation instructions, see [INSTALLATION.md](INSTALLATION.md).

For development guidance, see [CLAUDE.md](CLAUDE.md).