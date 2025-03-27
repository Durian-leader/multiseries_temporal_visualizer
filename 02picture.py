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
processor.load_processed_data(input_file="output/my_processed_data_use_all_points.npz")
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
    vmax=None   # 设置颜色范围最大值，None表示使用现有数据的最大值
)

# 7. 生成指定时间点的热图
specific_time = 0.125  # 指定时刻(秒)
viz_gen.generate_heatmap_at_time(
    target_time=specific_time,
    output_file=None, # 指定热图的输出文件名，可以不指定，默认是"heatmap_time_{target_time:.4f}_{timestamp}.png"
    title=None, # 指定热图的标题，可以不指定，默认是“Signal Intensity at Specific \n Time :t=0.50s”
    vmin=None,  # 指定颜色范围最小值，None表示使用现有数据的最小值
    vmax=None   # 指定颜色范围最大值，None表示使用现有数据的最大值
)

# 8. 生成指定时间点和角度的3D表面图
logger.info("生成指定时间点的3D表面图")
viz_gen.generate_3d_surface_at_time(
    target_time=specific_time,
    output_file=None, # 指定3D表面图的输出文件名，可以不指定，默认是"3d_surface_time_{target_time:.4f}_{timestamp}.png"
    title=f"时刻 {specific_time:.2f}s 3D表面图",  # 指定3D表面图的标题
    vmin=None,  # 指定颜色范围最小值，None表示使用现有数据的最小值
    vmax=None   # 指定颜色范围最大值，None表示使用现有数据的最大值
)

# 生成指定时间点的带剖面的热图
logger.info("生成指定时间点的带剖面的热图")
viz_gen.generate_heatmap_with_profiles_at_time(
    target_time=specific_time,
    output_file=None, # 指定带剖面的热图的输出文件名，可以不指定，默认是"profile_heatmap_time_{target_time:.4f}_{timestamp}.png"
    title=f"时刻 {specific_time:.2f}s 带剖面的热图",  # 指定带剖面的热图的标题
    vmin=None,  # 指定颜色范围最小值，None表示使用现有数据的最小值
    vmax=None,   # 指定颜色范围最大值，None表示使用现有数据的最大值
    dpi=300,  # 设置输出图像的分辨率
    profile_col=3,  # 剖面所在的列索引
    profile_row=3,  # 剖面所在的行索引
)

time_points = processed_data['time_points']
# 找到最接近指定时间点的索引
nearest_idx = np.abs(time_points - specific_time).argmin()
nearest_time = time_points[nearest_idx]
logger.info(f"找到最接近的时间点: {nearest_time:.6f}")
nearest_grid_data = grid_data[nearest_idx]
logger.info(f"最接近时间点的数据范围: {nearest_grid_data.min():.6f} 到 {nearest_grid_data.max():.6f}")

# 保存为csv文件
output_csv_file = f"output/grid_data_at_time_{specific_time:.4f}.csv"
np.savetxt(output_csv_file, nearest_grid_data, delimiter=",")
logger.info(f"数据已保存到{output_csv_file}")

# 保存为csv文件，行是否翻转，列是否翻转
x_flip = False
y_flip = True
if x_flip:
    nearest_grid_data = np.flip(nearest_grid_data, axis=1)
if y_flip:
    nearest_grid_data = np.flip(nearest_grid_data, axis=0)

# 输出的文件名要能体现翻转了什么
output_csv_file = f"output/grid_data_at_time_{specific_time:.4f}_x_flip_{x_flip}_y_flip_{y_flip}.csv"
np.savetxt(output_csv_file, nearest_grid_data, delimiter=",")
logger.info(f"数据已保存到{output_csv_file}")
