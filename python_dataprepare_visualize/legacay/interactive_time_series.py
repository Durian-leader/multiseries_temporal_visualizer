import os
import glob
import re
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from scipy.interpolate import interp1d
import plotly.io as pio
from typing import List, Tuple, Optional, Union, Callable
import json

# Set template for scientific appearance
pio.templates.default = "plotly_white"

class InteractiveTimeSeriesPlot:
    """
    Creates an interactive visualization of time series data using Plotly.
    
    Features:
    - Interactive timeline slider to explore data at different time points
    - Play/pause animation button for automatic playback
    - Multiple visualization modes: heatmap grid, 3D surface, contour
    - Hover information showing exact values
    - Automatically synchronizes multiple time series with different sampling rates
    - Can be exported as HTML for sharing or embedding
    """
    
    def __init__(self, 
                 input_folder: str = None,
                 file_paths_grid: List[List[str]] = None, 
                 rows: int = None,
                 cols: int = None,
                 colorscale: str = 'Viridis',
                 fps: int = 30,
                 sampling_points: int = 500):
        """
        Initialize the interactive time series visualization.
        
        Args:
            input_folder: Path to folder containing CSV files (optional)
            file_paths_grid: 2D list of file paths (will override input_folder if provided)
            rows: Number of rows for grid when using input_folder
            cols: Number of columns for grid when using input_folder
            colorscale: Plotly colorscale name
            fps: Frames per second for animation playback
            sampling_points: Number of time points to sample for synchronization
        """
        self.colorscale = colorscale
        self.fps = fps
        self.sampling_points = sampling_points
        
        # Data containers
        self.data = {}
        self.grid_data = None
        self.time_points = None
        self.min_signal = float('inf')
        self.max_signal = float('-inf')
        self.min_time = float('inf')
        self.max_time = float('-inf')
        
        # Create file grid from folder if provided, otherwise use the grid provided
        if input_folder and (rows is not None and cols is not None):
            self.file_paths_grid = self._create_file_grid_from_folder(input_folder, rows, cols)
            self.rows = rows
            self.cols = cols
        elif file_paths_grid:
            self.file_paths_grid = file_paths_grid
            self.rows = len(file_paths_grid)
            self.cols = len(file_paths_grid[0]) if self.rows > 0 else 0
        else:
            raise ValueError("Must provide either input_folder with rows and cols, or file_paths_grid")
        
        # Load and synchronize data
        self._load_data()
        self._synchronize_time_points()
        
    def _create_file_grid_from_folder(self, folder_path: str, rows: int, cols: int) -> List[List[str]]:
        """Create a grid of file paths from a folder using natural sorting."""
        # Get all CSV files in the folder
        csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
        
        # Natural sort function
        def natural_sort_key(s):
            return [int(text) if text.isdigit() else text.lower() 
                    for text in re.split(r'(\d+)', os.path.basename(s))]
        
        # Sort files naturally
        csv_files.sort(key=natural_sort_key)
        
        # Initialize empty grid
        grid = [[None for _ in range(cols)] for _ in range(rows)]
        
        # Fill grid with files in row-major order
        for idx, file_path in enumerate(csv_files):
            if idx >= rows * cols:
                print(f"Warning: More files ({len(csv_files)}) than grid cells ({rows}×{cols})")
                break
                
            row = idx // cols
            col = idx % cols
            grid[row][col] = file_path
            
        return grid
        
    def _load_data(self):
        """Load data from all CSV files in the grid."""
        print("Loading data from files...")
        
        for i in range(self.rows):
            for j in range(self.cols):
                file_path = self.file_paths_grid[i][j]
                
                # Skip empty cells
                if file_path is None or not file_path:
                    continue
                
                try:
                    # Read CSV file
                    df = pd.read_csv(file_path)
                    
                    # Ensure we have at least 2 columns
                    if len(df.columns) < 2:
                        print(f"Warning: File {file_path} has fewer than 2 columns")
                        continue
                    
                    # Assume first column is time and second column is signal
                    time_col = df.columns[0]
                    signal_col = df.columns[1]
                    
                    # Convert to numeric if needed
                    df[time_col] = pd.to_numeric(df[time_col], errors='coerce')
                    df[signal_col] = pd.to_numeric(df[signal_col], errors='coerce')
                    
                    # Drop any NaN values
                    df = df.dropna(subset=[time_col, signal_col])
                    
                    # Skip if no data
                    if len(df) == 0:
                        print(f"Warning: No valid data in {file_path}")
                        continue
                    
                    # Update min/max values
                    self.min_time = min(self.min_time, df[time_col].min())
                    self.max_time = max(self.max_time, df[time_col].max())
                    self.min_signal = min(self.min_signal, df[signal_col].min())
                    self.max_signal = max(self.max_signal, df[signal_col].max())
                    
                    # Store data
                    self.data[(i, j)] = {
                        'file_path': file_path,
                        'filename': os.path.basename(file_path),
                        'time': df[time_col].values,
                        'signal': df[signal_col].values
                    }
                    
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
        
        if not self.data:
            raise ValueError("No valid data files found")
            
        print(f"Loaded data from {len(self.data)} files")
        print(f"Time range: {self.min_time:.4f} to {self.max_time:.4f}")
        print(f"Signal range: {self.min_signal:.4f} to {self.max_signal:.4f}")
    
    def _synchronize_time_points(self):
        """Create a common set of time points and interpolate all signals to these points."""
        print("Synchronizing time points...")
        
        # Create common time points
        self.time_points = np.linspace(self.min_time, self.max_time, self.sampling_points)
        
        # Pre-allocate 3D grid for data: [time, row, col]
        self.grid_data = np.full((len(self.time_points), self.rows, self.cols), np.nan)
        
        # Interpolate each signal to common time points
        for (i, j), item in self.data.items():
            # Create interpolation function (linear interpolation)
            f = interp1d(item['time'], item['signal'], 
                         bounds_error=False, fill_value=(item['signal'][0], item['signal'][-1]))
            
            # Interpolate signal to common time points
            interpolated_signal = f(self.time_points)
            
            # Store in 3D grid
            self.grid_data[:, i, j] = interpolated_signal
            
            # Also store in original data dictionary
            item['interp_signal'] = interpolated_signal
        
        print(f"Created {len(self.time_points)} synchronized time points")
    
    def create_heatmap_animation(self, output_file: str = "interactive_time_series.html", title: str = "Signal Intensity Over Time"):
        """
        Create an interactive heatmap animation with a time slider.
        
        Args:
            output_file: Path to save the interactive HTML file
            title: Title for the visualization
        """
        print("Creating interactive heatmap animation...")
        
        # Create initial empty figure
        fig = go.Figure()
        
        # Add frames for each time point
        frames = []
        for t_idx, t in enumerate(self.time_points):
            # Extract 2D grid for this time point
            frame_data = self.grid_data[t_idx]
            
            # Create frame
            frames.append(
                go.Frame(
                    data=[
                        go.Heatmap(
                            z=frame_data,
                            colorscale=self.colorscale,
                            zmin=self.min_signal,
                            zmax=self.max_signal,
                            showscale=True,
                            colorbar=dict(title="Signal Value"),
                            hovertemplate="Row: %{y}<br>Column: %{x}<br>Signal: %{z:.4f}<extra></extra>"
                        )
                    ],
                    name=f"frame_{t_idx}"
                )
            )
        
        # Add base heatmap layer (first frame)
        fig.add_trace(
            go.Heatmap(
                z=self.grid_data[0],
                colorscale=self.colorscale,
                zmin=self.min_signal,
                zmax=self.max_signal,
                showscale=True,
                colorbar=dict(title="Signal Value"),
                hovertemplate="Row: %{y}<br>Column: %{x}<br>Signal: %{z:.4f}<extra></extra>"
            )
        )
        
        # Add frames to figure
        fig.frames = frames
        
        # Calculate number of slider steps and frame timing
        # Adjust to ensure slider matches animation progress properly
        total_frames = len(self.time_points)
        total_duration = total_frames / self.fps  # Total animation duration in seconds
        frame_duration = 1000 / self.fps  # Duration of each frame in milliseconds
        
        # Calculate slider steps based on total frames
        max_steps = 20  # Maximum number of steps to display on slider
        step_size = max(1, total_frames // max_steps)
        
        # Create slider steps that match frame indices exactly
        slider_steps = []
        for frame_idx in range(0, total_frames, step_size):
            # Calculate the corresponding time value for this frame
            time_val = self.time_points[frame_idx]
            
            slider_steps.append(
                dict(
                    args=[
                        [f"frame_{frame_idx}"],
                        dict(
                            frame=dict(duration=frame_duration, redraw=True),
                            mode="immediate",
                            transition=dict(duration=frame_duration)
                        )
                    ],
                    label=f"{time_val:.4f}",
                    method="animate"
                )
            )
        
        # Add special step for the last frame if not already included
        if (total_frames - 1) % step_size != 0:
            time_val = self.time_points[-1]
            slider_steps.append(
                dict(
                    args=[
                        [f"frame_{total_frames-1}"],
                        dict(
                            frame=dict(duration=frame_duration, redraw=True),
                            mode="immediate",
                            transition=dict(duration=frame_duration)
                        )
                    ],
                    label=f"{time_val:.4f}",
                    method="animate"
                )
            )
        
        # Set up slider
        sliders = [
            dict(
                active=0,
                yanchor="top",
                xanchor="left",
                currentvalue=dict(
                    font=dict(size=16),
                    prefix="Time: ",
                    suffix="",
                    visible=True,
                    xanchor="right"
                ),
                transition=dict(duration=frame_duration, easing="cubic-in-out"),
                pad=dict(b=10, t=50),
                len=0.9,
                x=0.1,
                y=0,
                steps=slider_steps
            )
        ]
        
        # Set up play button with proper timing
        updatemenus = [
            dict(
                type="buttons",
                showactive=False,
                y=0,
                x=0.1,
                xanchor="right",
                yanchor="top",
                pad=dict(t=0, r=10),
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[
                            None,
                            dict(
                                frame=dict(duration=frame_duration, redraw=True),
                                fromcurrent=True,
                                transition=dict(duration=frame_duration, easing="quadratic-in-out")
                            )
                        ]
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[
                            [None],  # Explicitly pause by showing no frames
                            dict(
                                frame=dict(duration=0, redraw=False),
                                mode="immediate",
                                transition=dict(duration=0)
                            )
                        ]
                    ),
                    dict(
                        label="Replay",
                        method="animate",
                        args=[
                            ["frame_0"],  # Start from the first frame
                            dict(
                                frame=dict(duration=frame_duration, redraw=True),
                                mode="immediate",
                                transition=dict(duration=0),
                                # After jumping to first frame, continue animation
                                after=[
                                    None,
                                    dict(
                                        frame=dict(duration=frame_duration, redraw=True),
                                        fromcurrent=True,
                                        transition=dict(duration=frame_duration, easing="quadratic-in-out")
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
        
        # Calculate figure dimensions to ensure square cells
        # Make sure the aspect ratio is maintained for square cells
        cell_size = 50  # Base size for each cell in pixels
        fig_width = max(600, cell_size * self.cols + 150)  # Add margin for colorbar
        fig_height = max(500, cell_size * self.rows + 150)  # Add margin for title and slider
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                xanchor="center"
            ),
            sliders=sliders,
            updatemenus=updatemenus,
            xaxis=dict(
                title="Column",
                range=[-0.5, self.cols-0.5],
                dtick=1,
                side="bottom",
                constrain="domain"  # Constrain to make cells square
            ),
            yaxis=dict(
                title="Row",
                range=[self.rows-0.5, -0.5],  # Reversed to match matrix convention (0,0 at top-left)
                dtick=1,
                side="left",
                scaleanchor="x",  # Make y-axis scale match x-axis for square cells
                scaleratio=1      # 1:1 aspect ratio
            ),
            height=fig_height,
            width=fig_width,
            margin=dict(l=50, r=50, b=100, t=100, pad=4),
            plot_bgcolor='white',
            hovermode='closest'
        )
        
        # Save as HTML with autoplay disabled
        fig.write_html(
            output_file,
            include_plotlyjs='cdn',  # Use CDN for smaller file size
            config={
                'displayModeBar': True,
                'responsive': True,
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': 'time_series_plot',
                    'height': 800,
                    'width': 1200,
                    'scale': 2  # Higher resolution
                }
            },
            auto_play=False  # Disable autoplay
        )
        
        print(f"Interactive heatmap animation saved to {output_file}")
        return fig
    
    def create_3d_surface(self, output_file: str = "3d_surface.html", title: str = "3D Signal Surface"):
        """
        Create an interactive 3D surface plot with a time slider.
        
        Args:
            output_file: Path to save the interactive HTML file
            title: Title for the visualization
        """
        print("Creating 3D surface visualization...")
        
        # Create initial empty figure
        fig = go.Figure()
        
        # Add frames for each time point
        frames = []
        for t_idx, t in enumerate(self.time_points):
            # Extract 2D grid for this time point
            frame_data = self.grid_data[t_idx]
            
            # Create coordinate grids
            x = np.arange(0, self.cols, 1)
            y = np.arange(0, self.rows, 1)
            
            # Create frame
            frames.append(
                go.Frame(
                    data=[
                        go.Surface(
                            x=x,
                            y=y,
                            z=frame_data,
                            colorscale=self.colorscale,
                            cmin=self.min_signal,
                            cmax=self.max_signal,
                            contours_z=dict(
                                show=True,
                                usecolormap=True,
                                highlightcolor="limegreen",
                                project_z=True
                            ),
                            hovertemplate="Column: %{x}<br>Row: %{y}<br>Signal: %{z:.4f}<extra></extra>"
                        )
                    ],
                    name=f"frame_{t_idx}"
                )
            )
        
        # Add base surface layer (first frame)
        x = np.arange(0, self.cols, 1)
        y = np.arange(0, self.rows, 1)
        
        fig.add_trace(
            go.Surface(
                x=x,
                y=y,
                z=self.grid_data[0],
                colorscale=self.colorscale,
                cmin=self.min_signal,
                cmax=self.max_signal,
                contours_z=dict(
                    show=True,
                    usecolormap=True,
                    highlightcolor="limegreen",
                    project_z=True
                ),
                hovertemplate="Column: %{x}<br>Row: %{y}<br>Signal: %{z:.4f}<extra></extra>"
            )
        )
        
        # Add frames to figure
        fig.frames = frames
        
        # Calculate number of slider steps and frame timing
        # Adjust to ensure slider matches animation progress properly
        total_frames = len(self.time_points)
        total_duration = total_frames / self.fps  # Total animation duration in seconds
        frame_duration = 1000 / self.fps  # Duration of each frame in milliseconds
        
        # Calculate slider steps based on total frames
        max_steps = 20  # Maximum number of steps to display on slider
        step_size = max(1, total_frames // max_steps)
        
        # Create slider steps that match frame indices exactly
        slider_steps = []
        for frame_idx in range(0, total_frames, step_size):
            # Calculate the corresponding time value for this frame
            time_val = self.time_points[frame_idx]
            
            slider_steps.append(
                dict(
                    args=[
                        [f"frame_{frame_idx}"],
                        dict(
                            frame=dict(duration=frame_duration, redraw=True),
                            mode="immediate",
                            transition=dict(duration=frame_duration)
                        )
                    ],
                    label=f"{time_val:.4f}",
                    method="animate"
                )
            )
        
        # Add special step for the last frame if not already included
        if (total_frames - 1) % step_size != 0:
            time_val = self.time_points[-1]
            slider_steps.append(
                dict(
                    args=[
                        [f"frame_{total_frames-1}"],
                        dict(
                            frame=dict(duration=frame_duration, redraw=True),
                            mode="immediate",
                            transition=dict(duration=frame_duration)
                        )
                    ],
                    label=f"{time_val:.4f}",
                    method="animate"
                )
            )
        
        # Set up slider
        sliders = [
            dict(
                active=0,
                yanchor="top",
                xanchor="left",
                currentvalue=dict(
                    font=dict(size=16),
                    prefix="Time: ",
                    suffix="",
                    visible=True,
                    xanchor="right"
                ),
                transition=dict(duration=frame_duration, easing="cubic-in-out"),
                pad=dict(b=10, t=50),
                len=0.9,
                x=0.1,
                y=0,
                steps=slider_steps
            )
        ]
        
        # Set up play button with proper timing
        updatemenus = [
            dict(
                type="buttons",
                showactive=False,
                y=0,
                x=0.1,
                xanchor="right",
                yanchor="top",
                pad=dict(t=0, r=10),
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[
                            None,
                            dict(
                                frame=dict(duration=frame_duration, redraw=True),
                                fromcurrent=True,
                                transition=dict(duration=frame_duration, easing="quadratic-in-out")
                            )
                        ]
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[
                            [None],  # Explicitly pause by showing no frames
                            dict(
                                frame=dict(duration=0, redraw=False),
                                mode="immediate",
                                transition=dict(duration=0)
                            )
                        ]
                    ),
                    dict(
                        label="Replay",
                        method="animate",
                        args=[
                            ["frame_0"],  # Start from the first frame
                            dict(
                                frame=dict(duration=frame_duration, redraw=True),
                                mode="immediate",
                                transition=dict(duration=0),
                                # After jumping to first frame, continue animation
                                after=[
                                    None,
                                    dict(
                                        frame=dict(duration=frame_duration, redraw=True),
                                        fromcurrent=True,
                                        transition=dict(duration=frame_duration, easing="quadratic-in-out")
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
        
        # Calculate figure dimensions to ensure square cells
        # Make sure the aspect ratio is maintained for square cells
        cell_size = 50  # Base size for each cell in pixels
        fig_width = max(600, cell_size * self.cols + 150)  # Add margin for colorbar
        fig_height = max(500, cell_size * self.rows + 150)  # Add margin for title and slider
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                xanchor="center"
            ),
            sliders=sliders,
            updatemenus=updatemenus,
            scene=dict(
                xaxis_title='Column',
                yaxis_title='Row',
                zaxis_title='Signal Value',
                xaxis=dict(range=[0, self.cols-1], dtick=1),
                yaxis=dict(range=[0, self.rows-1], dtick=1),
                zaxis=dict(range=[self.min_signal, self.max_signal]),
                aspectmode='cube',  # Force equal aspect ratio in all directions
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            height=fig_height,
            width=fig_width,
            margin=dict(l=50, r=50, b=100, t=100, pad=4)
        )
        
        # Save as HTML with autoplay disabled
        fig.write_html(
            output_file,
            include_plotlyjs='cdn',
            config={
                'displayModeBar': True,
                'responsive': True,
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': '3d_surface_plot',
                    'height': 800,
                    'width': 1200,
                    'scale': 2
                }
            },
            auto_play=False  # Disable autoplay
        )
        
        print(f"Interactive 3D surface saved to {output_file}")
        return fig
    
    def create_time_series_grid(self, output_file: str = "time_series_grid.html", title: str = "Time Series Grid"):
        """
        Create a grid of individual time series plots, one for each position.
        
        Args:
            output_file: Path to save the interactive HTML file
            title: Title for the visualization
        """
        print("Creating time series grid visualization...")
        
        # Create subplots
        fig = make_subplots(
            rows=self.rows, 
            cols=self.cols,
            shared_xaxes=True,
            shared_yaxes=True,
            subplot_titles=[f"({i},{j})" for i in range(self.rows) for j in range(self.cols)],
            horizontal_spacing=0.02,
            vertical_spacing=0.05
        )
        
        # Add time series to each subplot
        for (i, j), item in self.data.items():
            fig.add_trace(
                go.Scatter(
                    x=self.time_points,
                    y=item['interp_signal'],
                    mode='lines',
                    line=dict(
                        color=px.colors.sample_colorscale(
                            self.colorscale, 
                            (i * self.cols + j) / (self.rows * self.cols)
                        )[0],
                        width=2
                    ),
                    hovertemplate="Time: %{x:.4f}<br>Signal: %{y:.4f}<extra></extra>"
                ),
                row=i+1, 
                col=j+1
            )
        
        # Calculate figure dimensions for consistent cell size
        cell_width = 250  # Width per cell in pixels
        cell_height = 250  # Height per cell in pixels
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                xanchor="center"
            ),
            height=cell_height * self.rows,
            width=cell_width * self.cols,
            showlegend=False,
            plot_bgcolor='white',
            hovermode='closest'
        )
        
        # Update axes
        fig.update_xaxes(
            title_text="Time",
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        )
        
        fig.update_yaxes(
            title_text="Signal",
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        )
        
        # Save as HTML
        fig.write_html(
            output_file,
            include_plotlyjs='cdn',
            config={
                'displayModeBar': True,
                'responsive': True,
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': 'time_series_grid',
                    'height': 1200,
                    'width': 1200,
                    'scale': 2
                }
            }
        )
        
        print(f"Time series grid saved to {output_file}")
        return fig
    
    def create_all_visualizations(self, output_folder: str = "./visualizations"):
        """
        Create all visualization types and save to specified folder.
        
        Args:
            output_folder: Folder to save the HTML files
        """
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Create each visualization type
        self.create_heatmap_animation(os.path.join(output_folder, "heatmap_animation.html"))
        self.create_3d_surface(os.path.join(output_folder, "3d_surface.html"))
        self.create_time_series_grid(os.path.join(output_folder, "time_series_grid.html"))
        
        # Create index.html to link to all visualizations
        index_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Time Series Visualizations</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                h1 {{ color: #333; }}
                .container {{ display: flex; flex-wrap: wrap; gap: 20px; }}
                .viz-card {{ 
                    border: 1px solid #ddd; 
                    border-radius: 8px;
                    padding: 20px;
                    width: 300px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }}
                .viz-card h2 {{ margin-top: 0; }}
                .viz-card p {{ color: #666; }}
                .viz-card a {{ 
                    display: inline-block;
                    background: #4CAF50;
                    color: white;
                    padding: 10px 15px;
                    text-decoration: none;
                    border-radius: 4px;
                    margin-top: 10px;
                }}
                .viz-card a:hover {{ background: #45a049; }}
            </style>
        </head>
        <body>
            <h1>Time Series Visualizations</h1>
            <div class="container">
                <div class="viz-card">
                    <h2>Heatmap Animation</h2>
                    <p>Interactive animation showing how signal values change over time in a heatmap grid.</p>
                    <a href="heatmap_animation.html" target="_blank">View Visualization</a>
                </div>
                <div class="viz-card">
                    <h2>3D Surface</h2>
                    <p>3D surface visualization of signal values that changes over time, with interactive rotation and zoom.</p>
                    <a href="3d_surface.html" target="_blank">View Visualization</a>
                </div>
                <div class="viz-card">
                    <h2>Time Series Grid</h2>
                    <p>Grid of individual time series plots showing signal values over time for each position.</p>
                    <a href="time_series_grid.html" target="_blank">View Visualization</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(os.path.join(output_folder, "index.html"), "w") as f:
            f.write(index_html)
        
        print(f"All visualizations created in {output_folder}")
        print(f"Open {os.path.join(output_folder, 'index.html')} to view all visualizations")


# Example usage
if __name__ == "__main__":
    # Check if plotly is installed
    try:
        import plotly
        print(f"Using Plotly version {plotly.__version__}")
    except ImportError:
        print("Plotly is not installed. Please install it with: pip install plotly")
        exit(1)
        
    # Create interactive visualizations
    interactive_plot = InteractiveTimeSeriesPlot(
        input_folder="./data_csv_normalized",  # Folder containing CSV files
        rows=6,                     # Number of rows in the grid
        cols=6,                     # Number of columns in the grid
        colorscale='Viridis',       # Colorscale for visualizations
        fps=10,                     # Frames per second for animations
        sampling_points=500         # Number of time points to sample
    )
    
    # Create all visualizations
    interactive_plot.create_all_visualizations("./visualizations")
    
    print("Done! Open ./visualizations/index.html in a web browser to view the visualizations.") 