#!/usr/bin/env python3
"""
数据预处理主脚本

支持函数式调用和直接执行两种模式
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# 获取当前文件的绝对路径，并添加其上一级目录到 sys.path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))
sys.path.append(str(current_dir.parent))

from utils.dataprocess.vibration_data_loader import VibrationDataLoader  
from utils.dataprocess.wavelet_denoise import WaveletDenoiser
from utils.dataprocess.start_idx_visualized_select import StartIdxVisualizedSelect
from utils.dataprocess.debiasing import debias_csv_folder
from utils.visualize.data_processor import DataProcessor
from utils.visualize.visualization_generator import VisualizationGenerator
from loguru import logger
from utils.visualize.extract_timepoint import extract_timepoint_data, visualize_grid, export_filename_grid
import pandas as pd
import matplotlib

# Set up the matplotlib backend explicitly
matplotlib.use('TkAgg')  # Use TkAgg backend which has good button support

def setup_logging(log_level: str = "INFO"):
    """设置日志配置"""
    # 创建logs目录
    Path("logs").mkdir(exist_ok=True)
    
    logger.configure(handlers=[
        {"sink": sys.stdout, "level": log_level},
        {"sink": "logs/preprocess.log", "level": log_level, "rotation": "10 MB"}
    ])

def run_preprocessing_pipeline(
    input_dir: str = "./input/data",
    output_dir: str = "./output/data_csv_denoised_start-idx-reselected_debiased",
    csv_output_dir: str = "./output/data_csv",
    denoised_output_dir: str = "./output/data_csv_denoised", 
    start_idx_output_dir: str = "./output/data_csv_denoised_start-idx-reselected",
    wavelet: str = 'db6',
    wavelet_level: int = 6,
    keep_nodes: list = None,
    vg_delay: float = 0.0025,
    truncate_to_min: bool = True,
    rows: int = 4,
    cols: int = 6,
    use_all_points: bool = True,
    npz_output_file: str = "./output/my_processed_data_use_all_points.npz",
    enable_txt_to_csv: bool = True,
    enable_denoising: bool = True,
    enable_start_idx_selection: bool = True,
    enable_debiasing: bool = True,
    enable_data_processing: bool = True,
    verbose: bool = True,
    log_level: str = "INFO"
) -> Dict[str, Any]:
    """
    运行完整的数据预处理流水线
    
    参数:
        input_dir: 原始TXT文件目录
        output_dir: 最终输出目录
        csv_output_dir: CSV转换输出目录
        denoised_output_dir: 去噪输出目录
        start_idx_output_dir: 起始点选择输出目录
        wavelet: 小波类型
        wavelet_level: 小波分解级数
        keep_nodes: 保留的小波节点
        vg_delay: Vg信号延时(秒)
        truncate_to_min: 是否截断到最短长度
        rows: 网格行数
        cols: 网格列数
        use_all_points: 是否使用所有数据点
        npz_output_file: NPZ输出文件路径
        enable_*: 各步骤开关
        verbose: 详细输出
        log_level: 日志级别
    
    返回:
        包含处理结果的字典
    """
    
    # 设置日志
    setup_logging(log_level)
    
    if keep_nodes is None:
        keep_nodes = ['aaaaaa']
    
    # 创建必要目录
    directories = [csv_output_dir, denoised_output_dir, start_idx_output_dir, output_dir]
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    result = {
        'success': True,
        'steps_completed': [],
        'steps_failed': [],
        'metadata': {}
    }
    
    try:
        # 1. TXT文件转换为CSV
        if enable_txt_to_csv:
            logger.info("步骤1: 开始将TXT文件转换为CSV格式")
            VibrationDataLoader.convert_txt_to_csv_batch(input_dir, csv_output_dir)
            
            csv_files = list(Path(csv_output_dir).glob("*.csv"))
            result['steps_completed'].append('txt_to_csv')
            result['metadata']['csv_files_count'] = len(csv_files)
            logger.info(f"TXT转CSV完成，生成 {len(csv_files)} 个文件")
        
        # 2. 小波去噪
        if enable_denoising:
            logger.info("步骤2: 开始进行小波去噪处理")
            denoiser = WaveletDenoiser(wavelet=wavelet, level=wavelet_level, keep_nodes=keep_nodes)
            denoiser.denoise_csv_batch(
                input_folder=csv_output_dir,
                output_folder=denoised_output_dir,
                columns=["Time Signal"]
            )
            
            denoised_files = list(Path(denoised_output_dir).glob("*.csv"))
            result['steps_completed'].append('denoising')
            result['metadata']['denoised_files_count'] = len(denoised_files)
            logger.info(f"小波去噪完成，处理 {len(denoised_files)} 个文件")
        
        # 3. 起始点选择
        if enable_start_idx_selection:
            logger.info("步骤3: 开始进行数据起始点选择")
            processor_idx = StartIdxVisualizedSelect(
                denoised_output_dir,
                start_idx_output_dir,
                vg_delay=vg_delay
            )
            processor_idx.run()
            
            start_idx_files = list(Path(start_idx_output_dir).glob("*.csv"))
            result['steps_completed'].append('start_idx_selection')
            result['metadata']['start_idx_files_count'] = len(start_idx_files)
            logger.info(f"起始点选择完成，处理 {len(start_idx_files)} 个文件")
        
        # 4. 去偏处理
        if enable_debiasing:
            logger.info("步骤4: 开始进行数据去偏处理")
            debias_csv_folder(
                start_idx_output_dir,
                output_dir,
                truncate_to_min=truncate_to_min
            )
            
            debiased_files = list(Path(output_dir).glob("*.csv"))
            result['steps_completed'].append('debiasing')
            result['metadata']['debiased_files_count'] = len(debiased_files)
            logger.info(f"去偏处理完成，生成 {len(debiased_files)} 个文件")
        
        # 5. 数据处理为网格格式并保存NPZ
        if enable_data_processing:
            logger.info("步骤5: 开始数据处理并保存为NPZ格式")
            processor = DataProcessor(
                input_folder=output_dir,
                rows=rows,
                cols=cols,
                use_all_points=use_all_points
            )
            
            # 确保NPZ输出目录存在
            Path(npz_output_file).parent.mkdir(parents=True, exist_ok=True)
            
            processor.save_processed_data(npz_output_file)
            
            result['steps_completed'].append('data_processing')
            result['metadata']['npz_file'] = npz_output_file
            logger.info(f"数据处理完成，已保存到 {npz_output_file}")
        
        result['output_dir'] = output_dir
        result['npz_file'] = npz_output_file if enable_data_processing else None
        logger.success("数据预处理流水线完成！")
        
    except Exception as e:
        logger.error(f"数据预处理失败: {str(e)}")
        result['success'] = False
        result['error'] = str(e)
    
    return result

def main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(description="数据预处理流水线")
    
    # 路径参数
    parser.add_argument("--input-dir", default="./input/data", help="原始TXT文件目录")
    parser.add_argument("--output-dir", default="./output/data_csv_denoised_start-idx-reselected_debiased", help="最终输出目录")
    parser.add_argument("--npz-output", default="./output/my_processed_data_use_all_points.npz", help="NPZ输出文件")
    
    # 处理参数
    parser.add_argument("--wavelet", default="db6", help="小波类型")
    parser.add_argument("--wavelet-level", type=int, default=6, help="小波分解级数")
    parser.add_argument("--vg-delay", type=float, default=0.0025, help="Vg信号延时(秒)")
    parser.add_argument("--rows", type=int, default=4, help="网格行数")
    parser.add_argument("--cols", type=int, default=6, help="网格列数")
    
    # 开关参数
    parser.add_argument("--no-txt-to-csv", action="store_true", help="跳过TXT到CSV转换")
    parser.add_argument("--no-denoising", action="store_true", help="跳过小波去噪")
    parser.add_argument("--no-start-idx", action="store_true", help="跳过起始点选择")
    parser.add_argument("--no-debiasing", action="store_true", help="跳过去偏处理")
    parser.add_argument("--no-data-processing", action="store_true", help="跳过数据处理")
    parser.add_argument("--no-truncate", action="store_true", help="不截断到最短长度")
    parser.add_argument("--no-all-points", action="store_true", help="不使用所有数据点")
    
    # 其他参数
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="日志级别")
    parser.add_argument("--quiet", action="store_true", help="静默模式")
    
    args = parser.parse_args()
    
    # 运行预处理
    result = run_preprocessing_pipeline(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        npz_output_file=args.npz_output,
        wavelet=args.wavelet,
        wavelet_level=args.wavelet_level,
        vg_delay=args.vg_delay,
        rows=args.rows,
        cols=args.cols,
        enable_txt_to_csv=not args.no_txt_to_csv,
        enable_denoising=not args.no_denoising,
        enable_start_idx_selection=not args.no_start_idx,
        enable_debiasing=not args.no_debiasing,
        enable_data_processing=not args.no_data_processing,
        truncate_to_min=not args.no_truncate,
        use_all_points=not args.no_all_points,
        verbose=not args.quiet,
        log_level=args.log_level
    )
    
    # 输出结果
    if result['success']:
        print(f"✓ 预处理完成，输出目录: {result['output_dir']}")
        if result.get('npz_file'):
            print(f"✓ NPZ文件: {result['npz_file']}")
        return 0
    else:
        print(f"✗ 预处理失败: {result.get('error', '未知错误')}")
        return 1

# 兼容性：如果直接运行脚本，使用默认参数
if __name__ == "__main__":
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        # 有参数，使用命令行模式
        sys.exit(main())
    else:
        # 无参数，使用默认参数（向后兼容）
        logger.info("使用默认参数运行数据预处理流水线")
        setup_logging()
        result = run_preprocessing_pipeline()
        if not result['success']:
            sys.exit(1)

