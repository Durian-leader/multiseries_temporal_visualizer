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
# %matplotlib inline
import matplotlib.pyplot as plt
# 配置日志记录
logger.configure(handlers=[{"sink": sys.stdout, "level": "INFO"},
                           {"sink": "logs/log.log", "level": "INFO"}])



df = pd.read_csv("output/data_csv/54.csv")                                                      # 这里的文件路径需要根据实际情况修改
# 只保留低频节点 'a'（一级），或者更深层次的如 'aa', 'aaa'（更平滑趋势）
denoiser = WaveletDenoiser(wavelet='db6', level=6, keep_nodes=['aaaaaa'])  
denoised_df = denoiser.denoise_dataframe(df, columns=["Time Signal"])
fs = 1/df["Time"].diff().mean()  # 采样频率，单位 Hz
logger.info(f"采样频率是: {fs} Hz")
# 可视化对比
denoiser.plot_denoise_comparison(df, denoised_df, column="Time Signal", time_column="Time")
denoiser.plot_denoise_overlay(df, denoised_df, column="Time Signal", time_column="Time")
selected = denoiser.auto_select_trend_nodes(
    signal=df["Time Signal"].values,
    threshold_ratio=0.05,
    fs=fs,            # 采样频率，单位 Hz
    plot="band"         # 展示频带分布图，可选 "bar" 或 None
)
logger.info(f"自动选择的趋势节点: {selected}")
# 假设你对 level = 6，想看第 0 个路径（从 0 开始计）
freq_range = denoiser.get_node_frequency_range(node_index=0, fs=fs)
logger.info(f"路径 0 的频率范围是: {freq_range[0]:.2f} Hz 到 {freq_range[1]:.2f} Hz")
