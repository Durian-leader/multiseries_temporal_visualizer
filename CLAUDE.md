# CLAUDE.md

This file provides comprehensive guidance for Claude Code when working with the Multiseries Temporal Visualizer codebase.

## Project Overview

This is a multiseries temporal data visualization toolkit focused on processing and visualizing time-series data from scientific experiments, particularly for OECT (Organic Electrochemical Transistor) swelling measurements in materials science. The project provides both Python and MATLAB implementations with a unified, integrated processing pipeline.

## Architecture Overview

### Core Components

1. **Integrated Pipeline** (`main.ipynb` + `steps.py`)
   - Primary user interface through Jupyter notebook
   - Unified API functions for all processing steps
   - Automatic error handling and progress tracking
   - Sequential step execution with validation

2. **Data Processing Pipeline** (`python_dataprepare_visualize/`)
   - Raw data loading and conversion (TXT → CSV)
   - Interactive start point selection with Vg signal support
   - Debiasing and truncation processing
   - Grid organization and format conversion (CSV → NPZ → MAT)

3. **Visualization System** (`utils/visualize/`)
   - High-quality video generation (heatmaps, 3D surfaces)
   - Static visualization and data extraction
   - Cross-platform color mapping and font handling

4. **Interactive Tools** (`utils/dataprocess/`)
   - GUI-based start point selection with Vg signal support
   - Interactive baseline correction with dual-mode operation
   - Real-time preview and validation

5. **MATLAB Integration** (`matlab_数据可视化_比python精美/`)
   - Professional-grade 3D visualizations
   - Enhanced plotting capabilities
   - Cross-platform data compatibility

### Key Data Flow

```
Raw TXT Files → CSV (converted) → CSV (aligned) → CSV (debiased) → NPZ (grid) → MAT (MATLAB) → Visualizations
     ↓              ↓                ↓               ↓              ↓            ↓              ↓
  Metadata      File Loading    Start Point    Baseline Corr.  Time Sync.   3D Arrays    Videos/Images
   Parsing         GUI           Selection        & Truncate     Grid Org.                  & Plots
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
python -c "import numpy, pandas, matplotlib, scipy, loguru, tqdm; print('✓ Ready for development')"
```

### Core Development Workflow

#### Method 1: Integrated Jupyter Notebook (Primary Interface)
```bash
# Use the integrated Jupyter notebook for complete pipeline
jupyter notebook main.ipynb
# OR
jupyter lab main.ipynb
```

**Features of main.ipynb:**
- Complete sequential pipeline execution
- Real-time progress tracking with comprehensive logging
- Automatic error handling and recovery mechanisms
- Data validation at each processing step
- Built-in result summary reporting
- Configurable parameters through notebook cells
- Memory usage monitoring and optimization

#### Method 2: Programmatic API (Advanced Users)
```python
# Import the unified API
from python_dataprepare_visualize.steps import *

# Execute complete pipeline programmatically
results = {}

# Step 1: TXT to CSV conversion
results["txt_to_csv"] = convert_txt_to_csv('data/origin', 'data/csv')

# Step 2: Interactive start point selection
results["start_idx_selection"] = select_start_indices(
    'data/csv', 'data/csv_起始点选择', 
    vg_delay=0.0025  # 2.5ms Vg delay
)

# Step 3: Debiasing and truncation
results["debiasing"] = apply_debiasing(
    'data/csv_起始点选择', 'data/csv_起始点选择_去偏',
    truncate_to_min=True
)

# Step 4: CSV to NPZ conversion
results["csv_to_npz"] = convert_csv_to_npz_file(
    'data/csv_起始点选择_去偏', 'data/data.npz',
    rows=4, cols=6
)

# Step 5: NPZ to MAT conversion
results["npz_to_mat"] = convert_npz_to_mat_file(
    'data/data.npz', 'data/data.mat'
)

# Check results
for step_name, result in results.items():
    status = "✓" if result.get("success", False) else "✗"
    message = result.get("message", "Unknown status")
    print(f"{status} {step_name}: {message}")
```

#### Method 3: Individual Component Scripts (Legacy Support)
```bash
# Individual scripts for specific tasks (advanced usage)
python python_dataprepare_visualize/csv2npz.py \
  --input-folder ./data/processed \
  --output-file ./data/output.npz \
  --rows 4 --cols 6

python python_dataprepare_visualize/npz_to_mat.py \
  --input-file ./data/output.npz \
  --output-file ./data/output.mat
```

#### Optional: Baseline Correction
```bash
# Automatic baseline correction mode
python python_dataprepare_visualize/00_5_manual_baseline_correction.py \
  -i ./input/csv \
  -o ./output/baseline_corrected \
  -a -v

# Manual GUI baseline correction mode
python python_dataprepare_visualize/00_5_manual_baseline_correction.py \
  -i ./input/csv \
  -o ./output/baseline_corrected \
  -m -v
```

## Code Architecture Details

### Core Data Structures

#### 1. Unified API Response Format
```python
# Standardized response from all step functions
response = {
    "success": bool,           # Operation success status
    "input_dir/file": str,     # Input path
    "output_dir/file": str,    # Output path  
    "message": str,            # Human-readable status message
    "error": str,              # Error details (if failed)
    "files_processed": int,    # Number of files processed
    # Step-specific additional fields
}
```

#### 2. Grid Data Format
```python
# 3D numpy arrays [time, rows, cols] for spatial-temporal data
grid_data: np.ndarray  # Shape: (time_points, rows, cols)
time_points: np.ndarray  # Shape: (time_points,)
```

#### 3. Processed Data Dictionary
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

### Key Classes and Functions

#### 1. Unified API Functions (`steps.py`)

**convert_txt_to_csv()** - TXT to CSV conversion
```python
def convert_txt_to_csv(input_dir: str, output_dir: str, verbose: bool = True) -> Dict[str, Any]:
    """Convert TXT files to CSV format with metadata parsing"""
```

**select_start_indices()** - Interactive start point selection
```python
def select_start_indices(input_dir: str, output_dir: str, vg_delay: float = 0.0025, verbose: bool = True) -> Dict[str, Any]:
    """Interactive GUI for temporal alignment with Vg signal support"""
```

**apply_debiasing()** - Debiasing and truncation
```python
def apply_debiasing(input_dir: str, output_dir: str, truncate_to_min: bool = True, verbose: bool = True) -> Dict[str, Any]:
    """Apply baseline offset correction and optional truncation"""
```

**convert_csv_to_npz_file()** - CSV to NPZ conversion
```python
def convert_csv_to_npz_file(input_folder: str, output_file: str, rows: int = 4, cols: int = 6, use_all_points: bool = True, verbose: bool = True) -> Dict[str, Any]:
    """Convert CSV files to NPZ grid format"""
```

**convert_npz_to_mat_file()** - NPZ to MAT conversion
```python
def convert_npz_to_mat_file(input_file: str, output_file: str, include_metadata: bool = True, verbose: bool = True) -> Dict[str, Any]:
    """Convert NPZ to MATLAB MAT format"""
```

**run_full_pipeline()** - Complete automated pipeline
```python
def run_full_pipeline(input_txt_dir: str, output_base_dir: str = "./output", rows: int = 4, cols: int = 6, vg_delay: float = 0.0025, ...) -> Dict[str, Any]:
    """Execute complete processing pipeline with all steps"""
```

#### 2. Core Processing Classes

**VibrationDataLoader** (`vibration_data_loader.py:13-286`)
```python
loader = VibrationDataLoader.from_txt(file_path)
csv_path = loader.to_csv(output_path, include_metadata=False)
```

**StartIdxVisualizedSelect** (`start_idx_visualized_select.py:21-673`)
```python
processor = StartIdxVisualizedSelect(
    input_folder="./input/csv",
    output_folder="./output/aligned_csv",
    vg_delay=0.0025  # 2.5ms delay for Vg signal alignment
)
processor.run()
```

**DataProcessor** (`data_processor.py:21-371`)
```python
processor = DataProcessor(
    input_folder="./csv_data",
    rows=4, cols=6,
    use_all_points=True
)
processor.save_processed_data("output.npz")
```

### Processing Configuration

#### Vg Signal Handling
- **Default Delay:** `2.5ms (0.0025s)` - optimal for OECT measurement systems
- **Configuration Range:** `0-10ms` - adjustable for different measurement systems
- **Purpose:** Compensate for hardware latency between Vg signal and measurement response
- **Implementation:** Applied during file loading in GUI interface
- **Visual Feedback:** Synchronized dual-subplot display with delay information

#### Grid Organization
- **Default Size:** `4×6` grid (24 measurement points)
- **File Mapping:** Row-major order with natural sorting
- **Missing Files:** Gracefully handled with `None` placeholders
- **Flexibility:** Configurable dimensions via parameters

#### Error Handling and Logging
- **Unified Error Responses:** Consistent error reporting across all functions
- **Progress Tracking:** Real-time logging with `loguru` integration
- **Recovery Mechanisms:** Graceful handling of file format variations
- **Validation:** Data integrity checks at each processing step

## Important Implementation Details

### Integrated Pipeline Workflow

#### Main Notebook Structure (`main.ipynb`)
1. **Initialize Results Tracking**
   ```python
   results = {}
   ```

2. **Execute Sequential Steps**
   - Each step stores results in `results` dictionary
   - Automatic error checking with early termination on failure
   - Progress tracking with detailed logging

3. **Result Summary**
   ```python
   for step_name, result in results.items():
       status = "✓" if result.get("success", False) else "✗"
       message = result.get("message", "Unknown status")
       print(f"{status} {step_name}: {message}")
   ```

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

### Data Directory Structure
```
data/
├── origin/                    # Raw TXT files
├── csv/                      # Converted CSV files
├── csv_起始点选择/            # Start-point aligned data
├── csv_起始点选择_去偏/       # Debiased and truncated data
├── data.npz                  # Grid-organized NPZ data
└── data.mat                  # MATLAB-compatible output
```

## Development Guidelines

### Using the Unified API

1. **Import Pattern:**
   ```python
   from python_dataprepare_visualize.steps import *
   ```

2. **Error Handling Pattern:**
   ```python
   result = convert_txt_to_csv(input_dir, output_dir)
   if not result["success"]:
       logger.error(f"Conversion failed: {result.get('error', 'Unknown error')}")
       return result
   ```

3. **Progress Tracking:**
   ```python
   # All functions include verbose parameter for detailed logging
   result = select_start_indices(input_dir, output_dir, verbose=True)
   ```

### Adding New Processing Steps

1. **Create Function in steps.py:**
   ```python
   def new_processing_step(input_dir: str, output_dir: str, param1: type = default, verbose: bool = True) -> Dict[str, Any]:
       """New processing step with unified interface"""
       try:
           # Processing logic here
           
           if verbose:
               logger.info(f"Processing completed: {input_dir} -> {output_dir}")
           
           return {
               "success": True,
               "input_dir": input_dir,
               "output_dir": output_dir,
               "param1": param1,
               "message": "Processing completed successfully"
           }
           
       except Exception as e:
           logger.error(f"Processing failed: {str(e)}")
           return {
               "success": False,
               "error": str(e),
               "message": "Processing failed"
           }
   ```

2. **Update main.ipynb:**
   ```python
   # Add to notebook pipeline
   results["new_step"] = new_processing_step(input_dir, output_dir)
   if not results["new_step"]["success"]:
       print(results)
   ```

### Configuration Management

#### Common Parameters
```python
# Standard grid configuration
rows = 4
cols = 6

# Vg signal alignment
vg_delay = 0.0025  # 2.5ms default

# Data processing options
truncate_to_min = True
use_all_points = True
include_metadata = True
```

#### Parameter Validation
- All functions validate input parameters
- Provide meaningful error messages for invalid configurations
- Support flexible parameter types where appropriate

## Testing and Validation

### Function Testing Pattern
```python
# Test individual steps
def test_txt_to_csv():
    result = convert_txt_to_csv("test_input", "test_output")
    assert result["success"] == True
    assert "files_processed" in result

def test_pipeline_integration():
    results = run_full_pipeline("test_data", "test_output")
    assert results["pipeline"]["success"] == True
    assert all(step["success"] for step in results.values() if "success" in step)
```

### Data Validation
- **File Existence:** Check input files before processing
- **Format Validation:** Verify CSV structure and data types
- **Grid Completeness:** Validate spatial arrangement
- **Time Synchronization:** Ensure consistent time axes

## Performance Optimization

### Memory Management
```python
# Efficient processing for large datasets
def process_large_dataset(input_dir, chunk_size=100):
    """Process data in chunks to manage memory usage"""
    files = list(Path(input_dir).glob("*.csv"))
    
    for chunk in chunked(files, chunk_size):
        yield process_chunk(chunk)
```

### Progress Monitoring
```python
# Real-time progress tracking
from tqdm import tqdm
from loguru import logger

def process_with_progress(files):
    for file in tqdm(files, desc="Processing files"):
        result = process_file(file)
        logger.info(f"Processed: {file}")
```

## MATLAB Integration Details

### Data Structure Compatibility
```matlab
% Expected MAT file structure from convert_npz_to_mat_file()
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
data = load('data/data.mat');

% Run visualization scripts
main01_3d;                      % 3D surface animations
main03_heatmapwithprofile;      % Heat maps with cross-sectional profiles
```

## Best Practices Summary

1. **Use the Integrated Notebook** - Primary interface for most users
2. **Check Return Values** - Always validate success status from API functions
3. **Handle Errors Gracefully** - Implement proper error handling and logging
4. **Validate Inputs** - Check file existence and format before processing
5. **Monitor Progress** - Use verbose logging for long-running operations
6. **Maintain Data Structure** - Follow established directory organization
7. **Document Parameters** - Clearly specify all configuration options
8. **Test Incrementally** - Validate each processing step independently
9. **Optimize for Memory** - Use appropriate sampling for large datasets
10. **Leverage MATLAB** - Use MATLAB scripts for final visualization quality

## Troubleshooting Common Issues

### API Integration Problems
- **Import Errors:** Ensure `python_dataprepare_visualize` is in Python path
- **Function Not Found:** Check function name spelling in `steps.py`
- **Parameter Errors:** Validate required vs. optional parameters

### Data Processing Issues
- **File Format Errors:** Verify TXT/CSV file structure and encoding
- **Memory Issues:** Use sampling mode or reduce grid size
- **GUI Display:** Ensure proper X11 forwarding for remote sessions

### Pipeline Execution
- **Step Failures:** Check individual step error messages in results
- **Data Validation:** Verify input data integrity and file naming conventions
- **Output Issues:** Ensure proper permissions for output directories

This codebase represents a mature scientific data processing toolkit with a unified, user-friendly interface. The integration of the main notebook with the programmatic API provides flexibility for both interactive use and automated processing while maintaining consistent error handling and progress tracking throughout the pipeline.