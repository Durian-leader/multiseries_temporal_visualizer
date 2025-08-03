import os
from utils.dataprocess.vibration_data_loader import VibrationDataLoader  
from utils.dataprocess.wavelet_denoise import WaveletDenoiser
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


# 1. 使用VibrationDataLoader将TXT文件转换为CSV
logger.info("开始将TXT文件转换为CSV格式")
VibrationDataLoader.convert_txt_to_csv_batch(
    "./input/data",                                                                                                                             # 包含TXT文件的输入文件夹
    "./output/data_csv"  # CSV文件的输出文件夹
)

# 2. 使用WaveletDenoiser进行小波去噪
logger.info("开始进行小波去噪处理")
denoiser = WaveletDenoiser(wavelet='db6', level=6, keep_nodes=['aaaaaa'])  # 保留低频与前两层细节
denoiser.denoise_csv_batch(
    input_folder="./output/data_csv",
    output_folder="./output/data_csv_denoised",
    columns=["Time Signal"]  # 自动选取数值列
)

# 3. 使用StartIdxVisualizedSelect进行起始点选择
logger.info("开始进行数据起始点选择")
processor_idx = StartIdxVisualizedSelect(
    "./output/data_csv_denoised",  # 包含CSV文件的输入文件夹
    "./output/data_csv_denoised_start-idx-reselected",  # 处理后文件的输出文件夹
    vg_delay=0.0025  # Vg信号延时2.5ms用于信号对齐
)
processor_idx.run()

# 4. 使用debias_csv_folder进行数据去偏处理
logger.info("开始进行数据去偏处理")
debias_csv_folder(
    "./output/data_csv_denoised_start-idx-reselected",  # 选择起始点后的输入文件夹 
    "./output/data_csv_denoised_start-idx-reselected_debiased",  # 去偏后数据的输出文件夹
    truncate_to_min=True  # 将所有文件截断至最短文件的长度
)

processor_use_all_points = DataProcessor(
    input_folder="./output/data_csv_denoised_start-idx-reselected_debiased",  # 修改为去偏后的数据目录
    rows=4,  # 根据数据布局调整行数
    cols=6,  # 根据数据布局调整列数
    use_all_points=True  # 是否使用所有点,默认是False,如果为True,则使用所有点，忽略采样点数量
)

processor_use_all_points.save_processed_data("./output/my_processed_data_use_all_points.npz")
logger.info("数据已处理并保存到./output/my_processed_data_use_all_points.npz")

