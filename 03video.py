import os
from utils.dataprocess.vibration_data_loader import VibrationDataLoader  
from utils.dataprocess.start_idx_visualized_select import StartIdxVisualizedSelect
from utils.dataprocess.debiasing import debias_csv_folder
from utils.visualize.data_processor import DataProcessor
from utils.visualize.visualization_generator import VisualizationGenerator
from loguru import logger
import sys
from utils.visualize.extract_timepoint import extract_timepoint_data, visualize_grid,export_filename_grid
import pandas as pd
import matplotlib
import numpy as np
# Set up the matplotlib backend explicitly
matplotlib.use('TkAgg')  # Use TkAgg backend which has good button support

# 配置日志记录
logger.configure(handlers=[{"sink": sys.stdout, "level": "INFO"},
                           {"sink": "logs/log.log", "level": "INFO"}])

# 确保输出目录存在
os.makedirs('output', exist_ok=True)
os.makedirs('logs', exist_ok=True)
os.makedirs('output/data_csv', exist_ok=True)
os.makedirs('output/data_csv_start-idx-reselected', exist_ok=True)
os.makedirs('output/data_csv_start-idx-reselected_debiased', exist_ok=True)

# 6. 创建可视化
logger.info("开始生成可视化")
processor = DataProcessor()
processor.load_processed_data(input_file="output/my_processed_data_500points.npz")       # 这里记得替换为我们想要的总采样点数的数据文件
processed_data = processor.get_processed_data()


# 分析数据中的最小值和最大值
grid_data = processed_data['grid_data']
data_min = grid_data.min()
data_max = grid_data.max()
logger.info(f"数据范围: {data_min:.6f} 到 {data_max:.6f}")

# 定义所有可视化使用的统一颜色范围，可以先不设置，后面每个具体的图单独设置
viz_gen = VisualizationGenerator(
    processed_data=processed_data,
    colormap="viridis",  # 颜色映射
    output_folder="./output",  # 输出文件夹
    vmin=None,  # 设置颜色范围最小值，None表示使用现有数据的最小值
    vmax=None,  # 设置颜色范围最大值，None表示使用现有数据的最大值
    fps=30,  # 视频帧率                                                                     # 这里设置帧率
    dpi=150,  # 视频分辨率                                                                  # 这里设置分辨率
)

# # 9. 生成不旋转的指定角度的3D表面视频
# logger.info("生成固定视角的3D表面视频")
# viz_gen.generate_3d_surface_video(
#     rotate_view=False,  # 不旋转视角
#     initial_elev=45,   # 初始俯仰角度
#     initial_azim=45,   # 初始方位角度
#     add_timestamp=True,  # 添加时间戳
#     vmin=None,  # 指定颜色范围最小值，None表示使用现有数据的最小值
#     vmax=None,   # 指定颜色范围最大值，None表示使用现有数据的最大值
#     output_file="surface3d_fixed_view_elev45_azim45.mp4",
#     title="固定视角的3D表面动画"
# )

# # 10. 生成热图视频
# logger.info("生成热图视频")
# viz_gen.generate_heatmap_video(
#     output_file="heatmap_animation.mp4",
#     title="振动信号热图动画",
#     add_timestamp=True,  # 添加时间戳
#     add_colorbar=True,   # 添加颜色条
#     vmin=None,  # 指定颜色范围最小值，None表示使用现有数据的最小值
#     vmax=None   # 指定颜色范围最大值，None表示使用现有数据的最大值
# )

# 11. 生成带剖面图的热图视频
logger.info("生成带剖面图的热图视频")
viz_gen.generate_heatmap_with_profiles_video(
    output_file="heatmap_with_profiles.mp4",
    title="带剖面图的热图动画",
    add_timestamp=True,  # 添加时间戳
    vmin=None,  # 指定颜色范围最小值，None表示使用现有数据的最小值
    vmax=None,   # 指定颜色范围最大值，None表示使用现有数据的最大值
    profile_row=2,                                                                         # 剖面图所在行
    profile_col=2                                                                          # 剖面图所在列
)
