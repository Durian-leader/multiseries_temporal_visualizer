#!/usr/bin/env python3
"""
CSV到NPZ数据转换脚本

支持函数式调用和直接执行两种模式
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np

# 设置路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))
sys.path.append(str(current_dir.parent))

from utils.dataprocess.vibration_data_loader import VibrationDataLoader  
from utils.dataprocess.start_idx_visualized_select import StartIdxVisualizedSelect
from utils.dataprocess.debiasing import debias_csv_folder
from utils.visualize.data_processor import DataProcessor
from utils.visualize.visualization_generator import VisualizationGenerator
from loguru import logger
from utils.visualize.extract_timepoint import extract_timepoint_data, visualize_grid, export_filename_grid
import pandas as pd
import matplotlib

# Set up the matplotlib backend explicitly
matplotlib.use('TkAgg')

def setup_logging(log_level: str = "INFO"):
    """设置日志配置"""
    Path("logs").mkdir(exist_ok=True)
    
    logger.configure(handlers=[
        {"sink": sys.stdout, "level": log_level},
        {"sink": "logs/csv2npz.log", "level": log_level, "rotation": "10 MB"}
    ])

def convert_csv_to_npz(
    input_folder: str = "./output/data_csv_denoised_start-idx-reselected_debiased",
    output_file: str = "./output/my_processed_data_use_all_points.npz",
    rows: int = 6,
    cols: int = 6,
    use_all_points: bool = True,
    verbose: bool = True,
    log_level: str = "INFO"
) -> Dict[str, Any]:
    """
    将CSV文件转换为NPZ格式
    
    参数:
        input_folder: 输入CSV文件夹路径
        output_file: 输出NPZ文件路径
        rows: 网格行数
        cols: 网格列数
        use_all_points: 是否使用所有数据点
        verbose: 详细输出
        log_level: 日志级别
    
    返回:
        包含转换结果的字典
    """
    
    # 设置日志
    setup_logging(log_level)
    
    result = {
        'success': True,
        'metadata': {}
    }
    
    try:
        logger.info("开始CSV到NPZ转换")
        logger.info(f"输入文件夹: {input_folder}")
        logger.info(f"输出文件: {output_file}")
        logger.info(f"网格尺寸: {rows}x{cols}")
        logger.info(f"使用所有点: {use_all_points}")
        
        # 检查输入文件夹
        input_path = Path(input_folder)
        if not input_path.exists():
            raise FileNotFoundError(f"输入文件夹不存在: {input_folder}")
        
        # 检查CSV文件
        csv_files = list(input_path.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"在 {input_folder} 中未找到CSV文件")
        
        logger.info(f"找到 {len(csv_files)} 个CSV文件")
        
        # 确保输出目录存在
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 使用DataProcessor处理数据并组织为网格结构
        logger.info("开始处理数据并组织为网格结构")
        processor = DataProcessor(
            input_folder=input_folder,
            rows=rows,
            cols=cols,
            use_all_points=use_all_points
        )
        
        # 保存处理后的数据
        processor.save_processed_data(output_file)
        
        # 验证输出文件
        if output_path.exists():
            # 读取数据获取元信息
            data = np.load(output_file, allow_pickle=True)
            
            result['metadata'] = {
                'output_file': output_file,
                'input_files_count': len(csv_files),
                'grid_shape': data['grid_data'].shape if 'grid_data' in data else None,
                'time_points_count': len(data['time_points']) if 'time_points' in data else 0,
                'data_keys': list(data.keys()),
                'file_size': output_path.stat().st_size
            }
            
            logger.info(f"转换完成！NPZ文件已保存到: {output_file}")
            if 'grid_data' in data:
                logger.info(f"网格数据形状: {data['grid_data'].shape}")
            if 'time_points' in data:
                logger.info(f"时间点数量: {len(data['time_points'])}")
            
            result['output_file'] = output_file
            
        else:
            raise FileNotFoundError("NPZ文件未生成")
            
    except Exception as e:
        logger.error(f"CSV到NPZ转换失败: {str(e)}")
        result['success'] = False
        result['error'] = str(e)
    
    return result

def main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(description="CSV到NPZ数据转换")
    
    # 路径参数
    parser.add_argument("--input-folder", default="./output/data_csv_denoised_start-idx-reselected_debiased",
                       help="输入CSV文件夹路径")
    parser.add_argument("--output-file", default="./output/my_processed_data_use_all_points.npz",
                       help="输出NPZ文件路径")
    
    # 处理参数
    parser.add_argument("--rows", type=int, default=6, help="网格行数")
    parser.add_argument("--cols", type=int, default=6, help="网格列数")
    parser.add_argument("--no-all-points", action="store_true", help="不使用所有数据点")
    
    # 其他参数
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="日志级别")
    parser.add_argument("--quiet", action="store_true", help="静默模式")
    
    args = parser.parse_args()
    
    # 运行转换
    result = convert_csv_to_npz(
        input_folder=args.input_folder,
        output_file=args.output_file,
        rows=args.rows,
        cols=args.cols,
        use_all_points=not args.no_all_points,
        verbose=not args.quiet,
        log_level=args.log_level
    )
    
    # 输出结果
    if result['success']:
        print(f"✓ CSV到NPZ转换完成: {result['output_file']}")
        return 0
    else:
        print(f"✗ CSV到NPZ转换失败: {result.get('error', '未知错误')}")
        return 1

# 兼容性：如果直接运行脚本，使用默认参数
if __name__ == "__main__":
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        # 有参数，使用命令行模式
        sys.exit(main())
    else:
        # 无参数，使用默认参数（向后兼容）
        logger.info("使用默认参数运行CSV到NPZ转换")
        setup_logging()
        result = convert_csv_to_npz()
        if not result['success']:
            sys.exit(1)