import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import argparse
import matplotlib
import sys
from loguru import logger

# # 配置日志系统
# logger.remove()  # 移除默认处理器
# logger.add(sys.stdout, level="INFO")  # 控制台输出
# logger.add("start_idx_select.log", rotation="10 MB", level="DEBUG")  # 文件日志

# Set up the matplotlib backend explicitly
matplotlib.use('TkAgg')  # Use TkAgg backend which has good button support


class StartIdxVisualizedSelect:
    def __init__(self, input_folder, output_folder):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.current_file = None
        self.current_vg_file = None  # The Vg file used for visualization
        self.data = None  # Data from original file (for trimming)
        self.vg_data = None  # Data from Vg file (for visualization)
        self.fig = None
        self.ax = None
        self.selected_point = None
        self.line = None
        self.vertical_line = None
        self.files_to_process = []
        self.current_file_index = 0
        self.btn_next = None
        self.btn_skip = None
        
        # Find all TXT and CSV files in the input folder
        txt_files = glob.glob(os.path.join(self.input_folder, "*.txt"))
        csv_files = glob.glob(os.path.join(self.input_folder, "*.csv"))
        all_files = txt_files + csv_files
        
        # Filter to only include files that have corresponding Vg files
        # Look for pairs: original file (e.g., "11.txt") and Vg file (e.g., "11V.txt")
        self.files_to_process = []
        vg_files = set()
        
        # First, identify all Vg files
        for file_path in all_files:
            filename = os.path.basename(file_path)
            if filename.endswith('V.txt') or filename.endswith('V.csv'):
                vg_files.add(file_path)
        
        # Then, find original files that have corresponding Vg files
        for file_path in all_files:
            filename = os.path.basename(file_path)
            file_ext = os.path.splitext(filename)[1]
            
            # Skip if this is already a Vg file
            if filename.endswith('V.txt') or filename.endswith('V.csv'):
                continue
                
            # Look for corresponding Vg file
            base_name = os.path.splitext(filename)[0]
            vg_filename = base_name + 'V' + file_ext
            vg_file_path = os.path.join(self.input_folder, vg_filename)
            
            if vg_file_path in vg_files:
                self.files_to_process.append(file_path)
                logger.info(f"找到配对文件: {filename} <-> {vg_filename}")
            else:
                logger.warning(f"未找到对应的Vg文件: {filename}")
        
        logger.info(f"找到 {len(self.files_to_process)} 个有Vg配对的数据文件")
        
        # Create the output folder if it doesn't exist
        os.makedirs(self.output_folder, exist_ok=True)
        
        # Configure matplotlib to use interactive mode
        plt.ion()
    
    def read_data_file(self, file_path):
        """Read data from a file (TXT or CSV) using standard parsing"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            # If it's a CSV file, try to read it directly first
            if file_ext == '.csv':
                try:
                    data = pd.read_csv(file_path)
                    if not data.empty:
                        logger.info(f"成功读取CSV文件: {file_path}")
                        return data
                except Exception as e:
                    logger.warning(f"无法正常读取CSV文件，尝试替代方法: {e}")
            
            # Try to read as CSV with different delimiters
            for delimiter in [',', '\t', ' ']:
                try:
                    data = pd.read_csv(file_path, delimiter=delimiter, header=None)
                    if not data.empty:
                        # Check if we need to skip rows (metadata or headers)
                        if data.iloc[0].apply(lambda x: isinstance(x, str) and ':' in str(x)).any():
                            # There might be metadata with colon, try to skip these rows
                            for i in range(10):  # Try different header rows
                                try:
                                    data = pd.read_csv(file_path, delimiter=delimiter, header=i)
                                    # Check if this worked by seeing if we have numeric data
                                    if data.select_dtypes(include=[np.number]).shape[1] > 0:
                                        logger.debug(f"使用分隔符'{delimiter}'和头行{i}成功读取{file_path}")
                                        return data
                                except:
                                    continue
                        
                        # If the data looks good, return it
                        logger.debug(f"使用分隔符'{delimiter}'成功读取{file_path}")
                        
                        # Try to convert all columns to numeric
                        for col in data.columns:
                            data[col] = pd.to_numeric(data[col], errors='ignore')
                            
                        return data
                except Exception as e:
                    logger.debug(f"使用分隔符'{delimiter}'失败: {e}")
                    continue
            
            # If that fails, read as plain text
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            # Try to parse lines into numeric data
            data_rows = []
            header_row = None
            
            # Find where the data starts (after metadata)
            start_idx = 0
            for i, line in enumerate(lines):
                if ':' in line or line.startswith('#'):  # This is likely metadata or comment
                    start_idx = i + 1
                else:
                    break
            
            # Look for header row
            for i in range(start_idx, min(start_idx + 3, len(lines))):
                if i < len(lines):
                    parts = lines[i].strip().split()
                    # If this line has text parts, it's likely a header
                    if any(not self._is_number(part) for part in parts):
                        header_row = i
                        break
            
            # Skip header and process data rows
            for i in range(header_row + 1 if header_row is not None else start_idx, len(lines)):
                line = lines[i].strip()
                if not line or line.startswith('#'):
                    continue
                
                try:
                    # Try different delimiters
                    for delimiter in [',', '\t', ' ']:
                        parts = line.split(delimiter)
                        values = [float(part) for part in parts if part.strip()]
                        if values:
                            data_rows.append(values)
                            break
                except ValueError:
                    # Not a data row
                    continue
            
            if not data_rows:
                logger.warning(f"在{file_path}中未找到数值数据")
                return None
            
            # Create DataFrame from parsed data
            df = pd.DataFrame(data_rows)
            
            # Try to add column headers if available
            if header_row is not None:
                header_parts = lines[header_row].strip().split()
                if len(header_parts) == len(df.columns):
                    df.columns = header_parts
            
            logger.info(f"成功解析文本文件 {file_path}")
            return df
        
        except Exception as e:
            logger.error(f"读取文件{file_path}时出错: {e}")
            return None
    
    def _is_number(self, s):
        """Check if string can be converted to a number"""
        try:
            float(s)
            return True
        except ValueError:
            return False
    
    def on_click(self, event):
        """Handle mouse click event to select a new starting point"""
        # Allow clicks on either subplot
        if event.inaxes not in [self.ax, getattr(self, 'ax2', None)]:
            return
        
        logger.debug(f"选择了点 x={event.xdata}")
        
        # Store the exact x-coordinate of the click
        self.selected_point = event.xdata
        
        # Update the vertical lines on both subplots
        if self.vertical_line:
            self.vertical_line.remove()
        if hasattr(self, 'vertical_line2') and self.vertical_line2:
            self.vertical_line2.remove()
            
        self.vertical_line = self.ax.axvline(x=self.selected_point, color='r', linestyle='--', linewidth=2, alpha=0.8)
        if hasattr(self, 'ax2'):
            self.vertical_line2 = self.ax2.axvline(x=self.selected_point, color='r', linestyle='--', linewidth=2, alpha=0.8)
        
        # Redraw the canvas
        self.fig.canvas.draw_idle()
    
    def save_current_file(self):
        """Save the current data as CSV after trimming to the selected point"""
        if self.data is None or self.selected_point is None:
            logger.warning("没有可用的数据或选择点")
            return False
        
        # Find the closest data point to the selected x position
        # Note: We use the original data (self.data) for trimming, not the Vg data
        if isinstance(self.data, pd.DataFrame):
            # If using DataFrame with time as first column
            time_col = self.data.columns[0]
            time_array = self.data[time_col].values
            
            # Find the index of the closest time value
            closest_idx = np.abs(time_array - self.selected_point).argmin()
            logger.debug(f"选择的时间: {self.selected_point}, 最近的索引: {closest_idx} (在原始数据文件中)")
            
            # Trim the data from this index
            trimmed_data = self.data.iloc[closest_idx:]
        else:
            # If using numpy array
            # Convert to the nearest index
            idx = int(round(self.selected_point))
            trimmed_data = self.data[idx:, :]
        
        # Create output filename (always save as CSV)
        # Use the original file name, not the Vg file name
        base_name = os.path.basename(self.current_file)
        file_name_without_ext = os.path.splitext(base_name)[0]
        output_file = os.path.join(self.output_folder, file_name_without_ext + ".csv")
        
        # Save as CSV with headers
        trimmed_data.to_csv(output_file, index=False)
        logger.success(f"已保存截断数据到 {output_file} (基于Vg文件选择的起始点)")
        return True
    
    def on_next(self, event=None):
        """Process the current file and move to the next one"""
        logger.info("点击保存并下一个按钮")
        if self.selected_point is not None:
            self.save_current_file()
        
        self.process_next_file()
    
    def on_skip(self, event=None):
        """Skip the current file and move to the next one"""
        logger.info("点击跳过按钮")
        self.process_next_file()
    
    def create_buttons(self):
        """Create and set up the buttons with correct positioning"""
        # Create button axes with more space and clearer positioning
        # Adjust for dual subplot layout
        plt.subplots_adjust(bottom=0.15)  # Make room for buttons
        
        # Create button axes
        ax_next = plt.axes([0.7, 0.02, 0.2, 0.06])
        ax_skip = plt.axes([0.3, 0.02, 0.2, 0.06])
        
        # Create buttons with visible styling
        self.btn_next = Button(ax_next, 'Save & Next', color='lightblue', hovercolor='skyblue')
        self.btn_skip = Button(ax_skip, 'Skip File', color='lightgray', hovercolor='gray')
        
        # Connect button events
        self.btn_next.on_clicked(self.on_next)
        self.btn_skip.on_clicked(self.on_skip)
        
        # Add keyboard shortcuts as an alternative
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
    
    def on_key_press(self, event):
        """Handle keyboard shortcuts"""
        if event.key == 'n':
            # 'n' key for next
            self.on_next()
        elif event.key == 'k':
            # 'k' key for skip
            self.on_skip()
    
    def process_next_file(self):
        """Process the next file in the list"""
        if self.current_file_index >= len(self.files_to_process):
            if self.fig:
                plt.close(self.fig)
            logger.success("所有文件处理完成！")
            return
        
        self.current_file = self.files_to_process[self.current_file_index]
        self.current_file_index += 1
        self.selected_point = None
        
        # Generate corresponding Vg file path
        filename = os.path.basename(self.current_file)
        base_name = os.path.splitext(filename)[0]
        file_ext = os.path.splitext(filename)[1]
        vg_filename = base_name + 'V' + file_ext
        self.current_vg_file = os.path.join(self.input_folder, vg_filename)
        
        logger.info(f"正在处理文件: {self.current_file}")
        logger.info(f"对应的Vg文件: {self.current_vg_file}")
        
        # Read both the original data and the Vg data
        self.data = self.read_data_file(self.current_file)
        self.vg_data = self.read_data_file(self.current_vg_file)
        
        if self.data is None or len(self.data) == 0:
            logger.warning(f"文件 {self.current_file} 中没有有效数据，跳过...")
            self.process_next_file()
            return
            
        if self.vg_data is None or len(self.vg_data) == 0:
            logger.warning(f"Vg文件 {self.current_vg_file} 中没有有效数据，跳过...")
            self.process_next_file()
            return
        
        # Close any existing figure
        if self.fig is not None:
            plt.close(self.fig)
        
        # Create a new figure with two subplots
        self.fig, (self.ax, self.ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
        
        # Create buttons
        self.create_buttons()
        
        # Connect the mouse click event to both axes
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        # Reset vertical lines
        self.vertical_line = None
        self.vertical_line2 = None
        
        # Plot both Vg data and original data
        self._plot_both_signals()
        
        # Set titles
        self.ax.set_title(f"Vg Signal: {os.path.basename(self.current_vg_file)} (用于选择起始点)")
        self.ax2.set_title(f"Original Signal: {os.path.basename(self.current_file)} ({self.current_file_index}/{len(self.files_to_process)})")

        self.ax.grid(True)
        self.ax2.grid(True)
        
        # Show instructions
        plt.figtext(0.5, 0.08, "Click on either graph to select starting point. Red line shows selected position on both signals.", 
                   ha='center', fontsize=9)
        plt.figtext(0.5, 0.05, "Press 'n' to save & next, 'k' to skip file", 
                   ha='center', fontsize=8)
        
        # Show the plot
        self.fig.canvas.draw()
        plt.show(block=False)  # Non-blocking show
        plt.pause(0.1)  # Small pause to ensure the window shows
    
    def _plot_both_signals(self):
        """Plot both Vg data and original data on separate subplots"""
        # Plot Vg data on the first subplot (self.ax)
        if isinstance(self.vg_data, pd.DataFrame):
            time_col = self.vg_data.columns[0]
            x_values = self.vg_data[time_col]
            
            for col in self.vg_data.columns[1:]:
                try:
                    self.ax.plot(x_values, self.vg_data[col], label=f"Vg - {str(col)}", color='blue', linewidth=1.5)
                except Exception as e:
                    logger.error(f"绘制Vg列 {col} 时出错: {e}")
        else:
            x_values = self.vg_data[:, 0]
            for col in range(1, self.vg_data.shape[1]):
                self.ax.plot(x_values, self.vg_data[:, col], label=f"Vg - Column {col+1}", color='blue', linewidth=1.5)
        
        self.ax.set_ylabel("Voltage (Vg)")
        self.ax.legend()
        
        # Plot original data on the second subplot (self.ax2)
        if isinstance(self.data, pd.DataFrame):
            time_col = self.data.columns[0]
            x_values = self.data[time_col]
            
            for col in self.data.columns[1:]:
                try:
                    self.ax2.plot(x_values, self.data[col], label=str(col), color='green', linewidth=1.5)
                except Exception as e:
                    logger.error(f"绘制原始数据列 {col} 时出错: {e}")
        else:
            x_values = self.data[:, 0]
            for col in range(1, self.data.shape[1]):
                self.ax2.plot(x_values, self.data[:, col], label=f"Column {col+1}", color='green', linewidth=1.5)
        
        self.ax2.set_xlabel("Time")
        self.ax2.set_ylabel("Signal")
        self.ax2.legend()

    def _basic_plot_vg(self):
        """Plot the Vg data for visualization and start point selection"""
        # If vg_data is a DataFrame with named columns
        if isinstance(self.vg_data, pd.DataFrame):
            # Use first column as time (x-axis)
            time_col = self.vg_data.columns[0]
            x_values = self.vg_data[time_col]
            
            # Plot each remaining column against time
            for col in self.vg_data.columns[1:]:
                try:
                    self.ax.plot(x_values, self.vg_data[col], label=f"Vg - {str(col)}")
                except Exception as e:
                    logger.error(f"绘制Vg列 {col} 时出错: {e}")
        else:
            # Assume numpy array - first column is time
            x_values = self.vg_data[:, 0]
            
            # Plot each remaining column against time
            for col in range(1, self.vg_data.shape[1]):
                self.ax.plot(x_values, self.vg_data[:, col], label=f"Vg - Column {col+1}")
        
        # Set labels
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Voltage (Vg)")
        self.ax.legend()

    def _basic_plot(self):
        """Basic plotting function for when VibrationDataLoader is not available"""
        # If data is a DataFrame with named columns
        if isinstance(self.data, pd.DataFrame):
            # Use first column as time (x-axis)
            time_col = self.data.columns[0]
            x_values = self.data[time_col]
            
            # Plot each remaining column against time
            for col in self.data.columns[1:]:
                try:
                    self.ax.plot(x_values, self.data[col], label=str(col))
                except Exception as e:
                    logger.error(f"绘制列 {col} 时出错: {e}")
        else:
            # Assume numpy array - first column is time
            x_values = self.data[:, 0]
            
            # Plot each remaining column against time
            for col in range(1, self.data.shape[1]):
                self.ax.plot(x_values, self.data[:, col], label=f"Column {col+1}")
        
        # Set labels
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Signal")
        self.ax.legend()
    
    def run(self):
        """Run the main processing workflow"""
        if not self.files_to_process:
            logger.warning("在输入文件夹中未找到数据文件（TXT或CSV）。")
            return
        
        # Process the first file
        self.process_next_file()
        
        # Keep the main thread alive until all plots are closed
        logger.info("进入主循环。关闭所有图表窗口退出程序。")
        logger.info("键盘快捷键: 'n' = 保存并下一个, 'k' = 跳过")
        plt.ioff()  # Turn off interactive mode for final show
        plt.show()  # This will block until all figures are closed


if __name__ == "__main__":
    # # Set up command-line argument parsing
    # parser = argparse.ArgumentParser(description='Process data files and save trimmed data as CSV')
    # parser.add_argument('--input', '-i', type=str, required=True, help='Input folder containing TXT or CSV files')
    # parser.add_argument('--output', '-o', type=str, required=True, help='Output folder for CSV files')
    logger.configure(
        handlers=[
            {"sink": sys.stdout, "level": "INFO"},
            {"sink": "start_idx_select.log", "level": "DEBUG", "rotation": "10 MB"},
        ]
    )
    # args = parser.parse_args()
    input_folder = "./output/data_csv"
    output_folder = "./output/data_csv_start-idx-reselected"
    # Create and run the processor
    processor = StartIdxVisualizedSelect(input_folder, output_folder)
    processor.run()