import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端，避免GUI依赖
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import Normalize, LinearSegmentedColormap, to_rgb
from matplotlib.cm import ScalarMappable
import matplotlib.gridspec as gridspec
from tqdm import tqdm
from loguru import logger
import datetime
from typing import List, Dict, Tuple, Optional, Union
from pathlib import Path
import sys


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


import platform

# 自动设置中文字体
if platform.system() == 'Windows':
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
elif platform.system() == 'Darwin':  # macOS
    plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti SC', 'STHeiti']
elif platform.system() == 'Linux':
    plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'WenQuanYi Zen Hei']

# 修复负号显示问题
plt.rcParams['axes.unicode_minus'] = False

class VisualizationGenerator:
    """
    生成高质量的时间序列数据可视化
    
    功能包括:
    - 高分辨率视频输出
    - 多种可视化模式 (热图、3D曲面、线图等)
    - 专业标题、时间戳和色彩映射
    - 自定义帧率和编码设置
    - 进度条和日志记录
    """
    
    def __init__(self,
                 processed_data: Dict,
                 fps: int = 30,
                 dpi: int = 150,
                 colormap: str = 'viridis',
                 custom_gradient: List[str] = None,
                 output_folder: str = './output/videos',
                 vmin: float = None,
                 vmax: float = None):
        """
        初始化可视化生成器
        
        Args:
            processed_data: 处理后的数据字典（从DataProcessor获取）
            fps: 视频帧率
            dpi: 视频分辨率(点/英寸)
            colormap: matplotlib颜色映射名称或经典配色方案的键名
            custom_gradient: 自定义渐变色, 提供两个RGB或HEX色号
            output_folder: 视频输出文件夹
            vmin: 颜色映射的最小值，为None时使用数据的最小值
            vmax: 颜色映射的最大值，为None时使用数据的最大值
        """
        # 从处理后的数据中提取所需信息
        self.grid_data = processed_data['grid_data']
        self.time_points = processed_data['time_points']
        self.min_signal = processed_data['min_signal']
        self.max_signal = processed_data['max_signal']
        self.min_time = processed_data['min_time']
        self.max_time = processed_data['max_time']
        self.rows = processed_data['rows']
        self.cols = processed_data['cols']
        
        # 设置颜色映射范围
        self.vmin = self.min_signal if vmin is None else vmin
        self.vmax = self.max_signal if vmax is None else vmax
        
        # 可视化配置
        self.fps = fps
        self.dpi = dpi
        self.output_folder = output_folder
        
        # 设置色彩映射
        self.colormap = self._setup_colormap(colormap, custom_gradient)
        
        # 确保输出文件夹存在
        os.makedirs(output_folder, exist_ok=True)
        
        # 检查动画保存选项
        self._check_animation_writers()
        
        logger.info("初始化VisualizationGenerator完成")
        logger.info(f"网格大小: {self.rows}×{self.cols}, 时间点: {len(self.time_points)}")
        logger.info(f"使用色彩映射: {self.colormap}")
        logger.info(f"颜色映射范围: {self.vmin} - {self.vmax}")
        
    def _check_animation_writers(self):
        """检查可用的动画保存选项"""
        try:
            import matplotlib.animation as animation
            available_writers = animation.writers.list()
            
            if 'ffmpeg' in available_writers:
                logger.info("检测到FFmpeg可用，将用于保存高质量MP4视频")
                
                # 测试FFmpeg是否真正可用
                try:
                    writer = animation.FFMpegWriter(fps=30, bitrate="1000k")
                    logger.info("FFmpeg配置正确")
                except Exception as e:
                    logger.warning(f"FFmpeg配置可能有问题: {e}")
                    logger.warning("视频可能会保存为其他格式")
                    
            elif 'pillow' in available_writers:
                logger.warning("未检测到FFmpeg，将使用Pillow保存为GIF格式")
                logger.warning("如需保存高质量MP4视频，请安装FFmpeg。详见INSTALLATION.md")
            elif 'html' in available_writers:
                logger.warning("未检测到FFmpeg或Pillow，将使用HTML格式保存动画")
                logger.warning("如需保存高质量MP4视频，请安装FFmpeg。详见INSTALLATION.md")
            else:
                logger.error("未检测到支持的动画保存选项！视频生成可能会失败。")
                logger.error("请安装FFmpeg以保存视频。详见INSTALLATION.md")
        except Exception as e:
            logger.error(f"检查动画保存选项时出错: {e}")
            logger.error("保存视频可能会失败，请确保已安装必要的依赖")
    
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
    
    def generate_heatmap_video(self, 
                              output_file: str = "heatmap_animation.mp4", 
                              title: str = "Signal Intensity Over Time",
                              add_timestamp: bool = True,
                              add_colorbar: bool = True,
                              vmin: float = None,
                              vmax: float = None,
                              bitrate: str = "8000k"):
        """
        生成热图动画视频
        
        Args:
            output_file: 输出视频文件名
            title: 视频标题
            add_timestamp: 是否添加时间戳
            add_colorbar: 是否添加颜色条
            vmin: 颜色映射的最小值，为None时使用初始化时设置的值
            vmax: 颜色映射的最大值，为None时使用初始化时设置的值
            bitrate: 视频比特率
        """
        output_path = os.path.join(self.output_folder, output_file)
        logger.info(f"生成热图视频: {output_path}")
        
        # 使用方法参数覆盖默认值
        vmin = self.vmin if vmin is None else vmin
        vmax = self.vmax if vmax is None else vmax
        
        # 设置图形尺寸 - 增加尺寸确保标题显示
        cell_size = 0.8  # 英寸/单元格
        fig_width = max(12, cell_size * self.cols + 3)  # 增加额外的空间给标题和颜色条
        fig_height = max(9, cell_size * self.rows + 3)  # 增加额外的空间给标题和轴标签
        
        # 创建图形和轴对象
        fig = plt.figure(figsize=(fig_width, fig_height), dpi=self.dpi)
        gs = gridspec.GridSpec(1, 2, width_ratios=[20, 1]) if add_colorbar else gridspec.GridSpec(1, 1)
        ax = plt.subplot(gs[0])
        
        # 设置色彩映射范围
        norm = Normalize(vmin=vmin, vmax=vmax)
        
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
            # '-vcodec', 'h264_nvenc',
            '-preset', 'slow',
            '-profile:v', 'high',
            # '-level:v', '4.0',
            '-pix_fmt', 'yuv420p',
            '-b:v', bitrate,
            '-maxrate', bitrate,
            '-bufsize', str(int(bitrate.replace('k', '000')) * 2),
            # '-threads', '4'
        ]
        
        # 保存视频
        output_file = self._save_animation(
            anim=anim,
            output_path=output_path,
            title=title,
            bitrate=bitrate,
            progress_callback=progress_callback,
            ffmpeg_params=ffmpeg_params
        )
        
        # 关闭图形
        plt.close(fig)
        
        if output_file:
            logger.info(f"热图视频已处理完成")
            return output_file
        else:
            logger.warning("热图视频保存失败")
            return None
    
    def generate_3d_surface_video(self, 
                                 output_file: str = "3d_surface_animation.mp4", 
                                 title: str = "3D Signal Surface Over Time",
                                 add_timestamp: bool = True,
                                 add_colorbar: bool = True,
                                 vmin: float = None,
                                 vmax: float = None,
                                 rotate_view: bool = True,
                                 initial_elev: float = 30,
                                 initial_azim: float = 30,
                                 rotation_speed: float = 1.0,
                                 full_rotation: bool = True,
                                 fixed_view: bool = False,
                                 view_angles: List[Tuple[float, float]] = None,
                                 bitrate: str = "8000k"):
        """
        生成3D表面动画视频
        
        Args:
            output_file: 输出视频文件名
            title: 视频标题
            add_timestamp: 是否添加时间戳
            add_colorbar: 是否添加颜色条
            vmin: 颜色映射的最小值，为None时使用初始化时设置的值
            vmax: 颜色映射的最大值，为None时使用初始化时设置的值
            rotate_view: 是否在动画中旋转视图
            initial_elev: 初始仰角 (0-90度)
            initial_azim: 初始方位角 (0-360度)
            rotation_speed: 旋转速度倍率 (1.0为标准速度)
            full_rotation: 是否进行完整360度旋转 (False则仅在初始角度附近小幅度旋转)
            fixed_view: 是否使用固定视角（不旋转，优先级高于rotate_view）
            view_angles: 自定义视角列表，格式为[(elev1, azim1), (elev2, azim2), ...]
                         - 如果为None且fixed_view=True，则使用initial_elev和initial_azim
                         - 如果提供且fixed_view=True，则使用指定的视角列表
            bitrate: 视频比特率
        """
        from mpl_toolkits.mplot3d import Axes3D
        
        output_path = os.path.join(self.output_folder, output_file)
        logger.info(f"生成3D表面视频: {output_path}")
        
        # 使用方法参数覆盖默认值
        vmin = self.vmin if vmin is None else vmin
        vmax = self.vmax if vmax is None else vmax
        
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
            vmin=vmin,
            vmax=vmax
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
        ax.set_zlim(vmin, vmax)
        
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
        if fixed_view:
            # 使用固定视角模式
            logger.info(f"使用固定视角模式")
            
            if view_angles is not None and len(view_angles) > 0:
                # 使用自定义视角列表
                logger.info(f"使用自定义视角列表，共{len(view_angles)}个视角")
                
                # 确保视角列表长度足够，如果不够则重复使用
                if len(view_angles) < len(self.time_points):
                    # 计算需要重复的次数
                    repeat_times = (len(self.time_points) + len(view_angles) - 1) // len(view_angles)
                    view_angles = view_angles * repeat_times
                
                # 截取所需长度的视角列表
                view_angles = view_angles[:len(self.time_points)]
                
                # 提取仰角和方位角列表
                elev_range = [angle[0] for angle in view_angles]
                azim_range = [angle[1] for angle in view_angles]
            else:
                # 使用固定的单一视角
                logger.info(f"使用固定单一视角: elev={initial_elev}, azim={initial_azim}")
                elev_range = [initial_elev] * len(self.time_points)
                azim_range = [initial_azim] * len(self.time_points)
        elif rotate_view:
            if full_rotation:
                # 完整360度旋转
                logger.info(f"使用完整360度旋转视角")
                elev_range = np.linspace(initial_elev, initial_elev + 30, len(self.time_points)) % 90
                azim_range = np.linspace(initial_azim, initial_azim + 360 * rotation_speed, len(self.time_points)) % 360
            else:
                # 在初始视角附近小幅度摆动
                logger.info(f"使用视角小幅摆动")
                elev_amplitude = 15  # 仰角摆动幅度
                azim_amplitude = 45  # 方位角摆动幅度
                
                elev_range = initial_elev + elev_amplitude * np.sin(np.linspace(0, 2*np.pi * rotation_speed, len(self.time_points)))
                azim_range = initial_azim + azim_amplitude * np.sin(np.linspace(0, 4*np.pi * rotation_speed, len(self.time_points)))
        else:
            # 不旋转，使用固定视角
            logger.info(f"不旋转，使用固定视角: elev={initial_elev}, azim={initial_azim}")
            elev_range = [initial_elev] * len(self.time_points)
            azim_range = [initial_azim] * len(self.time_points)
        
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
                vmin=vmin,
                vmax=vmax
            )
            
            # 重新设置轴标签
            ax.set_xlabel('Column')
            ax.set_ylabel('Row')
            ax.set_zlabel('Signal Value')
            
            # 设置轴范围
            ax.set_xlim(0, self.cols-1)
            ax.set_ylim(0, self.rows-1)
            ax.set_zlim(vmin, vmax)
            
            # 添加时间戳
            if add_timestamp:
                time_text = ax.text2D(
                    0.02, 0.95, f'Time: {self.time_points[frame]:.4f}',
                    transform=ax.transAxes, fontsize=12, color='black',
                    bbox=dict(facecolor='white', alpha=0.5, pad=5)
                )
            
            # 更新视图角度
            if isinstance(elev_range, (list, np.ndarray)) and isinstance(azim_range, (list, np.ndarray)):
                if frame < len(elev_range) and frame < len(azim_range):
                    ax.view_init(elev=elev_range[frame], azim=azim_range[frame])
                else:
                    # 如果索引超出范围，使用默认视角
                    ax.view_init(elev=initial_elev, azim=initial_azim)
            else:
                # 如果不是数组类型，使用默认视角
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
            # '-vcodec', 'h264_nvenc',  
            '-preset', 'slow',
            '-profile:v', 'high',
            # '-level:v', '4.0',
            '-pix_fmt', 'yuv420p',
            '-b:v', bitrate,
            '-maxrate', bitrate,
            '-bufsize', str(int(bitrate.replace('k', '000')) * 2),
            # '-threads', '4'
        ]
        
        # 保存视频
        output_file = self._save_animation(
            anim=anim,
            output_path=output_path,
            title=title,
            bitrate=bitrate,
            progress_callback=progress_callback,
            ffmpeg_params=ffmpeg_params
        )
        
        # 关闭图形
        plt.close(fig)
        
        if output_file:
            logger.info(f"3D表面视频已处理完成")
            return output_file
        else:
            logger.warning("3D表面视频保存失败")
            return None
            
        # 关闭图形
        plt.close(fig)
        
        logger.info(f"3D表面视频已处理完成")
        
        # 根据实际保存的文件返回不同的路径
        if os.path.exists(output_path):
            logger.info(f"3D表面视频已保存到 {output_path}")
            return output_path
        elif os.path.exists(output_path.replace('.mp4', '.gif')):
            gif_path = output_path.replace('.mp4', '.gif')
            logger.info(f"3D表面动画已保存为GIF: {gif_path}")
            return gif_path
        elif os.path.exists(output_path.replace('.mp4', '.html')):
            html_path = output_path.replace('.mp4', '.html')
            logger.info(f"3D表面动画已保存为HTML: {html_path}")
            return html_path
        else:
            logger.warning("无法确认保存的文件路径")
            return None
    
    def generate_heatmap_with_profiles_video(self,
                                           output_file: str = "heatmap_with_profiles.mp4",
                                           title: str = "Heatmap with Signal Profiles",
                                           add_timestamp: bool = True,
                                           vmin: float = None,
                                           vmax: float = None,
                                           bitrate: str = "8000k"):
        """
        生成带有横纵剖面的热图动画视频
        
        Args:
            output_file: 输出视频文件名
            title: 视频标题
            add_timestamp: 是否添加时间戳
            vmin: 颜色映射的最小值，为None时使用初始化时设置的值
            vmax: 颜色映射的最大值，为None时使用初始化时设置的值
            bitrate: 视频比特率
        """
        output_path = os.path.join(self.output_folder, output_file)
        logger.info(f"生成带剖面的热图视频: {output_path}")
        
        # 使用方法参数覆盖默认值
        vmin = self.vmin if vmin is None else vmin
        vmax = self.vmax if vmax is None else vmax
        
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
        norm = Normalize(vmin=vmin, vmax=vmax)
        
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
        ax_top.set_ylim(vmin, vmax)
        ax_top.set_title(f'Row {middle_row} Profile')
        
        # 垂直剖面(所有行，固定列)
        line_right, = ax_right.plot(self.grid_data[0, :, middle_col], range(self.rows), 'r-', lw=2)
        ax_right.set_xlim(vmin, vmax)
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
            # '-vcodec', 'h264_nvenc',
            '-preset', 'slow',
            '-profile:v', 'high',
            # '-level:v', '4.0',
            '-pix_fmt', 'yuv420p',
            '-b:v', bitrate,
            '-maxrate', bitrate,
            '-bufsize', str(int(bitrate.replace('k', '000')) * 2),
            # '-threads', '8'
        ]
        
        # 保存视频
        output_file = self._save_animation(
            anim=anim,
            output_path=output_path,
            title=title,
            bitrate=bitrate,
            progress_callback=progress_callback,
            ffmpeg_params=ffmpeg_params
        )
        
        # 关闭图形
        plt.close(fig)
        
        if output_file:
            logger.info(f"带剖面的热图视频已处理完成")
            return output_file
        else:
            logger.warning("带剖面的热图视频保存失败")
            return None
    
    def _save_animation(self, anim, output_path, title="Animation", bitrate="8000k", progress_callback=None, ffmpeg_params=None):
        """
        通用的动画保存函数，处理各种编码器和格式
        
        Args:
            anim: matplotlib动画对象
            output_path: 输出文件路径
            title: 视频标题
            bitrate: 视频比特率
            progress_callback: 进度回调函数
            ffmpeg_params: FFmpeg参数列表
            
        Returns:
            str: 实际保存的文件路径，或者None表示保存失败
        """
        logger.info(f"正在保存动画到 {output_path}...")
        
        try:
            # 首先检查ffmpeg是否可用
            import matplotlib.animation as animation_module
            if 'ffmpeg' in animation_module.writers.list():
                # 使用ffmpeg
                # 将bitrate转换为字符串，确保类型一致
                if not isinstance(bitrate, str):
                    bitrate = str(bitrate)
                    
                # 确保ffmpeg_params正确设置
                if ffmpeg_params is None:
                    ffmpeg_params = []
                
                writer = animation_module.FFMpegWriter(
                    fps=self.fps, 
                    metadata=dict(title=title),
                    # bitrate=bitrate,
                    extra_args=ffmpeg_params
                )
                anim.save(
                    output_path, 
                    writer=writer, 
                    dpi=self.dpi,
                    progress_callback=progress_callback,
                    savefig_kwargs={'facecolor': 'white'}  # 更改为白色背景
                )
                logger.info(f"已使用FFmpeg保存为视频: {output_path}")
                return output_path
            else:
                logger.warning("ffmpeg不可用。尝试其他视频编码器...")
                raise ValueError("ffmpeg不可用")
                
        except (ValueError, TypeError) as e:
            logger.warning(f"无法使用ffmpeg，错误: {e}。尝试使用其他视频编码器...")
            
            try:
                # 尝试使用pillow
                logger.info("尝试使用Pillow保存动画...")
                gif_path = output_path.replace('.mp4', '.gif')  # Pillow通常只支持GIF
                anim.save(
                    gif_path,
                    writer='pillow',
                    fps=self.fps,
                    dpi=self.dpi,
                )
                logger.info(f"已使用Pillow保存动画为GIF: {gif_path}")
                return gif_path
            except Exception as e2:
                logger.error(f"使用Pillow保存动画失败: {e2}")
                logger.info("尝试使用其他保存方式...")
                
                try:
                    # 尝试使用HTML保存
                    html_path = output_path.replace('.mp4', '.html')
                    anim.save(
                        html_path,
                        writer='html',
                        fps=self.fps,
                        dpi=self.dpi
                    )
                    logger.info(f"已保存动画为HTML: {html_path}")
                    return html_path
                except Exception as e3:
                    logger.error(f"保存为HTML失败: {e3}")
                    logger.error("无法保存动画，请安装ffmpeg后重试")
                    return None
                    
        except Exception as e:
            logger.error(f"保存动画失败: {e}")
            logger.error("请确保已正确安装ffmpeg或其他支持的视频编码器")
            return None
        
    def generate_heatmap_at_time(self,
                               target_time: float,
                               output_file: str = None,
                               title: str = "Signal Intensity at Specific Time",
                               add_colorbar: bool = True,
                               vmin: float = None,
                               vmax: float = None,
                               dpi: int = None):
        """
        根据指定时间生成热图静态图像
        
        Args:
            target_time: 目标时间点
            output_file: 输出图像文件名，为None时使用默认命名
            title: 图像标题
            add_colorbar: 是否添加颜色条
            vmin: 颜色映射的最小值，为None时使用初始化时设置的值
            vmax: 颜色映射的最大值，为None时使用初始化时设置的值
            dpi: 图像分辨率，为None时使用对象的默认DPI
        
        Returns:
            str: 生成的图像文件路径
        """
        # 使用对象默认DPI或指定DPI
        dpi = dpi or self.dpi
        
        # 使用方法参数覆盖默认值
        vmin = self.vmin if vmin is None else vmin
        vmax = self.vmax if vmax is None else vmax
        
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
        norm = Normalize(vmin=vmin, vmax=vmax)
        
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
                                   vmin: float = None,
                                   vmax: float = None,
                                   elev: float = 30,
                                   azim: float = 30,
                                   view_angles: List[Tuple[float, float]] = None,
                                   dpi: int = None):
        """
        根据指定时间生成3D表面静态图像
        
        Args:
            target_time: 目标时间点
            output_file: 输出图像文件名，为None时使用默认命名
            title: 图像标题
            add_colorbar: 是否添加颜色条
            vmin: 颜色映射的最小值，为None时使用初始化时设置的值
            vmax: 颜色映射的最大值，为None时使用初始化时设置的值
            elev: 视图仰角 (0-90度)
            azim: 视图方位角 (0-360度)
            view_angles: 自定义视角列表 [(elev1, azim1), (elev2, azim2), ...]
                        如果提供，则会生成多个不同视角的图像
            dpi: 图像分辨率，为None时使用对象的默认DPI
        
        Returns:
            str or List[str]: 生成的图像文件路径或路径列表
        """
        from mpl_toolkits.mplot3d import Axes3D
        
        # 使用对象默认DPI或指定DPI
        dpi = dpi or self.dpi
        
        # 使用方法参数覆盖默认值
        vmin = self.vmin if vmin is None else vmin
        vmax = self.vmax if vmax is None else vmax
        
        # 找到最接近目标时间的时间点索引
        nearest_idx = np.abs(self.time_points - target_time).argmin()
        actual_time = self.time_points[nearest_idx]
        logger.info(f"找到最接近的时间点: {actual_time:.4f} (索引: {nearest_idx})")
        
        # 决定使用哪些视角
        if view_angles is not None and len(view_angles) > 0:
            # 使用自定义视角列表，生成多个图像
            logger.info(f"将使用 {len(view_angles)} 个自定义视角生成图像")
            output_files = []
            
            for i, (angle_elev, angle_azim) in enumerate(view_angles):
                # 为每个视角创建不同的文件名
                if output_file is None:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    angle_output_file = f"3d_surface_time_{target_time:.4f}_angle{i+1}_{timestamp}.png"
                else:
                    # 在文件名中加入视角编号
                    base_name, ext = os.path.splitext(output_file)
                    angle_output_file = f"{base_name}_angle{i+1}{ext}"
                
                # 生成该视角的图像
                file_path = self._generate_single_3d_surface_at_time(
                    target_time=target_time,
                    nearest_idx=nearest_idx,
                    actual_time=actual_time,
                    output_file=angle_output_file,
                    title=title,
                    add_colorbar=add_colorbar,
                    vmin=vmin,
                    vmax=vmax,
                    elev=angle_elev,
                    azim=angle_azim,
                    dpi=dpi
                )
                
                output_files.append(file_path)
            
            logger.info(f"已生成 {len(output_files)} 个不同视角的3D表面图")
            return output_files
        else:
            # 使用单一视角
            if output_file is None:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"3d_surface_time_{target_time:.4f}_{timestamp}.png"
            
            # 生成单一视角的图像
            return self._generate_single_3d_surface_at_time(
                target_time=target_time,
                nearest_idx=nearest_idx,
                actual_time=actual_time,
                output_file=output_file,
                title=title,
                add_colorbar=add_colorbar,
                vmin=vmin,
                vmax=vmax,
                elev=elev,
                azim=azim,
                dpi=dpi
            )
    
    def _generate_single_3d_surface_at_time(self,
                                           target_time: float,
                                           nearest_idx: int,
                                           actual_time: float,
                                           output_file: str,
                                           title: str,
                                           add_colorbar: bool,
                                           vmin: float,
                                           vmax: float,
                                           elev: float,
                                           azim: float,
                                           dpi: int):
        """
        生成单一视角的3D表面图
        
        Args:
            target_time: 目标时间点
            nearest_idx: 最近时间点索引
            actual_time: 实际时间点
            output_file: 输出文件名
            title: 图像标题
            add_colorbar: 是否添加颜色条
            vmin: 颜色映射的最小值
            vmax: 颜色映射的最大值
            elev: 视图仰角 (0-90度)
            azim: 视图方位角 (0-360度)
            dpi: 图像分辨率
            
        Returns:
            str: 生成的图像文件路径
        """
        
        # 确保输出路径包含文件夹路径
        output_path = os.path.join(self.output_folder, output_file)
        logger.info(f"生成特定时间点的3D表面图: {output_path}, 时间: {actual_time:.4f}, 视角: elev={elev}, azim={azim}")
        
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
            vmin=vmin,
            vmax=vmax
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
        ax.set_zlim(vmin, vmax)
        
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
                                             vmin: float = None,
                                             vmax: float = None,
                                             middle_row: int = None,
                                             middle_col: int = None,
                                             dpi: int = None):
        """
        根据指定时间生成带有横纵剖面的热图静态图像
        
        Args:
            target_time: 目标时间点
            output_file: 输出图像文件名，为None时使用默认命名
            title: 图像标题
            vmin: 颜色映射的最小值，为None时使用初始化时设置的值
            vmax: 颜色映射的最大值，为None时使用初始化时设置的值
            middle_row: 水平剖面的行索引，为None时使用中间行
            middle_col: 垂直剖面的列索引，为None时使用中间列
            dpi: 图像分辨率，为None时使用对象的默认DPI
        
        Returns:
            str: 生成的图像文件路径
        """
        # 使用对象默认DPI或指定DPI
        dpi = dpi or self.dpi
        
        # 使用方法参数覆盖默认值
        vmin = self.vmin if vmin is None else vmin
        vmax = self.vmax if vmax is None else vmax
        
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
        norm = Normalize(vmin=vmin, vmax=vmax)
        
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
        ax_top.set_ylim(vmin, vmax)
        ax_top.set_title(f'Row {middle_row} Profile')
        
        # 垂直剖面(所有行，固定列)
        ax_right.plot(self.grid_data[nearest_idx, :, middle_col], range(self.rows), 'r-', lw=2)
        ax_right.set_xlim(vmin, vmax)
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
    
    def generate_all_videos(self, video_quality="high", vmin=None, vmax=None):
        """
        生成所有类型的视频
        
        Args:
            video_quality: 视频质量 ("high" 或 "low")
            vmin: 颜色映射的最小值，为None时使用初始化时设置的值
            vmax: 颜色映射的最大值，为None时使用初始化时设置的值
        """
        logger.info("生成所有类型的视频...")
        
        # 根据视频质量设置参数
        bitrate = "8000k" if video_quality == "high" else "3000k"
        
        # 生成热图视频
        heat_result = self.generate_heatmap_video(
            output_file="heatmap_animation.mp4",
            title="Signal Intensity Over Time",
            vmin=vmin,
            vmax=vmax,
            bitrate=bitrate
        )
        
        # 生成3D表面视频
        surface_result = self.generate_3d_surface_video(
            output_file="3d_surface_animation.mp4",
            title="3D Signal Surface Over Time",
            rotate_view=True,
            vmin=vmin,
            vmax=vmax,
            bitrate=bitrate
        )
        
        # 生成带剖面的热图视频
        profile_result = self.generate_heatmap_with_profiles_video(
            output_file="heatmap_with_profiles.mp4",
            title="Heatmap with Signal Profiles",
            vmin=vmin,
            vmax=vmax,
            bitrate=bitrate
        )
        
        results = {
            'heatmap': heat_result,
            '3d_surface': surface_result,
            'profiles': profile_result
        }
        
        logger.info(f"所有视频已生成并保存到: {self.output_folder}")
        return results


# 示例用法
if __name__ == "__main__":
    # 直接从保存的处理数据创建可视化生成器
    logger.configure(handlers=[{"sink": sys.stdout, "level": "INFO"},
                {"sink": "logs/visualization_generator.log", "level": "INFO", "rotation": "10 MB"}
                ])

    import numpy as np
    
    # 加载预处理数据
    data = np.load('my_processed_data.npz')
    
    # 创建处理数据字典
    processed_data = {
        'grid_data': data['grid_data'],
        'time_points': data['time_points'],
        'min_signal': float(data['min_signal']),
        'max_signal': float(data['max_signal']),
        'min_time': float(data['min_time']),
        'max_time': float(data['max_time']),
        'rows': int(data['rows']),
        'cols': int(data['cols']),
        'data': {}  # 这里简化处理，实际可能需要重建原始数据结构
    }
    
    # 创建可视化生成器
    viz_gen = VisualizationGenerator(
        processed_data=processed_data,
        colormap="viridis",
        output_folder="./output/videos",
        # 可以在这里设置自定义的colorbar范围
        vmin=-2.8069029999999988e-08,
        # vmax=5.183850000000003e-08
        vmax=1.183850000000003e-08
    )
    
    # 生成3D表面视频
    viz_gen.generate_3d_surface_video(
        output_file="3d_surface_animation_hot.mp4",
        title="3D信号表面 (热力图配色)",
        rotate_view=False,
        initial_elev=60,
        initial_azim=45,
        rotation_speed=1.0,
        full_rotation=True,
        # 也可以为单个可视化设置自定义的colorbar范围
        # vmin=-5.0,
        # vmax=5.0
    )
    
    # # 生成所有视频，也可以设置统一的colorbar范围
    # viz_gen.generate_all_videos(
    #     video_quality="high", 
    #     vmin=-8.0, 
    #     vmax=8.0
    # )
    
    # 生成特定时间点的图像
    middle_time = (processed_data['min_time'] + processed_data['max_time']) / 2
    
    viz_gen.generate_heatmap_at_time(
        target_time=middle_time,
        output_file="static_heatmap.png",
        title="特定时间点的信号强度热图",
        # vmin=-10.0,
        # vmax=10.0
    )
    
    viz_gen.generate_3d_surface_at_time(
        target_time=middle_time,
        output_file="static_3d_surface.png",
        title="特定时间点的3D信号表面",
        # vmin=-5.0,
        # vmax=5.0
    )
    
    viz_gen.generate_heatmap_with_profiles_at_time(
        target_time=middle_time,
        output_file="static_profiles.png",
        title="特定时间点的带剖面热图",
        # vmin=-10.0,
        # vmax=10.0
    )