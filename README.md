# Multiseries Temporal Visualizer

- [简体中文](README_CN.md)

A comprehensive Python and MATLAB toolkit for processing, analyzing, and visualizing multi-series temporal data from scientific experiments, particularly focused on OECT (Organic Electrochemical Transistor) swelling measurements and similar materials science applications.

## Demo Videos
- https://youtu.be/eMQt-ECYRZA
- https://youtu.be/zs1seIiErXs  
- https://youtu.be/VFoZmemtraI

## Key Features

### 🎯 Integrated Pipeline Interface
- **Unified Jupyter Notebook**: Complete pipeline with `main.ipynb` for interactive processing
- **Programmatic API**: Clean function interfaces through `steps.py` for automation
- **Real-time Progress Tracking**: Comprehensive logging and error handling
- **Flexible Processing**: Support for both complete pipeline and individual steps

### 🔄 Complete Data Processing Pipeline
- **Raw Data Loading**: Convert TXT files to CSV with metadata parsing
- **Interactive Start Point Selection**: Visual GUI for temporal alignment with Vg signal support
- **Debiasing Processing**: Automatic baseline offset correction and data truncation
- **Grid Data Organization**: Convert individual time series into spatial grid format
- **Format Conversion**: NPZ to MATLAB MAT format for cross-platform compatibility

### 📊 Advanced Visualization
- **High-Quality Video Generation**: Heat maps, 3D surface plots, and cross-sectional profiles
- **Static Visualization**: Time-point snapshots and data exports
- **MATLAB Integration**: Professional-grade visualizations using MATLAB scripts
- **Multiple Color Schemes**: 20+ scientific color maps including viridis, plasma, turbo

### 🛠 User-Friendly Interface
- **Integrated Workflow**: Main notebook handles complete pipeline automatically
- **Interactive GUI Tools**: Start point selection and baseline correction
- **Command-Line Interface**: Individual script access for advanced users
- **Real-time Validation**: Data preview and error recovery during processing

## Quick Start

### Method 1: Integrated Jupyter Notebook (Recommended)
```bash
jupyter notebook main.ipynb
```
The notebook provides a complete, interactive pipeline with:
- Sequential step execution with automatic error handling
- Real-time progress tracking with detailed logging
- Configurable parameters directly in notebook cells
- Automatic output directory management
- Built-in result validation and summary reporting

### Method 2: Programmatic API
```python
from python_dataprepare_visualize.steps import *

# Step 1: TXT to CSV conversion
result1 = convert_txt_to_csv('data/origin', 'data/csv')

# Step 2: Interactive start point selection
result2 = select_start_indices('data/csv', 'data/csv_起始点选择', vg_delay=0.0025)

# Step 3: Debiasing and truncation
result3 = apply_debiasing('data/csv_起始点选择', 'data/csv_起始点选择_去偏')

# Step 4: Convert to NPZ format
result4 = convert_csv_to_npz_file('data/csv_起始点选择_去偏', 'data/data.npz', rows=4, cols=6)

# Step 5: Generate MATLAB file
result5 = convert_npz_to_mat_file('data/data.npz', 'data/data.mat')
```

### Method 3: Individual Scripts
```bash
# Advanced users can still access individual components
python python_dataprepare_visualize/csv2npz.py \
  --input-folder ./data/processed \
  --output-file ./data/output.npz \
  --rows 4 --cols 6

python python_dataprepare_visualize/npz_to_mat.py \
  --input-file ./data/output.npz \
  --output-file ./data/output.mat
```

## Project Architecture

```
multiseries_temporal_visualizer/
├── main.ipynb                          # 🎯 Primary integrated pipeline
├── python_dataprepare_visualize/       # Core processing package
│   ├── steps.py                        # 🔧 Unified API for all processing steps
│   ├── csv2npz.py                      # CSV to NPZ conversion
│   ├── npz_to_mat.py                   # NPZ to MATLAB conversion
│   ├── 00_5_manual_baseline_correction.py  # Baseline correction script
│   ├── batch_baseline_correction.py    # Batch baseline processing
│   └── utils/                          # Core utilities
│       ├── dataprocess/                # Data processing components
│       │   ├── vibration_data_loader.py      # TXT/CSV loader with metadata
│       │   ├── start_idx_visualized_select.py # Interactive GUI for alignment
│       │   ├── baseline_correction.py         # GUI baseline correction
│       │   ├── debiasing.py                   # Data offset correction
│       │   └── wavelet_denoise.py             # Wavelet filtering
│       └── visualize/                  # Visualization components
│           ├── data_processor.py              # Grid data organization
│           ├── visualization_generator.py     # Video/image generation
│           ├── extract_timepoint.py           # Time-point extraction
│           └── example.py                     # Usage examples
├── matlab_数据可视化_比python精美/      # MATLAB visualization suite
│   ├── main01_3d.m                     # 3D surface animations
│   └── main03_heatmapwithprofile.m     # Heat maps with profiles
├── data/                               # Organized data structure
│   ├── origin/                         # Raw TXT files
│   ├── csv/                           # Converted CSV files
│   ├── csv_起始点选择/                 # Start-point aligned data
│   ├── csv_起始点选择_去偏/            # Debiased and truncated data
│   ├── data.npz                       # Grid-organized data
│   └── data.mat                       # MATLAB-compatible output
├── datasets/                          # Archive of experimental datasets
├── logs/                              # Processing logs
└── requirements.txt                   # Python dependencies
```

## Data Processing Workflow

### Core Pipeline (Integrated)
The main notebook (`main.ipynb`) executes this complete workflow:

1. **TXT → CSV Conversion** (`convert_txt_to_csv`)
   - Parse raw measurement files with metadata extraction
   - Handle various file formats and encoding

2. **Start Point Selection** (`select_start_indices`) 
   - Interactive GUI with dual-signal display (Vg + measurement)
   - Configurable Vg delay compensation (default: 2.5ms)
   - Advanced zoom/pan controls for precise alignment

3. **Debiasing Processing** (`apply_debiasing`)
   - Offset correction to zero baseline 
   - Optional truncation to minimum common length
   - Handles missing data gracefully

4. **Grid Organization** (`convert_csv_to_npz_file`)
   - Spatial arrangement of time series (e.g., 4×6 grid)
   - Time synchronization and interpolation
   - Memory-efficient processing with progress tracking

5. **MATLAB Export** (`convert_npz_to_mat_file`)
   - Full metadata preservation
   - Compatible data structures for MATLAB visualization

### Key Processing Features
- **Unified Error Handling**: Each step returns standardized success/error information
- **Progress Tracking**: Real-time logging with loguru integration
- **Memory Management**: Efficient processing for large datasets
- **Configuration Flexibility**: All parameters easily adjustable

## Advanced Features

### Interactive Start Point Selection
The GUI interface provides:

- **Dual-Signal Display**: Synchronized visualization of Vg voltage and measurement signals
- **Hardware Delay Compensation**: 
  - Default 2.5ms Vg delay for typical OECT measurements
  - Configurable range 0-10ms for different systems
  - Applied transparently during file loading
- **Advanced Navigation**:
  - Mouse wheel zoom centered on cursor position
  - Synchronized X-axis scaling between signal plots
  - Independent Y-axis scaling for each subplot
  - Shift+drag or middle-click for smooth panning
- **Keyboard Shortcuts**: 
  - 'n' to save and proceed to next file
  - 'k' to skip current file
  - 'r' to reset zoom to original view

### Debiasing and Data Preparation
- **Baseline Correction**: Automatic offset removal using first data point as reference
- **Length Normalization**: Optional truncation to ensure consistent time series lengths
- **Quality Validation**: Automatic detection of corrupted or incomplete data files

### MATLAB Integration
After processing, use the MATLAB scripts for publication-quality visualizations:

```matlab
% Load the processed data
data = load('data/data.mat');

% Generate professional visualizations
main01_3d                    % 3D surface animations with rotation
main03_heatmapwithprofile   % Heat maps with cross-sectional profiles
```

The MATLAB scripts provide:
- High-resolution 3D surface animations
- Heat maps with integrated cross-sectional profiles  
- Professional color schemes and layout optimization
- Video export capabilities with customizable parameters

## Configuration Options

### Processing Parameters
All parameters can be configured in the main notebook or through the API:

```python
# Vg Signal Alignment
vg_delay = 0.0025  # 2.5ms default for OECT measurements

# Grid Configuration
rows = 4           # Spatial grid rows
cols = 6           # Spatial grid columns

# Data Processing
truncate_to_min = True  # Normalize time series lengths
use_all_points = True   # Use full resolution vs. sampling
```

### Vg Signal Delay Examples
```python
# Standard OECT measurement system
vg_delay = 0.0025  # 2.5ms

# Pre-synchronized data
vg_delay = 0.0     # No delay compensation
```

### Grid Configuration Options
- **Standard Layout**: 4×6 (24 measurement points)
- **High-Density**: 6×6 (36 measurement points) 
- **Custom Arrangements**: Any row×column combination
- **Missing Point Handling**: Graceful handling of incomplete grids

## System Requirements

### Core Dependencies
- Python 3.7+
- NumPy, pandas, matplotlib, scipy
- loguru (logging), tqdm (progress bars)
- tkinter (GUI components)

### Optional Dependencies
- **FFmpeg**: High-quality MP4 video output (recommended)
- **MATLAB**: Enhanced visualizations (optional)

### Installation
```bash
# Clone repository
git clone <repository-url>
cd multiseries_temporal_visualizer

# Install Python dependencies
pip install -r requirements.txt

```

## Usage Examples

### Basic Pipeline Execution
```python
# Run complete pipeline with default settings
results = {}

# Execute each step with error handling
from python_dataprepare_visualize.steps import *

results["txt_to_csv"] = convert_txt_to_csv('data/origin', 'data/csv')
results["start_idx_selection"] = select_start_indices('data/csv', 'data/csv_起始点选择', vg_delay=0.0025)
results["debiasing"] = apply_debiasing('data/csv_起始点选择', 'data/csv_起始点选择_去偏')
results["csv_to_npz"] = convert_csv_to_npz_file('data/csv_起始点选择_去偏', 'data/data.npz', rows=4, cols=6)
results["npz_to_mat"] = convert_npz_to_mat_file('data/data.npz', 'data/data.mat')

# Check results
for step_name, result in results.items():
    status = "✓" if result.get("success", False) else "✗"
    print(f"{status} {step_name}: {result.get('message', 'Unknown')}")
```

### Advanced Baseline Correction
```python
# Automatic baseline correction
from python_dataprepare_visualize.steps import apply_baseline_correction

result = apply_baseline_correction(
    input_dir='data/processed',
    output_dir='data/baseline_corrected',
    mode="auto"  # or "manual" for GUI interface
)
```

## Performance Optimization

### Memory Management
- **Chunked Processing**: Large datasets processed in manageable chunks
- **Progress Monitoring**: Real-time memory usage tracking
- **Efficient Data Structures**: NumPy arrays for optimal performance

### Processing Speed
- **Optimized Algorithms**: Efficient signal processing and data organization
- **Parallel-Ready**: Designed for easy parallelization of batch processing
- **Smart Caching**: Intermediate results cached to avoid recomputation

## Troubleshooting

### Common Issues
- **Memory Errors**: Reduce grid size or enable sampling mode
- **GUI Display Issues**: Ensure proper X11 forwarding for remote sessions
- **File Format Errors**: Verify consistent file naming (11.txt, 11V.txt pattern)
- **MATLAB Integration**: Ensure compatible data structures in exported MAT files

### Performance Tips
- **Start with Notebook**: Use `main.ipynb` for initial exploration
- **Batch Processing**: Process multiple datasets using the programmatic API
- **Memory Monitoring**: Watch memory usage during large dataset processing
- **Quality vs. Speed**: Adjust sampling parameters based on requirements

For development guidance and technical details, see [CLAUDE.md](CLAUDE.md).

## Citation

If you use this software in your research, please cite:

```bibtex
@software{multiseries_temporal_visualizer,
  title={Multiseries Temporal Visualizer: OECT Swelling Signal Processing and Visualization System},
  author={[Your Name]},
  year={2025},
  url={https://github.com/your-username/multiseries_temporal_visualizer}
}
```