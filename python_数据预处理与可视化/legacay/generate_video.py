import os
import glob
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端，避免GUI依赖
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import matplotlib.gridspec as gridspec
from typing import List, Optional, Tuple, Union, Dict
import scipy.interpolate as interp
from pathlib import Path
import argparse
import cv2
from tqdm import tqdm
import logging
import datetime
import sys


# 方法一：使用系统中已安装的中文字体
# Windows系统
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']  # 优先使用黑体、微软雅黑和宋体

# macOS系统
# plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti SC', 'STHeiti']

# Linux系统
# plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'WenQuanYi Zen Hei']

# 修复负号显示问题
plt.rcParams['axes.unicode_minus'] = False

# 经典配色方案字典
CLASSIC_COLORMAPS = {
    # 连续数据配色
    "viridis": "viridis",  # matplotlib默认 - 紫蓝青黄
    "plasma": "plasma",    # 紫红黄
    "inferno": "inferno",  # 黑紫红黄白
    "magma": "magma",      # 黑紫粉黄白
    "cividis": "cividis",  # 蓝黄(色盲友好)
    "turbo": "turbo",      # 蓝青绿黄红
    
    # 经典渐变
    "jet": "jet",          # 蓝青绿黄红
    "rainbow": "rainbow",  # 彩虹色
    "ocean": "ocean",      # 海洋蓝
    "terrain": "terrain",  # 地形色(蓝绿棕)
    
    # 高对比
    "hot": "hot",          # 黑红黄白
    "cool": "cool",        # 青到洋红
    "copper": "copper",    # 铜色系
    
    # 科学数据常用
    "RdBu": "RdBu_r",      # 红-白-蓝(反转)
    "coolwarm": "coolwarm", # 冷暖对比
    "seismic": "seismic",   # 地震图谱
    "spectral": "Spectral_r", # 光谱色
    
    # 特殊用途
    "Blues": "Blues",       # 蓝色渐变
    "Reds": "Reds",         # 红色渐变
    "Greens": "Greens",     # 绿色渐变
    "YlOrRd": "YlOrRd",     # 黄橙红渐变
    "BuPu": "BuPu",         # 蓝紫渐变
    
    # 色盲友好方案
    "cividis": "cividis",   # 蓝黄(色盲友好)
    "viridis": "viridis",   # 紫蓝青黄(色盲友好)
}

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('VideoGenerator')

class VideoGenerator:
    """
    生成高质量的时间序列数据可视化视频
    
    功能包括:
    - 高分辨率视频输出
    - 多种可视化模式 (热图、3D曲面、线图等)
    - 专业标题、时间戳和色彩映射
    - 自定义帧率和编码设置
    - 进度条和日志记录
    """
    
    def __init__(self,
                 input_folder: str,
                 rows: int,
                 cols: int,
                 fps: int = 30,
                 dpi: int = 150,
                 sampling_points: int = 500,
                 colormap: str = 'viridis',
                 custom_gradient: List[str] = None,
                 output_folder: str = './output/videos'):
        """
        初始化视频生成器
        
        Args:
            input_folder: 包含CSV文件的输入文件夹路径
            rows: 数据网格的行数
            cols: 数据网格的列数
            fps: 视频帧率
            dpi: 视频分辨率(点/英寸)
            sampling_points: 采样点数量
            colormap: matplotlib颜色映射名称或经典配色方案的键名
            custom_gradient: 自定义渐变色, 提供两个RGB或HEX色号
            output_folder: 视频输出文件夹
        """
        self.input_folder = input_folder
        self.rows = rows
        self.cols = cols
        self.fps = fps
        self.dpi = dpi
        self.sampling_points = sampling_points
        self.output_folder = output_folder
        
        # 设置色彩映射
        self.colormap = self._setup_colormap(colormap, custom_gradient)
        
        # 确保输出文件夹存在
        os.makedirs(output_folder, exist_ok=True)
        
        # 数据容器
        self.file_paths_grid = None
        self.data = {}
        self.grid_data = None
        self.time_points = None
        self.min_signal = float('inf')
        self.max_signal = float('-inf')
        self.min_time = float('inf')
        self.max_time = float('-inf')
        
        # 初始化数据
        logger.info("初始化VideoGenerator...")
        self._create_file_grid()
        self._load_data()
        self._synchronize_time_points()
    
    def _setup_colormap(self, colormap: str, custom_gradient: List[str] = None) -> str:
        """
        设置颜色映射，支持自定义渐变和预定义的经典配色方案
        
        Args:
            colormap: 颜色映射名称或预定义配色方案名称
            custom_gradient: 自定义渐变色，提供两个颜色值
        
        Returns:
            str: 实际使用的matplotlib颜色映射名称
        """
        if custom_gradient and len(custom_gradient) == 2:
            try:
                # 创建自定义线性渐变色映射
                from matplotlib.colors import LinearSegmentedColormap, to_rgb
                
                # 转换颜色值为RGB
                colors = [to_rgb(color) for color in custom_gradient]
                
                # 创建自定义色彩映射
                custom_cmap = LinearSegmentedColormap.from_list('custom_gradient', colors, N=256)
                
                # 注册色彩映射以便后续使用
                plt.register_cmap(name='custom_gradient', cmap=custom_cmap)
                
                logger.info(f"已创建自定义渐变色映射: {custom_gradient[0]} -> {custom_gradient[1]}")
                return 'custom_gradient'
                
            except Exception as e:
                logger.warning(f"创建自定义渐变色失败: {e}，将使用默认色彩映射")
                return 'viridis'
        
        # 使用经典配色方案
        if colormap in CLASSIC_COLORMAPS:
            cmap_name = CLASSIC_COLORMAPS[colormap]
            logger.info(f"使用经典配色方案: {colormap} -> {cmap_name}")
            return cmap_name
        
        # 直接使用matplotlib内置色彩映射
        logger.info(f"使用色彩映射: {colormap}")
        return colormap
    
    def list_available_colormaps(self):
        """列出所有可用的配色方案"""
        print("\n--- 可用的配色方案 ---")
        print("\n连续数据配色:")
        for name in ["viridis", "plasma", "inferno", "magma", "cividis", "turbo"]:
            print(f"  - {name}")
        
        print("\n经典渐变:")
        for name in ["jet", "rainbow", "ocean", "terrain"]:
            print(f"  - {name}")
        
        print("\n高对比:")
        for name in ["hot", "cool", "copper"]:
            print(f"  - {name}")
        
        print("\n科学数据常用:")
        for name in ["RdBu", "coolwarm", "seismic", "spectral"]:
            print(f"  - {name}")
        
        print("\n单色渐变:")
        for name in ["Blues", "Reds", "Greens", "YlOrRd", "BuPu"]:
            print(f"  - {name}")
        
        print("\n色盲友好方案:")
        for name in ["cividis", "viridis"]:
            print(f"  - {name}")
        
        print("\n--- 自定义渐变色 ---")
        print("可以提供两个颜色值(RGB或HEX)创建自定义渐变，例如:")
        print("  - ['#FF0000', '#0000FF']  # 红色到蓝色")
        print("  - ['red', 'yellow']       # 红色到黄色")
        print("  - ['#00FF00', '#FF00FF']  # 绿色到粉色")
        print("")

    def _create_file_grid(self):
        """创建文件路径网格，使用自然排序"""
        logger.info(f"从 {self.input_folder} 创建文件网格...")
        
        # 获取所有CSV文件
        csv_files = glob.glob(os.path.join(self.input_folder, "*.csv"))
        
        if not csv_files:
            raise ValueError(f"在 {self.input_folder} 中没有找到CSV文件")
        
        # 自然排序函数
        def natural_sort_key(s):
            return [int(text) if text.isdigit() else text.lower() 
                    for text in re.split(r'(\d+)', os.path.basename(s))]
        
        # 排序文件
        csv_files.sort(key=natural_sort_key)
        
        # 初始化空网格
        self.file_paths_grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        
        # 按行优先顺序填充网格
        for idx, file_path in enumerate(csv_files):
            if idx >= self.rows * self.cols:
                logger.warning(f"文件数量({len(csv_files)})超过网格大小({self.rows}×{self.cols})，将截断")
                break
                
            row = idx // self.cols
            col = idx % self.cols
            self.file_paths_grid[row][col] = file_path
        
        logger.info(f"创建了 {self.rows}×{self.cols} 的文件网格")
    
    def _load_data(self):
        """从所有CSV文件加载数据"""
        logger.info("加载数据...")
        
        for i in range(self.rows):
            for j in range(self.cols):
                file_path = self.file_paths_grid[i][j]
                
                # 跳过空单元格
                if file_path is None or not file_path:
                    continue
                
                try:
                    # 读取CSV文件
                    df = pd.read_csv(file_path)
                    
                    # 确保至少有2列
                    if len(df.columns) < 2:
                        logger.warning(f"文件 {file_path} 的列数少于2列")
                        continue
                    
                    # 假设第一列是时间，第二列是信号
                    time_col = df.columns[0]
                    signal_col = df.columns[1]
                    
                    # 转换为数值
                    df[time_col] = pd.to_numeric(df[time_col], errors='coerce')
                    df[signal_col] = pd.to_numeric(df[signal_col], errors='coerce')
                    
                    # 删除NaN值
                    df = df.dropna(subset=[time_col, signal_col])
                    
                    # 如果没有数据则跳过
                    if len(df) == 0:
                        logger.warning(f"文件 {file_path} 中没有有效数据")
                        continue
                    
                    # 更新最小/最大值
                    self.min_time = min(self.min_time, df[time_col].min())
                    self.max_time = max(self.max_time, df[time_col].max())
                    self.min_signal = min(self.min_signal, df[signal_col].min())
                    self.max_signal = max(self.max_signal, df[signal_col].max())
                    
                    # 存储数据
                    self.data[(i, j)] = {
                        'file_path': file_path,
                        'filename': os.path.basename(file_path),
                        'time': df[time_col].values,
                        'signal': df[signal_col].values
                    }
                    
                except Exception as e:
                    logger.error(f"处理文件 {file_path} 时出错: {e}")
        
        if not self.data:
            raise ValueError("没有找到有效的数据文件")
            
        logger.info(f"加载了 {len(self.data)} 个文件的数据")
        logger.info(f"时间范围: {self.min_time:.4f} 到 {self.max_time:.4f}")
        logger.info(f"信号范围: {self.min_signal:.4f} 到 {self.max_signal:.4f}")
    
    def _synchronize_time_points(self):
        """创建公共时间点并将所有信号插值到这些点"""
        logger.info("同步时间点...")
        
        # 创建公共时间点
        self.time_points = np.linspace(self.min_time, self.max_time, self.sampling_points)
        
        # 预分配3D网格数据: [时间, 行, 列]
        self.grid_data = np.full((len(self.time_points), self.rows, self.cols), np.nan)
        
        # 将每个信号插值到公共时间点
        for (i, j), item in self.data.items():
            # 创建插值函数(线性插值)
            f = interp.interp1d(
                item['time'], 
                item['signal'], 
                bounds_error=False, 
                fill_value=(item['signal'][0], item['signal'][-1])
            )
            
            # 插值到公共时间点
            interpolated_signal = f(self.time_points)
            
            # 存储到3D网格
            self.grid_data[:, i, j] = interpolated_signal
            
            # 同时存储到原始数据字典
            item['interp_signal'] = interpolated_signal
        
        logger.info(f"创建了 {len(self.time_points)} 个同步时间点")
    
    def generate_heatmap_video(self, 
                              output_file: str = "heatmap_animation.mp4", 
                              title: str = "Signal Intensity Over Time",
                              add_timestamp: bool = True,
                              add_colorbar: bool = True,
                              bitrate: str = "8000k"):
        """
        生成热图动画视频
        
        Args:
            output_file: 输出视频文件名
            title: 视频标题
            add_timestamp: 是否添加时间戳
            add_colorbar: 是否添加颜色条
            bitrate: 视频比特率
        """
        output_path = os.path.join(self.output_folder, output_file)
        logger.info(f"生成热图视频: {output_path}")
        
        # 设置图形尺寸 - 增加尺寸确保标题显示
        cell_size = 0.8  # 英寸/单元格
        fig_width = max(12, cell_size * self.cols + 3)  # 增加额外的空间给标题和颜色条
        fig_height = max(9, cell_size * self.rows + 3)  # 增加额外的空间给标题和轴标签
        
        # 创建图形和轴对象
        fig = plt.figure(figsize=(fig_width, fig_height), dpi=self.dpi)
        gs = gridspec.GridSpec(1, 2, width_ratios=[20, 1]) if add_colorbar else gridspec.GridSpec(1, 1)
        ax = plt.subplot(gs[0])
        
        # 设置色彩映射范围
        norm = Normalize(vmin=self.min_signal, vmax=self.max_signal)
        
        # 如果添加颜色条，创建相应轴
        if add_colorbar:
            cax = plt.subplot(gs[1])
            sm = ScalarMappable(cmap=self.colormap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, cax=cax)
            cbar.set_label('Signal Value')
        
        # 初始化热图
        im = ax.imshow(
            self.grid_data[0],
            cmap=self.colormap,
            norm=norm,
            aspect='equal',
            interpolation='nearest',
            origin='upper'
        )
        
        # 添加标题 - 调整位置以确保显示
        fig.suptitle(title, fontsize=16, y=0.95)
        
        # 设置轴标签和刻度
        ax.set_xlabel('Column')
        ax.set_ylabel('Row')
        ax.set_xticks(np.arange(self.cols))
        ax.set_yticks(np.arange(self.rows))
        ax.set_xticklabels(np.arange(self.cols))
        ax.set_yticklabels(np.arange(self.rows))
        
        # 添加网格
        ax.grid(color='black', linestyle='-', linewidth=0.5, alpha=0.3)
        
        # 添加时间戳
        if add_timestamp:
            time_text = ax.text(
                0.02, 0.95, '', transform=ax.transAxes,
                fontsize=12, color='black', 
                bbox=dict(facecolor='white', alpha=0.5, pad=5)
            )
        
        # 修剪图形边距
        plt.tight_layout(rect=[0, 0, 1, 0.93])  # 为标题留出空间
        
        # 更新函数 - 每一帧调用
        def update(frame):
            # 更新热图数据
            im.set_array(self.grid_data[frame])
            
            # 更新时间戳
            if add_timestamp:
                time_text.set_text(f'Time: {self.time_points[frame]:.4f}')
            
            return [im] + ([time_text] if add_timestamp else [])
        
        # 创建动画
        total_frames = len(self.time_points)
        logger.info(f"创建 {total_frames} 帧的动画...")
        
        # 使用tqdm显示进度条
        progress_callback = lambda i, n: tqdm.write(f'渲染帧 {i}/{n}', end='\r') if i % 10 == 0 else None
        
        # 创建动画
        anim = animation.FuncAnimation(
            fig, update, frames=total_frames, interval=1000/self.fps, blit=True
        )
        
        # 设置FFMPEG参数
        ffmpeg_params = [
            '-vcodec', 'libx264',
            '-preset', 'slow',
            '-profile:v', 'high',
            '-level:v', '4.0',
            '-pix_fmt', 'yuv420p',
            '-b:v', bitrate,
            '-maxrate', bitrate,
            '-bufsize', str(int(bitrate.replace('k', '000')) * 2)
        ]
        
        # 保存视频
        logger.info(f"正在保存视频到 {output_path}...")
        anim.save(
            output_path, 
            writer='ffmpeg', 
            fps=self.fps, 
            dpi=self.dpi,
            extra_args=ffmpeg_params,
            progress_callback=progress_callback,
            savefig_kwargs={'facecolor': 'white'}  # 更改为白色背景
        )
        
        # 关闭图形
        plt.close(fig)
        
        logger.info(f"热图视频已保存到 {output_path}")
    
    def generate_3d_surface_video(self, 
                                 output_file: str = "3d_surface_animation.mp4", 
                                 title: str = "3D Signal Surface Over Time",
                                 add_timestamp: bool = True,
                                 add_colorbar: bool = True,
                                 rotate_view: bool = True,
                                 initial_elev: float = 30,
                                 initial_azim: float = 30,
                                 rotation_speed: float = 1.0,
                                 full_rotation: bool = True,
                                 bitrate: str = "8000k"):
        """
        生成3D表面动画视频
        
        Args:
            output_file: 输出视频文件名
            title: 视频标题
            add_timestamp: 是否添加时间戳
            add_colorbar: 是否添加颜色条
            rotate_view: 是否在动画中旋转视图
            initial_elev: 初始仰角 (0-90度)
            initial_azim: 初始方位角 (0-360度)
            rotation_speed: 旋转速度倍率 (1.0为标准速度)
            full_rotation: 是否进行完整360度旋转 (False则仅在初始角度附近小幅度旋转)
            bitrate: 视频比特率
        """
        from mpl_toolkits.mplot3d import Axes3D
        
        output_path = os.path.join(self.output_folder, output_file)
        logger.info(f"生成3D表面视频: {output_path}")
        
        # 设置图形尺寸 - 增加尺寸确保标题显示
        fig = plt.figure(figsize=(14, 11), dpi=self.dpi)  # 增加高度以留出标题空间
        
        # 创建子图，并留出标题空间
        ax = fig.add_subplot(111, projection='3d')
        
        # 创建X和Y坐标网格
        X = np.arange(self.cols)
        Y = np.arange(self.rows)
        X, Y = np.meshgrid(X, Y)
        
        # 初始化表面
        surf = ax.plot_surface(
            X, Y, self.grid_data[0],
            cmap=self.colormap,
            linewidth=0,
            antialiased=True,
            vmin=self.min_signal,
            vmax=self.max_signal
        )
        
        # 添加颜色条
        if add_colorbar:
            cbar = fig.colorbar(surf, ax=ax, shrink=0.6, aspect=10)
            cbar.set_label('Signal Value')
        
        # 使用fig.suptitle代替ax.set_title，以获得更好的控制
        fig.suptitle(title, fontsize=18, y=0.98)
        
        # 设置轴标签
        ax.set_xlabel('Column')
        ax.set_ylabel('Row')
        ax.set_zlabel('Signal Value')
        
        # 设置轴范围
        ax.set_xlim(0, self.cols-1)
        ax.set_ylim(0, self.rows-1)
        ax.set_zlim(self.min_signal, self.max_signal)
        
        # 设置初始视角
        ax.view_init(elev=initial_elev, azim=initial_azim)
        
        # 添加时间戳
        if add_timestamp:
            time_text = ax.text2D(
                0.02, 0.95, '', transform=ax.transAxes,
                fontsize=12, color='black', 
                bbox=dict(facecolor='white', alpha=0.5, pad=5)
            )
        
        # 计算视图旋转角度
        if rotate_view:
            if full_rotation:
                # 完整360度旋转
                elev_range = np.linspace(initial_elev, initial_elev + 30, len(self.time_points)) % 90
                azim_range = np.linspace(initial_azim, initial_azim + 360 * rotation_speed, len(self.time_points)) % 360
            else:
                # 在初始视角附近小幅度摆动
                elev_amplitude = 15  # 仰角摆动幅度
                azim_amplitude = 45  # 方位角摆动幅度
                
                elev_range = initial_elev + elev_amplitude * np.sin(np.linspace(0, 2*np.pi * rotation_speed, len(self.time_points)))
                azim_range = initial_azim + azim_amplitude * np.sin(np.linspace(0, 4*np.pi * rotation_speed, len(self.time_points)))
        
        # 适当调整图形布局，确保标题有足够空间
        plt.subplots_adjust(top=0.9)  # 为标题留出更多空间
        
        # 更新函数 - 每一帧调用
        def update(frame):
            # 清除当前表面
            ax.clear()
            
            # 创建新的表面
            surf = ax.plot_surface(
                X, Y, self.grid_data[frame],
                cmap=self.colormap,
                linewidth=0,
                antialiased=True,
                vmin=self.min_signal,
                vmax=self.max_signal
            )
            
            # 重新设置轴标签
            ax.set_xlabel('Column')
            ax.set_ylabel('Row')
            ax.set_zlabel('Signal Value')
            
            # 设置轴范围
            ax.set_xlim(0, self.cols-1)
            ax.set_ylim(0, self.rows-1)
            ax.set_zlim(self.min_signal, self.max_signal)
            
            # 添加时间戳
            if add_timestamp:
                time_text = ax.text2D(
                    0.02, 0.95, f'Time: {self.time_points[frame]:.4f}',
                    transform=ax.transAxes, fontsize=12, color='black',
                    bbox=dict(facecolor='white', alpha=0.5, pad=5)
                )
            
            # 更新视图角度
            if rotate_view:
                ax.view_init(elev=elev_range[frame], azim=azim_range[frame])
            else:
                ax.view_init(elev=initial_elev, azim=initial_azim)
            
            return [surf]
        
        # 创建动画
        total_frames = len(self.time_points)
        logger.info(f"创建 {total_frames} 帧的动画...")
        
        # 使用tqdm显示进度条
        progress_callback = lambda i, n: tqdm.write(f'渲染帧 {i}/{n}', end='\r') if i % 10 == 0 else None
        
        # 创建动画
        anim = animation.FuncAnimation(
            fig, update, frames=total_frames, interval=1000/self.fps, blit=False
        )
        
        # 设置FFMPEG参数
        ffmpeg_params = [
            '-vcodec', 'libx264',
            '-preset', 'slow',
            '-profile:v', 'high',
            '-level:v', '4.0',
            '-pix_fmt', 'yuv420p',
            '-b:v', bitrate,
            '-maxrate', bitrate,
            '-bufsize', str(int(bitrate.replace('k', '000')) * 2)
        ]
        
        # 保存视频
        logger.info(f"正在保存视频到 {output_path}...")
        anim.save(
            output_path, 
            writer='ffmpeg', 
            fps=self.fps, 
            dpi=self.dpi,
            extra_args=ffmpeg_params,
            progress_callback=progress_callback,
            savefig_kwargs={'facecolor': 'white'}  # 更改为白色背景
        )
        
        # 关闭图形
        plt.close(fig)
        
        logger.info(f"3D表面视频已保存到 {output_path}")
    
    def generate_heatmap_with_profiles_video(self,
                                           output_file: str = "heatmap_with_profiles.mp4",
                                           title: str = "Heatmap with Signal Profiles",
                                           add_timestamp: bool = True,
                                           bitrate: str = "8000k"):
        """
        生成带有横纵剖面的热图动画视频
        
        Args:
            output_file: 输出视频文件名
            title: 视频标题
            add_timestamp: 是否添加时间戳
            bitrate: 视频比特率
        """
        output_path = os.path.join(self.output_folder, output_file)
        logger.info(f"生成带剖面的热图视频: {output_path}")
        
        # 创建图形和子图布局
        fig = plt.figure(figsize=(14, 10), dpi=self.dpi)
        gs = gridspec.GridSpec(2, 2, width_ratios=[3, 1], height_ratios=[1, 3],
                             wspace=0.05, hspace=0.05)
        
        # 主热图
        ax_heatmap = plt.subplot(gs[1, 0])
        # 顶部剖面图
        ax_top = plt.subplot(gs[0, 0], sharex=ax_heatmap)
        # 右侧剖面图
        ax_right = plt.subplot(gs[1, 1], sharey=ax_heatmap)
        # 隐藏不需要的刻度
        plt.setp(ax_top.get_xticklabels(), visible=False)
        plt.setp(ax_right.get_yticklabels(), visible=False)
        
        # 设置色彩映射范围
        norm = Normalize(vmin=self.min_signal, vmax=self.max_signal)
        
        # 初始化热图
        im = ax_heatmap.imshow(
            self.grid_data[0],
            cmap=self.colormap,
            norm=norm,
            aspect='equal',
            interpolation='nearest',
            origin='upper'
        )
        
        # 添加颜色条
        cbar = fig.colorbar(im, ax=ax_heatmap, orientation='horizontal', pad=0.1)
        cbar.set_label('Signal Value')
        
        # 初始化剖面图 - 中间行和中间列
        middle_row = self.rows // 2
        middle_col = self.cols // 2
        
        # 水平剖面(固定行，所有列)
        line_top, = ax_top.plot(range(self.cols), self.grid_data[0, middle_row, :], 'b-', lw=2)
        ax_top.set_ylim(self.min_signal, self.max_signal)
        ax_top.set_title(f'Row {middle_row} Profile')
        
        # 垂直剖面(所有行，固定列)
        line_right, = ax_right.plot(self.grid_data[0, :, middle_col], range(self.rows), 'r-', lw=2)
        ax_right.set_xlim(self.min_signal, self.max_signal)
        ax_right.set_title(f'Column {middle_col} Profile')
        
        # 在热图上显示剖面线
        h_line = ax_heatmap.axhline(y=middle_row, color='b', lw=1)
        v_line = ax_heatmap.axvline(x=middle_col, color='r', lw=1)
        
        # 设置轴标签
        ax_heatmap.set_xlabel('Column')
        ax_heatmap.set_ylabel('Row')
        
        # 添加标题
        fig.suptitle(title, fontsize=16, y=0.98)
        
        # 添加时间戳
        if add_timestamp:
            time_text = ax_heatmap.text(
                0.02, 0.95, '', transform=ax_heatmap.transAxes,
                fontsize=12, color='white', 
                bbox=dict(facecolor='black', alpha=0.5, pad=5)
            )
        
        # 添加交互说明
        fig.text(0.5, 0.01, 'Showing profiles for fixed middle row and column', 
                ha='center', va='center', fontsize=10, 
                bbox=dict(facecolor='white', alpha=0.7, pad=5))
        
        # 更新函数 - 每一帧调用
        def update(frame):
            # 更新热图数据
            im.set_array(self.grid_data[frame])
            
            # 更新剖面图数据
            line_top.set_ydata(self.grid_data[frame, middle_row, :])
            line_right.set_xdata(self.grid_data[frame, :, middle_col])
            
            # 更新时间戳
            if add_timestamp:
                time_text.set_text(f'Time: {self.time_points[frame]:.4f}')
            
            return [im, line_top, line_right, time_text] if add_timestamp else [im, line_top, line_right]
        
        # 创建动画
        total_frames = len(self.time_points)
        logger.info(f"创建 {total_frames} 帧的动画...")
        
        # 使用tqdm显示进度条
        progress_callback = lambda i, n: tqdm.write(f'渲染帧 {i}/{n}', end='\r') if i % 10 == 0 else None
        
        # 创建动画
        anim = animation.FuncAnimation(
            fig, update, frames=total_frames, interval=1000/self.fps, blit=True
        )
        
        # 设置FFMPEG参数
        ffmpeg_params = [
            '-vcodec', 'libx264',
            '-preset', 'slow',
            '-profile:v', 'high',
            '-level:v', '4.0',
            '-pix_fmt', 'yuv420p',
            '-b:v', bitrate,
            '-maxrate', bitrate,
            '-bufsize', str(int(bitrate.replace('k', '000')) * 2)
        ]
        
        # 保存视频
        logger.info(f"正在保存视频到 {output_path}...")
        anim.save(
            output_path, 
            writer='ffmpeg', 
            fps=self.fps, 
            dpi=self.dpi,
            extra_args=ffmpeg_params,
            progress_callback=progress_callback,
            savefig_kwargs={'facecolor': 'white'}
        )
        
        # 关闭图形
        plt.close(fig)
        
        logger.info(f"带剖面的热图视频已保存到 {output_path}")
    
    def generate_heatmap_at_time(self,
                               target_time: float,
                               output_file: str = None,
                               title: str = "Signal Intensity at Specific Time",
                               add_colorbar: bool = True,
                               dpi: int = None):
        """
        根据指定时间生成热图静态图像
        
        Args:
            target_time: 目标时间点
            output_file: 输出图像文件名，为None时使用默认命名
            title: 图像标题
            add_colorbar: 是否添加颜色条
            dpi: 图像分辨率，为None时使用对象的默认DPI
        
        Returns:
            str: 生成的图像文件路径
        """
        # 使用对象默认DPI或指定DPI
        dpi = dpi or self.dpi
        
        # 如果没有指定输出文件名，生成默认文件名
        if output_file is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"heatmap_time_{target_time:.4f}_{timestamp}.png"
        
        # 确保输出路径包含文件夹路径
        output_path = os.path.join(self.output_folder, output_file)
        logger.info(f"生成特定时间点的热图: {output_path}, 时间: {target_time:.4f}")
        
        # 找到最接近目标时间的时间点索引
        nearest_idx = np.abs(self.time_points - target_time).argmin()
        actual_time = self.time_points[nearest_idx]
        logger.info(f"找到最接近的时间点: {actual_time:.4f} (索引: {nearest_idx})")
        
        # 设置图形尺寸
        cell_size = 0.8  # 英寸/单元格
        fig_width = max(12, cell_size * self.cols + 3)
        fig_height = max(9, cell_size * self.rows + 3)
        
        # 创建图形和轴对象
        fig = plt.figure(figsize=(fig_width, fig_height), dpi=dpi)
        gs = gridspec.GridSpec(1, 2, width_ratios=[20, 1]) if add_colorbar else gridspec.GridSpec(1, 1)
        ax = plt.subplot(gs[0])
        
        # 设置色彩映射范围
        norm = Normalize(vmin=self.min_signal, vmax=self.max_signal)
        
        # 绘制热图
        im = ax.imshow(
            self.grid_data[nearest_idx],
            cmap=self.colormap,
            norm=norm,
            aspect='equal',
            interpolation='nearest',
            origin='upper'
        )
        
        # 添加颜色条
        if add_colorbar:
            cax = plt.subplot(gs[1])
            sm = ScalarMappable(cmap=self.colormap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, cax=cax)
            cbar.set_label('Signal Value')
        
        # 添加标题，包含时间信息
        full_title = f"{title}\nTime: {actual_time:.4f}"
        fig.suptitle(full_title, fontsize=16, y=0.95)
        
        # 设置轴标签和刻度
        ax.set_xlabel('Column')
        ax.set_ylabel('Row')
        ax.set_xticks(np.arange(self.cols))
        ax.set_yticks(np.arange(self.rows))
        ax.set_xticklabels(np.arange(self.cols))
        ax.set_yticklabels(np.arange(self.rows))
        
        # 添加网格
        ax.grid(color='black', linestyle='-', linewidth=0.5, alpha=0.3)
        
        # 调整布局
        plt.tight_layout(rect=[0, 0, 1, 0.93])
        
        # 保存图像
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
        
        # 关闭图形
        plt.close(fig)
        
        logger.info(f"热图已保存到 {output_path}")
        return output_path
    
    def generate_3d_surface_at_time(self,
                                   target_time: float,
                                   output_file: str = None,
                                   title: str = "3D Signal Surface at Specific Time",
                                   add_colorbar: bool = True,
                                   elev: float = 30,
                                   azim: float = 30,
                                   dpi: int = None):
        """
        根据指定时间生成3D表面静态图像
        
        Args:
            target_time: 目标时间点
            output_file: 输出图像文件名，为None时使用默认命名
            title: 图像标题
            add_colorbar: 是否添加颜色条
            elev: 视图仰角 (0-90度)
            azim: 视图方位角 (0-360度)
            dpi: 图像分辨率，为None时使用对象的默认DPI
        
        Returns:
            str: 生成的图像文件路径
        """
        from mpl_toolkits.mplot3d import Axes3D
        
        # 使用对象默认DPI或指定DPI
        dpi = dpi or self.dpi
        
        # 如果没有指定输出文件名，生成默认文件名
        if output_file is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"3d_surface_time_{target_time:.4f}_{timestamp}.png"
        
        # 确保输出路径包含文件夹路径
        output_path = os.path.join(self.output_folder, output_file)
        logger.info(f"生成特定时间点的3D表面图: {output_path}, 时间: {target_time:.4f}")
        
        # 找到最接近目标时间的时间点索引
        nearest_idx = np.abs(self.time_points - target_time).argmin()
        actual_time = self.time_points[nearest_idx]
        logger.info(f"找到最接近的时间点: {actual_time:.4f} (索引: {nearest_idx})")
        
        # 创建图形
        fig = plt.figure(figsize=(14, 11), dpi=dpi)
        ax = fig.add_subplot(111, projection='3d')
        
        # 创建X和Y坐标网格
        X = np.arange(self.cols)
        Y = np.arange(self.rows)
        X, Y = np.meshgrid(X, Y)
        
        # 绘制3D表面
        surf = ax.plot_surface(
            X, Y, self.grid_data[nearest_idx],
            cmap=self.colormap,
            linewidth=0,
            antialiased=True,
            vmin=self.min_signal,
            vmax=self.max_signal
        )
        
        # 添加颜色条
        if add_colorbar:
            cbar = fig.colorbar(surf, ax=ax, shrink=0.6, aspect=10)
            cbar.set_label('Signal Value')
        
        # 添加标题，包含时间信息
        full_title = f"{title}\nTime: {actual_time:.4f}"
        fig.suptitle(full_title, fontsize=18, y=0.98)
        
        # 设置轴标签
        ax.set_xlabel('Column')
        ax.set_ylabel('Row')
        ax.set_zlabel('Signal Value')
        
        # 设置轴范围
        ax.set_xlim(0, self.cols-1)
        ax.set_ylim(0, self.rows-1)
        ax.set_zlim(self.min_signal, self.max_signal)
        
        # 设置视角
        ax.view_init(elev=elev, azim=azim)
        
        # 调整布局
        plt.subplots_adjust(top=0.9)
        
        # 保存图像
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
        
        # 关闭图形
        plt.close(fig)
        
        logger.info(f"3D表面图已保存到 {output_path}")
        return output_path
    
    def generate_heatmap_with_profiles_at_time(self,
                                             target_time: float,
                                             output_file: str = None,
                                             title: str = "Heatmap with Signal Profiles at Specific Time",
                                             middle_row: int = None,
                                             middle_col: int = None,
                                             dpi: int = None):
        """
        根据指定时间生成带有横纵剖面的热图静态图像
        
        Args:
            target_time: 目标时间点
            output_file: 输出图像文件名，为None时使用默认命名
            title: 图像标题
            middle_row: 水平剖面的行索引，为None时使用中间行
            middle_col: 垂直剖面的列索引，为None时使用中间列
            dpi: 图像分辨率，为None时使用对象的默认DPI
        
        Returns:
            str: 生成的图像文件路径
        """
        # 使用对象默认DPI或指定DPI
        dpi = dpi or self.dpi
        
        # 如果没有指定剖面位置，使用中间行列
        if middle_row is None:
            middle_row = self.rows // 2
        if middle_col is None:
            middle_col = self.cols // 2
            
        # 确保剖面索引在有效范围内
        middle_row = max(0, min(middle_row, self.rows - 1))
        middle_col = max(0, min(middle_col, self.cols - 1))
        
        # 如果没有指定输出文件名，生成默认文件名
        if output_file is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"heatmap_profiles_time_{target_time:.4f}_{timestamp}.png"
        
        # 确保输出路径包含文件夹路径
        output_path = os.path.join(self.output_folder, output_file)
        logger.info(f"生成特定时间点的带剖面热图: {output_path}, 时间: {target_time:.4f}")
        
        # 找到最接近目标时间的时间点索引
        nearest_idx = np.abs(self.time_points - target_time).argmin()
        actual_time = self.time_points[nearest_idx]
        logger.info(f"找到最接近的时间点: {actual_time:.4f} (索引: {nearest_idx})")
        
        # 创建图形和子图布局
        fig = plt.figure(figsize=(14, 10), dpi=dpi)
        gs = gridspec.GridSpec(2, 2, width_ratios=[3, 1], height_ratios=[1, 3],
                             wspace=0.05, hspace=0.05)
        
        # 主热图
        ax_heatmap = plt.subplot(gs[1, 0])
        # 顶部剖面图
        ax_top = plt.subplot(gs[0, 0], sharex=ax_heatmap)
        # 右侧剖面图
        ax_right = plt.subplot(gs[1, 1], sharey=ax_heatmap)
        # 隐藏不需要的刻度
        plt.setp(ax_top.get_xticklabels(), visible=False)
        plt.setp(ax_right.get_yticklabels(), visible=False)
        
        # 设置色彩映射范围
        norm = Normalize(vmin=self.min_signal, vmax=self.max_signal)
        
        # 绘制热图
        im = ax_heatmap.imshow(
            self.grid_data[nearest_idx],
            cmap=self.colormap,
            norm=norm,
            aspect='equal',
            interpolation='nearest',
            origin='upper'
        )
        
        # 添加颜色条
        cbar = fig.colorbar(im, ax=ax_heatmap, orientation='horizontal', pad=0.1)
        cbar.set_label('Signal Value')
        
        # 水平剖面(固定行，所有列)
        ax_top.plot(range(self.cols), self.grid_data[nearest_idx, middle_row, :], 'b-', lw=2)
        ax_top.set_ylim(self.min_signal, self.max_signal)
        ax_top.set_title(f'Row {middle_row} Profile')
        
        # 垂直剖面(所有行，固定列)
        ax_right.plot(self.grid_data[nearest_idx, :, middle_col], range(self.rows), 'r-', lw=2)
        ax_right.set_xlim(self.min_signal, self.max_signal)
        ax_right.set_title(f'Column {middle_col} Profile')
        
        # 在热图上显示剖面线
        ax_heatmap.axhline(y=middle_row, color='b', lw=1)
        ax_heatmap.axvline(x=middle_col, color='r', lw=1)
        
        # 设置轴标签
        ax_heatmap.set_xlabel('Column')
        ax_heatmap.set_ylabel('Row')
        
        # 添加标题，包含时间信息
        full_title = f"{title}\nTime: {actual_time:.4f}"
        fig.suptitle(full_title, fontsize=16, y=0.98)
        
        # 添加交互说明
        fig.text(0.5, 0.01, f'Profiles for row {middle_row} and column {middle_col}', 
                ha='center', va='center', fontsize=10, 
                bbox=dict(facecolor='white', alpha=0.7, pad=5))
        
        # 保存图像
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
        
        # 关闭图形
        plt.close(fig)
        
        logger.info(f"带剖面的热图已保存到 {output_path}")
        return output_path
    
    def generate_all_videos(self, video_quality="high"):
        """生成所有类型的视频"""
        logger.info("生成所有类型的视频...")
        
        # 根据视频质量设置参数
        bitrate = "8000k" if video_quality == "high" else "3000k"
        dpi = 180 if video_quality == "high" else 120
        
        # 生成热图视频
        self.generate_heatmap_video(
            output_file="heatmap_animation.mp4",
            title="Signal Intensity Over Time",
            bitrate=bitrate
        )
        
        # 生成3D表面视频
        self.generate_3d_surface_video(
            output_file="3d_surface_animation.mp4",
            title="3D Signal Surface Over Time",
            rotate_view=True,
            bitrate=bitrate
        )
        
        # 生成带剖面的热图视频
        self.generate_heatmap_with_profiles_video(
            output_file="heatmap_with_profiles.mp4",
            title="Heatmap with Signal Profiles",
            bitrate=bitrate
        )
        
        logger.info(f"所有视频已生成并保存到: {self.output_folder}")


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='生成高质量时间序列数据可视化视频')
    parser.add_argument('--input', '-i', required=True, help='输入文件夹路径（包含CSV文件）')
    parser.add_argument('--output', '-o', default='./output/videos', help='输出文件夹路径')
    parser.add_argument('--rows', '-r', type=int, required=True, help='数据网格的行数')
    parser.add_argument('--cols', '-c', type=int, required=True, help='数据网格的列数')
    parser.add_argument('--fps', '-f', type=int, default=30, help='视频帧率')
    parser.add_argument('--dpi', '-d', type=int, default=150, help='视频分辨率(DPI)')
    parser.add_argument('--colormap', '-m', default='viridis', help='颜色映射名称 (使用 --list-colormaps 查看所有选项)')
    parser.add_argument('--custom-gradient', nargs=2, metavar=('COLOR1', 'COLOR2'), 
                        help='自定义渐变色, 提供两个颜色值(RGB或HEX), 例如: "#FF0000" "#0000FF"')
    parser.add_argument('--list-colormaps', action='store_true', help='列出所有可用的配色方案')
    parser.add_argument('--quality', '-q', choices=['low', 'medium', 'high'], default='high', help='视频质量')
    parser.add_argument('--type', '-t', choices=['all', 'heatmap', '3d', 'profiles'], default='all',
                       help='要生成的视频类型')
    parser.add_argument('--sampling', '-s', type=int, default=500, help='采样点数量')
    
    # 3D视图参数
    parser.add_argument('--rotate', action='store_true', help='是否旋转3D视图')
    parser.add_argument('--no-rotate', action='store_false', dest='rotate', help='不旋转3D视图')
    parser.add_argument('--elev', type=float, default=30.0, help='3D视图初始仰角')
    parser.add_argument('--azim', type=float, default=30.0, help='3D视图初始方位角')
    parser.add_argument('--rot-speed', type=float, default=1.0, help='3D视图旋转速度')
    parser.add_argument('--full-rotation', action='store_true', help='3D视图进行完整360度旋转')
    parser.add_argument('--partial-rotation', action='store_false', dest='full_rotation', help='3D视图在初始视角附近小幅摆动')
    
    # 特定时间点图像生成参数
    parser.add_argument('--time', type=float, help='生成特定时间点的静态图像而非视频')
    parser.add_argument('--time-start', action='store_true', help='生成时间序列开始时刻的静态图像')
    parser.add_argument('--time-middle', action='store_true', help='生成时间序列中间时刻的静态图像')
    parser.add_argument('--time-end', action='store_true', help='生成时间序列结束时刻的静态图像')
    parser.add_argument('--time-all', action='store_true', help='生成时间序列开始、中间和结束三个时刻的静态图像')
    
    # 设置默认值
    parser.set_defaults(rotate=True, full_rotation=True)
    
    args = parser.parse_args()
    
    # 如果请求列出配色方案，打印并退出
    if args.list_colormaps:
        # 临时创建一个VideoGenerator实例，只用于列出配色方案
        temp_gen = VideoGenerator(
            input_folder=".",  # 不重要，因为我们只调用list_available_colormaps
            rows=1,
            cols=1,
            output_folder="."
        )
        temp_gen.list_available_colormaps()
        return 0
    
    try:
        # 创建视频生成器
        video_gen = VideoGenerator(
            input_folder=args.input,
            rows=args.rows,
            cols=args.cols,
            fps=args.fps,
            dpi=args.dpi,
            sampling_points=args.sampling,
            colormap=args.colormap,
            custom_gradient=args.custom_gradient,
            output_folder=args.output
        )
        
        # 检查是否生成特定时间点的静态图像
        if args.time is not None or args.time_start or args.time_middle or args.time_end or args.time_all:
            # 如果指定了具体时间
            if args.time is not None:
                if args.type == 'all' or args.type == 'heatmap':
                    video_gen.generate_heatmap_at_time(
                        target_time=args.time,
                        title=f"信号强度热图 (时间: {args.time:.4f})"
                    )
                
                if args.type == 'all' or args.type == '3d':
                    video_gen.generate_3d_surface_at_time(
                        target_time=args.time,
                        elev=args.elev,
                        azim=args.azim,
                        title=f"3D信号表面 (时间: {args.time:.4f})"
                    )
                
                if args.type == 'all' or args.type == 'profiles':
                    video_gen.generate_heatmap_with_profiles_at_time(
                        target_time=args.time,
                        title=f"带剖面热图 (时间: {args.time:.4f})"
                    )
                
                logger.info(f"已生成时间点 {args.time:.4f} 的静态图像")
            
            # 如果请求特定时间点
            if args.time_all or args.time_start:
                video_gen.generate_heatmap_at_time(
                    target_time=video_gen.min_time,
                    output_file="time_series_start.png",
                    title="信号强度热图 (开始时刻)"
                )
                logger.info(f"已生成开始时刻 {video_gen.min_time:.4f} 的热图")
            
            if args.time_all or args.time_middle:
                middle_time = (video_gen.min_time + video_gen.max_time) / 2
                video_gen.generate_heatmap_at_time(
                    target_time=middle_time,
                    output_file="time_series_middle.png",
                    title="信号强度热图 (中间时刻)"
                )
                logger.info(f"已生成中间时刻 {middle_time:.4f} 的热图")
            
            if args.time_all or args.time_end:
                video_gen.generate_heatmap_at_time(
                    target_time=video_gen.max_time,
                    output_file="time_series_end.png",
                    title="信号强度热图 (结束时刻)"
                )
                logger.info(f"已生成结束时刻 {video_gen.max_time:.4f} 的热图")
                
            return 0
        
        # 根据类型生成视频
        if args.type == 'all':
            video_gen.generate_all_videos(args.quality)
        elif args.type == 'heatmap':
            video_gen.generate_heatmap_video()
        elif args.type == '3d':
            video_gen.generate_3d_surface_video(
                rotate_view=args.rotate,
                initial_elev=args.elev,
                initial_azim=args.azim,
                rotation_speed=args.rot_speed,
                full_rotation=args.full_rotation
            )
        elif args.type == 'profiles':
            video_gen.generate_heatmap_with_profiles_video()
        
        logger.info("视频生成完成!")
        
    except Exception as e:
        logger.error(f"生成视频时出错: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    # exit(main()) 
    #脚本执行，不用main，main是命令行

    # 脚本执行，不用main，main是命令行
    # 获取命令行参数
    input_folder = "./data2_csv_normalized"
    output_folder = "./output/videos2"
    rows = 6
    cols = 6

    # 创建视频生成器
    video_gen = VideoGenerator(
        input_folder=input_folder,
        rows=rows,
        cols=cols,
        output_folder=output_folder
    )

    # 列出所有可用配色方案
    video_gen.list_available_colormaps()

    # 生成热图视频 - 使用默认viridis配色
    video_gen.generate_heatmap_video(
        output_file="heatmap_animation_default.mp4",
        title="信号强度随时间变化 (默认配色)"
    )
    
    # 使用经典配色方案
    classic_colormap_gen = VideoGenerator(
        input_folder=input_folder,
        rows=rows,
        cols=cols,
        colormap="jet",  # 使用经典的jet配色
        output_folder=output_folder
    )
    
    classic_colormap_gen.generate_heatmap_video(
        output_file="heatmap_animation_jet.mp4",
        title="信号强度随时间变化 (Jet配色)"
    )
    
    # 使用自定义渐变配色
    custom_colormap_gen = VideoGenerator(
        input_folder=input_folder,
        rows=rows,
        cols=cols,
        custom_gradient=["#3366FF", "#FF3366"],  # 蓝色到粉红色渐变
        output_folder=output_folder
    )
    
    custom_colormap_gen.generate_heatmap_video(
        output_file="heatmap_animation_custom.mp4",
        title="信号强度随时间变化 (自定义渐变)"
    )
    
    # 生成3D表面视频 - 使用热力图配色
    heat_colormap_gen = VideoGenerator(
        input_folder=input_folder,
        rows=rows,
        cols=cols,
        colormap="hot",  # 热力图配色
        output_folder=output_folder
    )
    
    heat_colormap_gen.generate_3d_surface_video(
        output_file="3d_surface_animation_hot.mp4",
        title="3D信号表面 (热力图配色)",
        rotate_view=True,
        initial_elev=30,
        initial_azim=45,
        rotation_speed=1.0,
        full_rotation=True
    )
    
    # 使用科学数据常用的coolwarm配色
    coolwarm_colormap_gen = VideoGenerator(
        input_folder=input_folder,
        rows=rows,
        cols=cols,
        colormap="coolwarm",  # 冷暖对比配色
        output_folder=output_folder
    )
    
    coolwarm_colormap_gen.generate_3d_surface_video(
        output_file="3d_surface_animation_coolwarm.mp4",
        title="3D信号表面 (冷暖对比配色)",
        rotate_view=False,
        initial_elev=20,
        initial_azim=30
    )
    
    # 带剖面的热图视频 - 使用光谱配色
    spectral_colormap_gen = VideoGenerator(
        input_folder=input_folder,
        rows=rows,
        cols=cols,
        colormap="spectral",  # 光谱配色
        output_folder=output_folder
    )
    
    spectral_colormap_gen.generate_heatmap_with_profiles_video(
        output_file="heatmap_with_profiles_spectral.mp4",
        title="带剖面的热图 (光谱配色)"
    )
    
    # 示例：生成特定时间点的静态图像
    # 首先确定时间范围 
    print(f"\n数据时间范围: {video_gen.min_time:.4f} 到 {video_gen.max_time:.4f}")
    
    # 选择一个中间时间点
    middle_time = (video_gen.min_time + video_gen.max_time) / 2
    
    # 生成三种类型的特定时间点图像
    print(f"\n生成时间点 {middle_time:.4f} 的静态图像...")
    
    # 1. 热图
    heatmap_file = video_gen.generate_heatmap_at_time(
        target_time=middle_time,
        output_file="static_heatmap.png",
        title="特定时间点的信号强度热图"
    )
    
    # 2. 3D表面图 - 不同角度
    surface_file1 = video_gen.generate_3d_surface_at_time(
        target_time=middle_time,
        output_file="static_3d_surface_angle1.png",
        title="特定时间点的3D信号表面",
        elev=30,
        azim=45
    )
    
    surface_file2 = video_gen.generate_3d_surface_at_time(
        target_time=middle_time,
        output_file="static_3d_surface_angle2.png",
        title="特定时间点的3D信号表面",
        elev=20,
        azim=120
    )
    
    # 3. 带剖面的热图
    profiles_file = video_gen.generate_heatmap_with_profiles_at_time(
        target_time=middle_time,
        output_file="static_heatmap_with_profiles.png",
        title="特定时间点的带剖面热图"
    )
    
    print(f"\n已生成以下静态图像:")
    print(f"  热图: {heatmap_file}")
    print(f"  3D表面图(角度1): {surface_file1}")
    print(f"  3D表面图(角度2): {surface_file2}")
    print(f"  带剖面热图: {profiles_file}")
    
    # 特殊时间点的图像示例 - 使用时间序列的开始、中间和结束时间点
    start_time = video_gen.min_time
    end_time = video_gen.max_time
    
    # 创建一个使用coolwarm配色的生成器实例用于时间序列比较
    time_series_gen = VideoGenerator(
        input_folder=input_folder,
        rows=rows,
        cols=cols,
        colormap="coolwarm",
        output_folder=output_folder
    )
    
    # 生成时间序列的起始、中间和结束时刻的热图
    time_series_gen.generate_heatmap_at_time(
        target_time=start_time,
        output_file="time_series_start.png",
        title="信号强度热图 (开始时刻)"
    )
    
    time_series_gen.generate_heatmap_at_time(
        target_time=middle_time,
        output_file="time_series_middle.png",
        title="信号强度热图 (中间时刻)"
    )
    
    time_series_gen.generate_heatmap_at_time(
        target_time=end_time,
        output_file="time_series_end.png",
        title="信号强度热图 (结束时刻)"
    )
    
    print(f"\n已生成时间序列的三个关键时刻热图 (开始、中间、结束)")


    