# Multiseries Temporal Visualizer

A comprehensive Python toolkit for processing, analyzing, and visualizing multi-series temporal data. This tool specializes in transforming vibration data or other time-series datasets into high-quality visualizations and animations.

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
├── utils/                      # Core utility modules
│   ├── dataprocess/            # Data processing utilities
│   │   ├── vibration_data_loader.py    # Raw data loading and conversion
│   │   ├── start_idx_visualized_select.py  # Interactive starting point selection
│   │   └── debiasing.py        # Data normalization and debiasing
│   └── visualize/              # Visualization utilities
│       ├── data_processor.py   # Data synchronization and interpolation
│       └── visualization_generator.py  # Generate visualizations and animations
├── input/                      # Input data directory 
│   └── data/                   # Raw data files
├── output/                     # Output directory structure
│   ├── data_csv/               # Converted CSV files
│   ├── data_csv_start-idx-reselected/  # Files with selected starting points
│   └── videos/                 # Generated videos and visualizations
├── extract_timepoint.py        # Extract data at specific time points
└── INSTALLATION.md             # Detailed installation instructions
```

## Data Processing Workflow

### 1. Data Loading and Conversion

Convert raw TXT files to CSV format:

```python
from utils.dataprocess.vibration_data_loader import VibrationDataLoader

# Convert all TXT files in a folder to CSV
VibrationDataLoader.convert_txt_to_csv_batch(
    "./input/data",  # Input folder with TXT files
    "./output/data_csv"  # Output folder for CSV files
)
```

### 2. Interactive Data Start Point Selection

Select the starting point for each data file using an interactive interface:

```python
from utils.dataprocess.start_idx_visualized_select import StartIdxVisualizedSelect

processor = StartIdxVisualizedSelect(
    "./output/data_csv",  # Input folder with CSV files
    "./output/data_csv_start-idx-reselected"  # Output folder for processed files
)
processor.run()
```

Use the interface:
- Click anywhere on the chart to select a starting point (shown as a red dashed line)
- Click "Save & Next" (or press 'n') to save and move to the next file
- Click "Skip File" (or press 'k') to skip the current file

### 3. Data Debiasing

Normalize the data by setting the first value of each series to zero:

```python
from utils.dataprocess.debiasing import debias_csv_folder

debias_csv_folder(
    "./output/data_csv_start-idx-reselected",  # Input folder with selected start points 
    "./output/data_csv_start-idx-reselected_debiased",  # Output folder for debiased data
    truncate_to_min=True  # Truncate all files to the length of the shortest file
)
```

### 4. Data Grid Processing and Synchronization

Organize multiple CSV files into a grid structure and synchronize their time points:

```python
from utils.visualize.data_processor import DataProcessor

# Create a data processor with a 6x6 grid
processor = DataProcessor(
    input_folder="./output/data_csv_start-idx-reselected_debiased",
    rows=6,
    cols=6,
    sampling_points=500  # Number of sampling points
)

# Save the processed data for later use
processor.save_processed_data("my_processed_data.npz")
```

### 5. Visualization Generation

Create high-quality visualizations using the processed data:

```python
from utils.visualize.visualization_generator import VisualizationGenerator

# Get the processed data
processed_data = processor.get_processed_data()

# Create visualization generator
viz_gen = VisualizationGenerator(
    processed_data=processed_data,
    colormap="viridis",  # Color mapping
    output_folder="./output/videos"  # Output folder
)

# Generate all types of videos
viz_gen.generate_all_videos()

# Generate a heatmap at a specific time point
middle_time = (processed_data['min_time'] + processed_data['max_time']) / 2
viz_gen.generate_heatmap_at_time(
    target_time=middle_time,
    output_file="heatmap.png",
    title="Signal Intensity Heatmap"
)
```

### 6. Extracting Data at Specific Time Points

Extract and visualize data at a specific time point:

```python
from extract_timepoint import extract_timepoint_data, visualize_grid

# Extract data at a specific time point
time_point, data_grid, metadata = extract_timepoint_data(
    "my_processed_data.npz",
    target_time=1.5  # Target time point
)

# Visualize the extracted data
fig = visualize_grid(
    time_point,
    data_grid,
    title="Data at t=1.5",
    filename_grid=metadata.get('filename_grid'),
    show_filenames=True
)
```

## Available Visualization Types

1. **Heatmap Videos**: Show intensity changes over time as a 2D color map
   ```python
   viz_gen.generate_heatmap_video(output_file="heatmap.mp4", title="Signal Intensity Heatmap")
   ```

2. **3D Surface Videos**: Display data as a 3D surface with optional rotation
   ```python
   viz_gen.generate_3d_surface_video(
       output_file="3d_surface.mp4",
       title="3D Signal Surface",
       rotate_view=True,
       initial_elev=30,
       initial_azim=45
   )
   ```

3. **Heatmap with Cross-Sectional Profiles**: Combined visualization showing heatmap and profile lines
   ```python
   viz_gen.generate_heatmap_with_profiles_video(
       output_file="heatmap_with_profiles.mp4",
       title="Heatmap with Signal Profiles"
   )
   ```

4. **Static Visualizations**: Generate static images at specific time points
   ```python
   viz_gen.generate_heatmap_at_time(target_time=1.5, output_file="heatmap_t1.5.png")
   viz_gen.generate_3d_surface_at_time(target_time=1.5, output_file="surface_t1.5.png")
   ```

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
- tqdm
- loguru
- FFmpeg (for video generation)

For detailed installation instructions, see [INSTALLATION.md](INSTALLATION.md).