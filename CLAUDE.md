# CLAUDE.md

This file provides comprehensive guidance for Claude Code when working with the Multiseries Temporal Visualizer codebase.

## Project Overview

This is a multiseries temporal data visualization toolkit focused on processing and visualizing time-series data from scientific experiments, particularly for vibration/expansion measurements in materials science. The project provides both Python and MATLAB implementations for data preprocessing and visualization.

## Architecture Overview

### Core Components

1. **Data Processing Pipeline** (`python_dataprepare_visualize/`)
   - Raw data loading and conversion (TXT → CSV)
   - Wavelet denoising and signal alignment
   - Baseline correction (automatic and manual)
   - Grid organization and format conversion (CSV → NPZ → MAT)

2. **Visualization System** (`utils/visualize/`)
   - High-quality video generation (heatmaps, 3D surfaces)
   - Static visualization and data extraction
   - Cross-platform color mapping and font handling

3. **Interactive Tools** (`utils/dataprocess/`)
   - GUI-based start point selection with Vg signal support
   - Interactive baseline correction with dual-mode operation
   - Real-time preview and validation

4. **MATLAB Integration** (`matlab_数据可视化_比python精美/`)
   - Professional-grade 3D visualizations
   - Enhanced plotting capabilities
   - Cross-platform data compatibility

### Key Data Flow

```
Raw TXT Files → CSV (aligned) → NPZ (grid) → MAT (MATLAB) → Visualizations
     ↓              ↓              ↓            ↓             ↓
  Metadata    Baseline Corr.   Time Sync.   3D Arrays    Videos/Images
```

## Development Commands

### Environment Setup
```bash
# Create development environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import numpy, pandas, matplotlib, scipy, pywt, loguru, tqdm; print('✓ Ready for development')"
```

### Core Development Workflow

#### Integrated Pipeline (Recommended for Development)
```bash
# Use the integrated Jupyter notebook for complete pipeline
jupyter notebook main.ipynb
# OR
jupyter lab main.ipynb
```

**Features of main.ipynb:**
- Real-time progress tracking with detailed logging
- Comprehensive error handling and recovery mechanisms
- Data validation at each processing step
- Built-in visualization preview and debugging
- Configurable parameters through notebook cells
- Memory usage monitoring and optimization

#### Manual Processing Pipeline (Individual Components)
```bash
# Step 1: Complete preprocessing pipeline
python python_dataprepare_visualize/00select_start_idx.py \
  --input-dir ./input/data \
  --output-dir ./output/processed_csv \
  --rows 4 --cols 6 \
  --vg-delay 0.0025 \
  --wavelet db6 --wavelet-level 6

# Step 1.5: Baseline correction (optional)
# Automatic mode
python python_dataprepare_visualize/00_5_manual_baseline_correction.py \
  -i ./output/processed_csv \
  -o ./output/baseline_corrected_csv \
  -a -v

# Manual mode with GUI
python python_dataprepare_visualize/00_5_manual_baseline_correction.py \
  -i ./output/processed_csv \
  -o ./output/baseline_corrected_csv \
  -m -v

# Step 2: CSV to NPZ conversion
python python_dataprepare_visualize/01csv2npz.py \
  --input-folder ./output/baseline_corrected_csv \
  --output-file ./output/my_processed_data.npz \
  --rows 4 --cols 6 --use-all-points

# Step 3: NPZ to MATLAB conversion
python python_dataprepare_visualize/npz_to_mat.py \
  --input-file ./output/my_processed_data.npz \
  --output-file ./my_processed_data.mat
```

#### Visualization Pipeline
```bash
# For video generation (5-point sampling)
python python_dataprepare_visualize/01sample.py
python python_dataprepare_visualize/03video.py

# For detailed analysis (all data points)
python python_dataprepare_visualize/02picture.py
```

#### Testing and Validation
```bash
# Test individual components
python python_dataprepare_visualize/04查看某个信号小波去噪前后的对比.py

# Run specific processing steps
python -c "from python_dataprepare_visualize.utils.dataprocess.vibration_data_loader import VibrationDataLoader; print('✓ Data loader test')"
```

## Code Architecture Details

### Core Data Structures

#### 1. Grid Data Format
```python
# 3D numpy arrays [time, rows, cols] for spatial-temporal data
grid_data: np.ndarray  # Shape: (time_points, rows, cols)
time_points: np.ndarray  # Shape: (time_points,)
```

#### 2. Processed Data Dictionary
```python
processed_data = {
    'grid_data': np.ndarray,      # Main 3D grid data
    'time_points': np.ndarray,    # Time axis
    'min_signal': float,          # Data range information
    'max_signal': float,
    'min_time': float,
    'max_time': float,
    'rows': int,                  # Grid dimensions
    'cols': int,
    'filename_grid': List[List[str]]  # File mapping grid
}
```

#### 3. File Path Grid
```python
# 2D array mapping spatial positions to data file paths
file_paths_grid: List[List[str]]  # Shape: (rows, cols)
# Row-major ordering: row = idx // cols, col = idx % cols
```

### Key Classes and Their Roles

#### 1. VibrationDataLoader (`vibration_data_loader.py:13-286`)
**Purpose:** Load and convert raw TXT files with metadata parsing
```python
loader = VibrationDataLoader.from_txt(file_path)
csv_path = loader.to_csv(output_path, include_metadata=False)
```

**Key Methods:**
- `from_txt()`: Parse TXT files with metadata extraction
- `to_csv()`: Export to CSV with optional metadata
- `convert_txt_to_csv_batch()`: Batch processing of TXT files

#### 2. StartIdxVisualizedSelect (`start_idx_visualized_select.py:21-673`)
**Purpose:** Interactive GUI for temporal alignment with Vg signal support and advanced zoom/pan controls
```python
processor = StartIdxVisualizedSelect(
    input_folder="./input/csv",
    output_folder="./output/aligned_csv",
    vg_delay=0.0025  # 2.5ms delay for Vg signal alignment
)
processor.run()
```

**Key Features:**
- Dual-signal display with synchronized subplots (Vg voltage + original signal)
- Visual time alignment with configurable Vg delay compensation
- **Advanced Zoom Controls:**
  - Mouse wheel zoom centered on cursor position
  - X-axis synchronized between both signal plots
  - Independent Y-axis scaling for each subplot
- **Precise Navigation:**
  - Shift+drag or middle mouse button for panning
  - Smart zoom maintains selected start point markers
  - 'r' key or Reset View button to restore original view
- Keyboard shortcuts: 'n' next, 'k' skip, 'r' reset view
- **Vg Delay Configuration:**
  - Default: 2.5ms for hardware compensation
  - Range: 0-10ms for different measurement systems
  - Applied during file loading for WYSIWYG alignment
  - Automatic detection of Vg files (ending with 'V.txt' or 'V.csv')

#### 3. DataProcessor (`data_processor.py:21-371`)
**Purpose:** Convert individual time series into synchronized grid format
```python
processor = DataProcessor(
    input_folder="./csv_data",
    rows=4, cols=6,
    use_all_points=True  # False for 500-point sampling
)
processor.save_processed_data("output.npz")
```

**Key Methods:**
- `_create_file_grid()`: Natural sorting and grid organization
- `_load_data()`: CSV loading with error handling
- `_synchronize_time_points()`: Temporal interpolation and alignment

#### 4. VisualizationGenerator (`visualization_generator.py:71-200+`)
**Purpose:** High-quality video and image generation
```python
viz_gen = VisualizationGenerator(
    processed_data=data,
    fps=30, dpi=150,
    colormap='viridis',
    vmin=None, vmax=None
)

# Generate different visualization types
viz_gen.generate_heatmap_video("heatmap.mp4")
viz_gen.generate_3d_surface_video("surface.mp4", rotate_view=True)
viz_gen.generate_heatmap_with_profiles_video("profiles.mp4")
```

### Processing Configuration

#### Wavelet Parameters
- **Default Wavelet:** `db6` (Daubechies 6)
- **Decomposition Levels:** `6`
- **Node Selection:** `['aaaaaa']` (approximate coefficients only)
- **Configurable via:** Command line args or function parameters

#### Vg Signal Handling
- **Default Delay:** `2.5ms (0.0025s)` - optimal for most measurement systems
- **Purpose:** Compensate for hardware latency between Vg signal and actual measurement response
- **Configuration Range:** `0-10ms` - adjustable for different measurement systems
- **Implementation Details:**
  - Applied during file loading in `read_data_file()` method
  - Automatic detection of Vg files (files ending with 'V.txt' or 'V.csv')
  - Time offset added to first column (time) of Vg data: `data[time_col] = data[time_col] + vg_delay`
  - Transparent operation - both signals align in time domain after loading
- **Visual Alignment:** What-you-see-is-what-you-get approach
- **Interface Feedback:**
  - Subplot titles show delay info: "Vg Signal: 11V.txt (延时2.5ms)" or "(无延时)"
  - Log messages confirm delay application: "已对Vg文件应用 2.5ms 时间偏移"
- **Usage Scenarios:**
  - Hardware delay compensation for measurement systems
  - Signal synchronization from different sensors
  - Time series alignment for cross-correlation analysis
- **Precision:** Limited by data sampling rate
- **Best Practices:** Use consistent delay settings across experiment batches

#### Grid Organization
- **Default Size:** `4×6` grid (24 measurement points)
- **File Mapping:** Row-major order with natural sorting
- **Missing Files:** Gracefully handled with `None` placeholders
- **Flexibility:** Configurable dimensions via parameters

#### Memory Management
- **All-Points Mode:** Use complete time series data
- **Sampling Mode:** Downsample to specified point count (e.g., 500)
- **Chunked Processing:** For large datasets
- **Progress Tracking:** Real-time status with `tqdm` and `loguru`

## Important Implementation Details

### Cross-Platform Font Handling
```python
# Automatic platform detection and font selection
if platform.system() == 'Windows':
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
elif platform.system() == 'Darwin':  # macOS
    plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti SC', 'STHeiti']
elif platform.system() == 'Linux':
    plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'WenQuanYi Zen Hei']
```

### Color Mapping System
```python
# Comprehensive color scheme support
CLASSIC_COLORMAPS = {
    'viridis': 'viridis',    # Default scientific
    'plasma': 'plasma',      # High contrast
    'turbo': 'turbo',        # Full spectrum
    'RdBu': 'RdBu_r',        # Diverging (reversed)
    'jet': 'jet',            # Classic rainbow
    # ... 20+ total schemes
}
```

### Video Generation Pipeline
1. **Quality Settings:** Configurable DPI (default: 150), bitrate, FPS (default: 30)
2. **Format Priority:** FFmpeg MP4 → Pillow GIF → HTML fallback
3. **Enhancement Options:** Timestamps, colorbars, custom titles
4. **View Controls:** Fixed or rotating 3D views

### Error Handling and Logging
```python
# Comprehensive logging with loguru
logger.configure(handlers=[
    {"sink": sys.stdout, "level": "INFO"},
    {"sink": "logs/processing.log", "level": "DEBUG", "rotation": "10 MB"}
])

# Error recovery mechanisms
try:
    result = processing_function()
except Exception as e:
    logger.error(f"Processing failed: {str(e)}")
    # Implement fallback or recovery
```

## Interactive Workflow Best Practices

### Start Point Selection Workflow

#### Optimal User Experience Flow
1. **Initial Overview** - Display complete signal traces for context
2. **Zoom to Critical Region** - Use mouse wheel to focus on transition areas
3. **Fine-tune Positioning** - Shift+drag to center critical points
4. **Precise Selection** - Click to select with pixel-level accuracy
5. **Verification** - Press 'r' to reset view and confirm selection
6. **Save and Continue** - Press 'n' to process and move to next file

#### Zoom and Pan Implementation Details
```python
# Mouse scroll event handler
def on_scroll(self, event):
    """Handle mouse scroll events for zooming"""
    if event.inaxes not in [self.ax, self.ax2]:
        return
    
    # Get mouse position and current limits
    xdata, ydata = event.xdata, event.ydata
    cur_xlim = self.ax.get_xlim()
    
    # Calculate zoom scale
    scale_factor = 1 / self.zoom_factor if event.button == 'up' else self.zoom_factor
    
    # Apply zoom centered on mouse position
    new_xlim = [xdata - (xdata - cur_xlim[0]) * scale_factor,
                xdata - (xdata - cur_xlim[1]) * scale_factor]
    
    # Synchronize X-axis between subplots
    self.ax.set_xlim(new_xlim)
    self.ax2.set_xlim(new_xlim)
```

#### Navigation Controls Reference
```python
# Mouse and keyboard controls mapping
CONTROL_MAPPING = {
    'left_click': 'select_start_point',
    'mouse_wheel': 'zoom_in_out',
    'shift_drag': 'pan_view',
    'middle_drag': 'pan_view_alt',
    'r_key': 'reset_view',
    'n_key': 'save_and_next',
    'k_key': 'skip_file'
}
```

#### Technical Implementation Notes
- **Synchronized X-Axis:** Both subplots share time axis for consistent navigation
- **Independent Y-Axis:** Each signal maintains its own scale for clarity
- **Smart Marker Persistence:** Selected points remain visible during zoom/pan operations
- **Event Handling Priority:** Click events distinguished from drag events using event modifiers

### Vg Signal Delay Configuration Patterns

#### Common Configuration Scenarios
```python
# Scenario 1: Standard measurement system
processor = StartIdxVisualizedSelect(
    input_folder="./data",
    output_folder="./processed",
    vg_delay=0.0025  # 2.5ms - most common hardware delay
)

# Scenario 2: High-precision system with faster response
processor = StartIdxVisualizedSelect(
    input_folder="./data",
    output_folder="./processed", 
    vg_delay=0.001  # 1ms - faster systems
)

# Scenario 3: Legacy system with slower response
processor = StartIdxVisualizedSelect(
    input_folder="./data",
    output_folder="./processed",
    vg_delay=0.005  # 5ms - slower systems
)

# Scenario 4: Pre-aligned data
processor = StartIdxVisualizedSelect(
    input_folder="./data",
    output_folder="./processed",
    vg_delay=0.0  # No delay compensation needed
)
```

#### Delay Validation and Testing
```python
# Method to validate delay setting with known test signals
def validate_vg_delay(test_file_path, expected_delay):
    """
    Test Vg delay setting using a signal with known characteristics.
    
    Args:
        test_file_path: Path to test data with known timing
        expected_delay: Expected delay in seconds
        
    Returns:
        bool: True if delay setting produces expected alignment
    """
    processor = StartIdxVisualizedSelect(
        input_folder=os.path.dirname(test_file_path),
        output_folder="./temp",
        vg_delay=expected_delay
    )
    
    # Load both signals and check alignment
    original_data = processor.read_data_file(test_file_path)
    vg_file = test_file_path.replace('.txt', 'V.txt')
    vg_data = processor.read_data_file(vg_file)
    
    # Verify alignment using cross-correlation or known features
    return check_signal_alignment(original_data, vg_data)
```

### Performance Optimization for Interactive Tools

#### Memory Management for Large Datasets
```python
# Efficient data loading for large files
def load_data_chunked(file_path, chunk_size=10000):
    """Load large CSV files in chunks to manage memory usage"""
    chunks = pd.read_csv(file_path, chunksize=chunk_size)
    return pd.concat(chunks, ignore_index=True)

# Downsampling for visualization while preserving precision
def smart_downsample(data, target_points=5000):
    """Intelligent downsampling that preserves critical features"""
    if len(data) <= target_points:
        return data
    
    # Use uniform downsampling with feature preservation
    indices = np.linspace(0, len(data)-1, target_points).astype(int)
    return data.iloc[indices]
```

#### GUI Responsiveness Optimization
```python
# Non-blocking UI updates
def update_plot_async(self):
    """Update plots without blocking user interaction"""
    self.fig.canvas.draw_idle()  # Non-blocking redraw
    plt.pause(0.001)  # Minimal pause to process events
    
# Event handling optimization
def optimize_event_handling(self):
    """Optimize event connection for better responsiveness"""
    # Disconnect/reconnect only necessary events
    self.fig.canvas.mpl_disconnect('motion_notify_event')
    # Only reconnect during active dragging
```

## Development Guidelines

### Code Style and Conventions

1. **Import Organization:**
   ```python
   # Standard library imports
   import os
   import sys
   from pathlib import Path
   
   # Third-party imports
   import numpy as np
   import pandas as pd
   import matplotlib.pyplot as plt
   
   # Local imports
   from utils.dataprocess.vibration_data_loader import VibrationDataLoader
   ```

2. **Error Handling:**
   - Use `try-except` blocks for file operations
   - Log errors with context using `loguru`
   - Provide fallback mechanisms where possible
   - Validate inputs before processing

3. **Function Documentation:**
   ```python
   def process_data(input_folder: str, output_file: str, rows: int = 4, cols: int = 6) -> Dict[str, Any]:
       """
       Process time series data into grid format.
       
       Args:
           input_folder: Path to folder containing CSV files
           output_file: Path for NPZ output file
           rows: Number of grid rows
           cols: Number of grid columns
           
       Returns:
           Dictionary containing processing results and metadata
       """
   ```

4. **Configuration Management:**
   - Use command-line arguments with `argparse`
   - Provide reasonable defaults
   - Support both programmatic and CLI usage
   - Include help text and validation

### Testing and Validation

#### Unit Testing Approach
```python
# Test data loading
def test_data_loader():
    loader = VibrationDataLoader.from_txt("test_data.txt")
    assert loader.data is not None
    assert len(loader.data) > 0

# Test processing pipeline
def test_processing_pipeline():
    processor = DataProcessor("test_input", rows=2, cols=2)
    result = processor.get_processed_data()
    assert result['grid_data'].shape == (N_time, 2, 2)
```

#### Integration Testing
```python
# Test complete workflow
def test_full_pipeline():
    # Run preprocessing
    result1 = run_preprocessing_pipeline(
        input_dir="test/input",
        output_dir="test/output"
    )
    assert result1['success']
    
    # Test visualization
    viz_gen = VisualizationGenerator(result1['data'])
    viz_gen.generate_heatmap_video("test_output.mp4")
    assert Path("test_output.mp4").exists()
```

### Performance Optimization

#### Memory Efficiency
```python
# Use generators for large datasets
def process_large_dataset(files):
    for file_batch in chunked(files, chunk_size=100):
        yield process_batch(file_batch)

# Monitor memory usage
import psutil
process = psutil.Process()
memory_mb = process.memory_info().rss / 1024 / 1024
logger.info(f"Memory usage: {memory_mb:.1f} MB")
```

#### Processing Speed
```python
# Parallel processing where appropriate
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_file, file_list))
```

## Common Development Tasks

### Adding New Visualization Types

1. **Extend VisualizationGenerator class:**
   ```python
   def generate_custom_plot(self, output_file: str, **kwargs):
       """Generate custom visualization type."""
       fig, ax = plt.subplots(figsize=(10, 8))
       # Custom plotting logic
       self._save_with_metadata(fig, output_file)
   ```

2. **Update color mapping support:**
   ```python
   # Add to CLASSIC_COLORMAPS dictionary
   CLASSIC_COLORMAPS['custom_scheme'] = 'custom_cmap'
   ```

### Adding New Data Processing Steps

1. **Create processing function:**
   ```python
   def custom_processing_step(input_data, **params):
       """Custom data processing step."""
       # Processing logic
       return processed_data
   ```

2. **Integrate into pipeline:**
   ```python
   # Add to main processing script
   if enable_custom_processing:
       result = custom_processing_step(data, **config)
   ```

### Extending File Format Support

1. **Add format detection:**
   ```python
   def detect_file_format(file_path):
       """Detect and return file format type."""
       # Format detection logic
   ```

2. **Create format-specific loader:**
   ```python
   class NewFormatLoader:
       @classmethod
       def from_file(cls, file_path):
           # Format-specific loading logic
   ```

## Troubleshooting Common Issues

### Data Loading Problems
- **Issue:** TXT files not parsing correctly
- **Solution:** Check file encoding, delimiter detection, metadata format
- **Debug:** Enable verbose logging, inspect raw file contents

### Memory Issues
- **Issue:** Out of memory during processing
- **Solutions:** 
  - Use sampling mode (`use_all_points=False`)
  - Reduce grid size
  - Process in smaller batches
  - Close unnecessary applications

### Visualization Problems
- **Issue:** FFmpeg not found
- **Solutions:**
  - Install FFmpeg and add to PATH
  - Use alternative formats (GIF, HTML)
  - Check `animation.writers.list()` for available options

### GUI Issues
- **Issue:** Interactive tools not displaying
- **Solutions:**
  - Ensure X11 forwarding for SSH
  - Install tkinter package
  - Use virtual display for headless systems (`xvfb-run`)

### Font Rendering Issues
- **Issue:** Chinese characters not displaying
- **Solutions:**
  - Install appropriate fonts for platform
  - Clear matplotlib font cache
  - Set font manually in rcParams

## Performance Monitoring

### Key Metrics to Monitor
```python
# Processing time tracking
start_time = time.time()
# ... processing ...
elapsed_time = time.time() - start_time
logger.info(f"Processing completed in {elapsed_time:.2f} seconds")

# Memory usage tracking
import psutil
memory_percent = psutil.virtual_memory().percent
logger.info(f"System memory usage: {memory_percent:.1f}%")

# File size monitoring
file_size = Path(output_file).stat().st_size
logger.info(f"Output file size: {file_size:,} bytes")
```

### Optimization Strategies
1. **Data Size Management:** Use appropriate sampling rates
2. **File I/O Optimization:** Use SSD storage, minimize file operations
3. **Memory Management:** Process in chunks, clean up temporary data
4. **Parallel Processing:** Utilize multiple cores where applicable

## MATLAB Integration Details

### Data Structure Compatibility
```matlab
% Expected MAT file structure
data.grid_data      % (time_points, rows, cols) double array
data.time_points    % (1, time_points) double array
data.min_signal     % scalar double
data.max_signal     % scalar double
data.rows          % scalar double
data.cols          % scalar double
```

### MATLAB Workflow Integration
```matlab
% Load processed data
data = load('my_processed_data.mat');

% Run visualization scripts
main01_3d;          % 3D surface animations
main02_heatmap;     % Heat map visualizations  
main03_heatmapwithprofile; % Heat maps with cross-sectional profiles
```

## Best Practices Summary

1. **Always validate inputs** before processing
2. **Use appropriate logging levels** (DEBUG for development, INFO for production)
3. **Handle missing files gracefully** with meaningful error messages
4. **Provide progress feedback** for long-running operations
5. **Support both command-line and programmatic usage**
6. **Maintain backward compatibility** when modifying interfaces
7. **Document configuration options** thoroughly
8. **Test with various data sizes and formats**
9. **Optimize for the common use case** (4×6 grid, standard processing)
10. **Provide clear error messages** with suggested solutions

## Future Development Considerations

- **Scalability:** Consider distributed processing for very large datasets
- **User Interface:** Potential web-based interface for broader accessibility
- **Data Formats:** Support for additional scientific data formats
- **Real-time Processing:** Streaming data processing capabilities
- **Cloud Integration:** Support for cloud storage and processing platforms

This codebase represents a mature scientific data processing toolkit with extensive flexibility and robust error handling. When making modifications, always consider the impact on existing workflows and maintain the high standards of documentation and testing established in the current codebase.