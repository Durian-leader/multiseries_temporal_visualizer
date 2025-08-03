import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy import interpolate
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import platform

class BaselineCorrectionTool:
    def __init__(self, root):
        self.root = root
        self.root.title("时序数据基线矫正工具")
        self.root.geometry("1100x700")
        
        # 数据变量
        self.original_data = None
        self.selected_points = []
        self.baseline_data = None
        self.corrected_data = None
        self.x_column = None
        self.y_column = None
        self.file_name = None
        
        # Zoom and pan functionality
        self.zoom_factor = 1.1
        self.original_xlim = None
        self.original_ylim_ax1 = None
        self.press_event = None
        
        # 创建UI
        self.create_widgets()
        
    def create_widgets(self):
        # 创建顶部菜单
        menu_frame = tk.Frame(self.root)
        menu_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 加载数据按钮
        load_button = tk.Button(menu_frame, text="加载CSV数据", command=self.load_csv)
        load_button.pack(side=tk.LEFT, padx=5)
        
        # 选择第一个点按钮
        self.first_point_button = tk.Button(menu_frame, text="选择第一个点", 
                                           command=self.select_first_point, state=tk.DISABLED)
        self.first_point_button.pack(side=tk.LEFT, padx=5)
        
        # 选择最后一个点按钮
        self.last_point_button = tk.Button(menu_frame, text="选择最后一个点", 
                                          command=self.select_last_point, state=tk.DISABLED)
        self.last_point_button.pack(side=tk.LEFT, padx=5)
        
        # 撤销上一个点按钮
        self.undo_button = tk.Button(menu_frame, text="撤销上一个点", 
                                    command=self.undo_last_point, state=tk.DISABLED)
        self.undo_button.pack(side=tk.LEFT, padx=5)
        
        # 重置选择按钮
        self.reset_button = tk.Button(menu_frame, text="重置选择", 
                                     command=self.reset_selection, state=tk.DISABLED)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # 重置视图按钮
        self.reset_view_button = tk.Button(menu_frame, text="重置视图", 
                                          command=self.reset_view, state=tk.DISABLED)
        self.reset_view_button.pack(side=tk.LEFT, padx=5)
        
        # 导出数据按钮
        self.export_button = tk.Button(menu_frame, text="导出矫正后的数据", 
                                      command=self.export_data, state=tk.DISABLED)
        self.export_button.pack(side=tk.LEFT, padx=5)
        
        # 状态标签
        self.status_label = tk.Label(menu_frame, text="请加载CSV文件开始")
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # 创建图表框架
        self.graph_frame = tk.Frame(self.root)
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建使用说明框架
        help_frame = tk.Frame(self.root)
        help_frame.pack(fill=tk.X, padx=10, pady=5)
        
        help_text = """使用说明:
1. 点击"加载CSV数据"按钮选择一个包含两列数据的CSV文件。
2. 在图表上点击选择基线点，或使用"选择第一个点"/"选择最后一个点"按钮。
3. 如果选择错误，可以点击"撤销上一个点"按钮删除最后添加的点。
4. 至少选择两个点后，系统会自动计算基线并显示矫正后的数据。
5. 点击"导出矫正后的数据"将结果保存为新的CSV文件。
6. 缩放: 滚轮缩放 | 平移: Shift+拖拽 | 重置视图: 点击"重置视图"按钮
        """
        help_label = tk.Label(help_frame, text=help_text, justify=tk.LEFT)
        help_label.pack(anchor=tk.W)
        
        # 初始化图表
        self.setup_plots()
    
    def setup_plots(self):
        # 创建matplotlib图表
        self.fig = plt.figure(figsize=(10, 8))
        
        # 原始数据与基线图表
        self.ax1 = self.fig.add_subplot(2, 1, 1)
        self.ax1.set_title("原始数据与基线")
        self.ax1.set_xlabel("X轴")
        self.ax1.set_ylabel("Y轴")
        self.original_line, = self.ax1.plot([], [], 'b-', label="原始数据")
        self.baseline_line, = self.ax1.plot([], [], 'orange', label="基线")
        self.points_scatter = self.ax1.scatter([], [], color='red', s=50, label="基线点")
        self.ax1.legend()
        
        # 矫正后的数据图表
        self.ax2 = self.fig.add_subplot(2, 1, 2)
        self.ax2.set_title("矫正后的数据")
        self.ax2.set_xlabel("X轴")
        self.ax2.set_ylabel("Y轴")
        self.corrected_line, = self.ax2.plot([], [], 'g-', label="矫正后的数据")
        self.ax2.legend()
        
        # 将matplotlib图表嵌入到tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 添加matplotlib工具栏
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.graph_frame)
        self.toolbar.update()
        
        # 添加图表事件
        self.fig.canvas.mpl_connect('button_press_event', self._combined_button_press)
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        
        # 调整布局
        self.fig.tight_layout()
    
    def load_csv(self):
        # 打开文件对话框
        file_path = filedialog.askopenfilename(
            title="选择CSV文件",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # 读取CSV文件
            df = pd.read_csv(file_path)
            
            # 检查是否至少有两列
            if len(df.columns) < 2:
                messagebox.showerror("错误", "CSV文件应至少包含两列数据")
                return
            
            # 获取列名
            self.x_column = df.columns[0]
            self.y_column = df.columns[1]
            
            # 保存数据
            self.original_data = df
            self.corrected_data = df.copy()
            
            # 更新文件名
            self.file_name = os.path.basename(file_path)
            
            # 清除之前的选择
            self.selected_points = []
            self.baseline_data = None
            
            # Reset view limits for new data
            self.original_xlim = None
            self.original_ylim_ax1 = None
            
            # 更新状态
            self.status_label['text'] = f"已加载: {self.file_name}"
            
            # 更新图表（会同时更新按钮状态）
            self.update_plots()
            
            # 显示消息
            messagebox.showinfo("成功", f"成功加载CSV文件: {self.file_name}")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载CSV文件时出错: {str(e)}")
    
    def _combined_button_press(self, event):
        """Combined handler for button press events"""
        # Handle selection (left click without modifiers)
        if event.button == 1 and event.key != 'shift':
            self.on_plot_click(event)
        
        # Handle panning setup (all button presses)
        self.on_press(event)
    
    def on_plot_click(self, event):
        # 确保点击在第一个图表上，且已加载数据
        if event.inaxes != self.ax1 or self.original_data is None:
            return
        
        # 获取点击的坐标
        x_click = event.xdata
        y_click = event.ydata
        
        # 找到最接近点击位置的数据点
        x_data = self.original_data[self.x_column].values
        y_data = self.original_data[self.y_column].values
        
        # 计算距离
        distances = np.sqrt((x_data - x_click)**2 + (y_data - y_click)**2)
        closest_idx = np.argmin(distances)
        
        closest_x = x_data[closest_idx]
        closest_y = y_data[closest_idx]
        
        # 检查是否已选择该点
        for i, (x, y, idx) in enumerate(self.selected_points):
            if idx == closest_idx:
                # 点已存在，删除它
                self.selected_points.pop(i)
                self.update_baseline()
                self.update_plots()
                return
        
        # 点不存在，添加它
        self.selected_points.append((closest_x, closest_y, closest_idx))
        
        # 更新基线和图表
        self.update_baseline()
        self.update_plots()
    
    def on_scroll(self, event):
        """Handle mouse scroll events for zooming"""
        if event.inaxes not in [self.ax1, self.ax2]:
            return
        
        # Get the current axis limits
        cur_xlim = self.ax1.get_xlim()
        cur_ylim_ax1 = self.ax1.get_ylim()
        cur_ylim_ax2 = self.ax2.get_ylim()
        
        # Get mouse position
        xdata = event.xdata
        ydata = event.ydata
        
        if xdata is None or ydata is None:
            return
        
        # Calculate zoom
        if event.button == 'up':
            # Zoom in
            scale_factor = 1 / self.zoom_factor
        elif event.button == 'down':
            # Zoom out
            scale_factor = self.zoom_factor
        else:
            return
        
        # Calculate new limits centered on mouse position
        new_xlim = [xdata - (xdata - cur_xlim[0]) * scale_factor,
                    xdata - (xdata - cur_xlim[1]) * scale_factor]
        
        # Apply zoom to both subplots with synchronized x-axis
        self.ax1.set_xlim(new_xlim)
        self.ax2.set_xlim(new_xlim)
        
        # For y-axis, zoom based on which subplot was scrolled on
        if event.inaxes == self.ax1:
            new_ylim_ax1 = [ydata - (ydata - cur_ylim_ax1[0]) * scale_factor,
                           ydata - (ydata - cur_ylim_ax1[1]) * scale_factor]
            self.ax1.set_ylim(new_ylim_ax1)
        elif event.inaxes == self.ax2:
            new_ylim_ax2 = [ydata - (ydata - cur_ylim_ax2[0]) * scale_factor,
                           ydata - (ydata - cur_ylim_ax2[1]) * scale_factor]
            self.ax2.set_ylim(new_ylim_ax2)
        
        self.canvas.draw_idle()
    
    def on_press(self, event):
        """Handle mouse press events for panning"""
        if event.inaxes not in [self.ax1, self.ax2]:
            return
        
        # Store the press event for panning
        self.press_event = event
    
    def on_motion(self, event):
        """Handle mouse motion events for panning"""
        if self.press_event is None or event.inaxes not in [self.ax1, self.ax2]:
            return
        
        # Only pan if middle mouse button or shift+left mouse button is pressed
        if event.button == 2 or (event.button == 1 and (event.key == 'shift')):
            # Calculate the movement
            dx = event.xdata - self.press_event.xdata
            dy = event.ydata - self.press_event.ydata
            
            if dx is None or dy is None:
                return
            
            # Get current limits
            cur_xlim = self.ax1.get_xlim()
            cur_ylim_ax1 = self.ax1.get_ylim()
            cur_ylim_ax2 = self.ax2.get_ylim()
            
            # Pan x-axis for both subplots (synchronized)
            new_xlim = [cur_xlim[0] - dx, cur_xlim[1] - dx]
            self.ax1.set_xlim(new_xlim)
            self.ax2.set_xlim(new_xlim)
            
            # Pan y-axis based on which subplot is being dragged
            if event.inaxes == self.ax1:
                new_ylim_ax1 = [cur_ylim_ax1[0] - dy, cur_ylim_ax1[1] - dy]
                self.ax1.set_ylim(new_ylim_ax1)
            elif event.inaxes == self.ax2:
                new_ylim_ax2 = [cur_ylim_ax2[0] - dy, cur_ylim_ax2[1] - dy]
                self.ax2.set_ylim(new_ylim_ax2)
            
            self.canvas.draw_idle()
    
    def on_release(self, event):
        """Handle mouse release events"""
        self.press_event = None
    
    def reset_view(self):
        """Reset view to original limits"""
        if self.original_xlim is not None:
            self.ax1.set_xlim(self.original_xlim)
            self.ax2.set_xlim(self.original_xlim)
        
        if self.original_ylim_ax1 is not None:
            self.ax1.set_ylim(self.original_ylim_ax1)
        
        # For the second subplot, auto-scale based on current data content
        # instead of using fixed original limits
        self.ax2.relim()
        self.ax2.autoscale_view()
        
        self.canvas.draw_idle()
    
    def select_first_point(self):
        if self.original_data is None:
            return
        
        # 获取第一个点
        first_idx = 0
        first_x = self.original_data[self.x_column].iloc[first_idx]
        first_y = self.original_data[self.y_column].iloc[first_idx]
        
        # 检查是否已选择
        for i, (x, y, idx) in enumerate(self.selected_points):
            if idx == first_idx:
                return  # 已选择
        
        # 添加点
        self.selected_points.append((first_x, first_y, first_idx))
        
        # 更新基线和图表
        self.update_baseline()
        self.update_plots()
    
    def select_last_point(self):
        if self.original_data is None:
            return
        
        # 获取最后一个点
        last_idx = len(self.original_data) - 1
        last_x = self.original_data[self.x_column].iloc[last_idx]
        last_y = self.original_data[self.y_column].iloc[last_idx]
        
        # 检查是否已选择
        for i, (x, y, idx) in enumerate(self.selected_points):
            if idx == last_idx:
                return  # 已选择
        
        # 添加点
        self.selected_points.append((last_x, last_y, last_idx))
        
        # 更新基线和图表
        self.update_baseline()
        self.update_plots()
    
    def undo_last_point(self):
        """撤销最后一个选择的点"""
        if self.selected_points:
            # 移除最后一个点
            self.selected_points.pop()
            
            # 更新基线和图表
            self.update_baseline()
            self.update_plots()
            
            # 更新按钮状态
            self.update_button_states()
    
    def reset_selection(self):
        self.selected_points = []
        self.baseline_data = None
        
        # 重置矫正数据为原始数据
        if self.original_data is not None:
            self.corrected_data = self.original_data.copy()
        
        # 更新图表
        self.update_plots()
        
        # 更新按钮状态
        self.update_button_states()
    
    def update_baseline(self):
        if len(self.selected_points) < 2 or self.original_data is None:
            self.baseline_data = None
            self.corrected_data = self.original_data.copy()
            return
        
        # 排序选择的点
        sorted_points = sorted(self.selected_points, key=lambda p: p[0])
        
        # 提取基线点的x和y值
        baseline_x = [p[0] for p in sorted_points]
        baseline_y = [p[1] for p in sorted_points]
        
        # 创建插值函数
        if len(sorted_points) == 2:
            # 两点时使用线性插值
            f = interpolate.interp1d(baseline_x, baseline_y, bounds_error=False, fill_value="extrapolate")
        else:
            # 多点时使用三次样条插值
            f = interpolate.PchipInterpolator(baseline_x, baseline_y)
        
        # 对每个点计算基线值
        x_data = self.original_data[self.x_column].values
        baseline_values = f(x_data)
        
        # 保存基线数据
        self.baseline_data = baseline_values
        
        # 计算矫正后的数据
        y_data = self.original_data[self.y_column].values
        corrected_values = y_data - baseline_values
        
        # 更新矫正后的数据
        self.corrected_data = self.original_data.copy()
        self.corrected_data["corrected"] = corrected_values
    
    def update_button_states(self):
        """更新按钮的启用/禁用状态"""
        if self.original_data is None:
            # 没有数据时，禁用所有操作按钮
            self.first_point_button['state'] = tk.DISABLED
            self.last_point_button['state'] = tk.DISABLED
            self.undo_button['state'] = tk.DISABLED
            self.reset_button['state'] = tk.DISABLED
            self.reset_view_button['state'] = tk.DISABLED
            self.export_button['state'] = tk.DISABLED
        else:
            # 有数据时，启用基本按钮
            self.first_point_button['state'] = tk.NORMAL
            self.last_point_button['state'] = tk.NORMAL
            self.reset_view_button['state'] = tk.NORMAL
            
            # 只有在有选择的点时才启用撤销和重置按钮
            if self.selected_points:
                self.undo_button['state'] = tk.NORMAL
                self.reset_button['state'] = tk.NORMAL
            else:
                self.undo_button['state'] = tk.DISABLED
                self.reset_button['state'] = tk.DISABLED
            
            # 只有在有矫正数据时才启用导出按钮
            if self.baseline_data is not None and len(self.selected_points) >= 2:
                self.export_button['state'] = tk.NORMAL
            else:
                self.export_button['state'] = tk.DISABLED
    
    def update_plots(self):
        if self.original_data is None:
            return
        
        # 获取数据
        x_data = self.original_data[self.x_column].values
        y_data = self.original_data[self.y_column].values
        
        # 更新原始数据线
        self.original_line.set_data(x_data, y_data)
        
        # 更新基线点
        if self.selected_points:
            x_points = [p[0] for p in self.selected_points]
            y_points = [p[1] for p in self.selected_points]
            self.points_scatter.set_offsets(np.column_stack([x_points, y_points]))
        else:
            self.points_scatter.set_offsets(np.empty((0, 2)))
        
        # 更新基线
        if self.baseline_data is not None:
            self.baseline_line.set_data(x_data, self.baseline_data)
            self.baseline_line.set_visible(True)
        else:
            self.baseline_line.set_visible(False)
        
        # 更新矫正后的数据
        if "corrected" in self.corrected_data:
            corrected_values = self.corrected_data["corrected"].values
            self.corrected_line.set_data(x_data, corrected_values)
            self.corrected_line.set_visible(True)
        else:
            self.corrected_line.set_visible(False)
        
        # 调整坐标轴
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.ax2.relim()
        self.ax2.autoscale_view()
        
        # Store original view limits for reset functionality (only when first loading data)
        if self.original_xlim is None and self.original_data is not None:
            self.original_xlim = self.ax1.get_xlim()
            self.original_ylim_ax1 = self.ax1.get_ylim()
        
        # 更新标签
        self.ax1.set_xlabel(self.x_column)
        self.ax1.set_ylabel(self.y_column)
        self.ax2.set_xlabel(self.x_column)
        self.ax2.set_ylabel(f"矫正后的{self.y_column}")
        
        # 更新状态标签
        self.status_label['text'] = f"已选择 {len(self.selected_points)} 个基线点"
        
        # 更新按钮状态
        self.update_button_states()
        
        # 重绘图表
        self.canvas.draw()
    
    def export_data(self):
        if self.corrected_data is None or not "corrected" in self.corrected_data:
            messagebox.showerror("错误", "没有可导出的矫正数据")
            return
        
        # 打开保存文件对话框
        default_name = f"矫正后_{self.file_name}" if self.file_name else "corrected_data.csv"
        file_path = filedialog.asksaveasfilename(
            title="保存矫正后的数据",
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # 导出数据
            self.corrected_data.to_csv(file_path, index=False)
            
            # 显示成功消息
            messagebox.showinfo("成功", f"矫正后的数据已保存到：\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出数据时出错: {str(e)}")

# 运行应用程序
if __name__ == "__main__":
    root = tk.Tk()
    app = BaselineCorrectionTool(root)
    root.mainloop()