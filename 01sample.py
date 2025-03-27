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


sampling_points = 500  # 采样点数量
# 4. 使用DataProcessor处理数据并组织为网格结构
logger.info("开始处理数据并组织为网格结构")
processor = DataProcessor(
    input_folder="output/data_csv_denoised_start-idx-reselected_debiased",  # 修改为去偏后的数据目录
    rows=6,  # 根据数据布局调整行数
    cols=6,  # 根据数据布局调整列数
    sampling_points=sampling_points,  # 采样点数量
    use_all_points=False  # 是否使用所有点,默认是False,如果为True,则使用所有点，忽略采样点数量
)
# 5. 保存处理后的数据
processor.save_processed_data(f"./output/my_processed_data_{sampling_points}points.npz")
logger.info(f"数据已处理并保存到./output/my_processed_data_{sampling_points}points.npz")



# # 4. 使用DataProcessor处理数据并组织为网格结构
# logger.info("开始处理数据并组织为网格结构")
# processor = DataProcessor(
#     input_folder="./output/data_csv_start-idx-reselected_debiased",  # 修改为去偏后的数据目录
#     rows=6,  # 根据数据布局调整行数
#     cols=6,  # 根据数据布局调整列数
#     use_all_points=True  # 是否使用所有点,默认是False,如果为True,则使用所有点，忽略采样点数量
# )
# # 5. 保存处理后的数据
# processor.save_processed_data(f"./output/my_processed_data_use_all_points.npz")
# logger.info(f"数据已处理并保存到./output/my_processed_data_use_all_points.npz")