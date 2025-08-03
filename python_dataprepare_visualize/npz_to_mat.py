#!/usr/bin/env python3
"""
NPZ到MATLAB文件转换脚本

支持函数式调用和直接执行两种模式
"""

import numpy as np
import scipy.io as sio
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

def setup_logging(log_level: str = "INFO"):
    """设置日志配置"""
    logger.remove()
    logger.configure(
        handlers=[
            {"sink": sys.stdout, "level": log_level},
            {"sink": "logs/npz_to_mat.log", "level": "DEBUG", "rotation": "10 MB"},
        ]
    )

def convert_npz_to_mat(
    input_file: str = "output/my_processed_data_use_all_points.npz",
    output_file: str = "my_processed_data.mat",
    include_metadata: bool = True,
    verbose: bool = True,
    log_level: str = "INFO"
) -> Dict[str, Any]:
    """
    将NPZ文件转换为MATLAB MAT格式
    
    参数:
        input_file: 输入NPZ文件路径
        output_file: 输出MAT文件路径
        include_metadata: 是否包含元数据
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
        logger.info("开始NPZ到MAT转换")
        logger.info(f"输入文件: {input_file}")
        logger.info(f"输出文件: {output_file}")
        logger.info(f"包含元数据: {include_metadata}")
        
        # 检查输入文件
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"输入NPZ文件不存在: {input_file}")
        
        # 确保输出目录存在
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载NPZ文件
        logger.info(f"正在加载NPZ文件: {input_file}")
        data = np.load(input_file, allow_pickle=True)
        
        # 检查必要的键是否存在
        if 'grid_data' not in data or 'time_points' not in data:
            raise ValueError("NPZ文件中缺少必要的数据：grid_data 或 time_points")
        
        # 准备MAT文件的数据结构
        mat_data = {
            # 核心数据 - 用于3D可视化的三维数组和时间点
            'grid_data': data['grid_data'],      # 3D数组 [时间, 行, 列]
            'time_points': data['time_points'],  # 时间点数组
        }
        
        # 获取数组形状信息
        time_len, rows, cols = data['grid_data'].shape
        logger.info(f"数据形状: 时间点 = {time_len}, 行 = {rows}, 列 = {cols}")
        
        # 添加额外的元数据（如果需要）
        if include_metadata:
            # 添加各种元数据
            metadata_keys = [
                'min_signal', 'max_signal', 'min_time', 'max_time', 
                'rows', 'cols'
            ]
            
            for key in metadata_keys:
                if key in data:
                    value = data[key]
                    # 确保标量值正确转换为MATLAB可读格式
                    if hasattr(value, 'size') and value.size == 1:
                        mat_data[key] = float(value)
                    else:
                        mat_data[key] = value
                    logger.debug(f"添加元数据: {key} = {mat_data[key]}")
        
        # 保存MAT文件
        logger.info(f"正在保存MAT文件: {output_file}")
        sio.savemat(output_file, mat_data)
        
        # 验证输出文件
        if output_path.exists():
            # 获取文件信息
            try:
                mat_info = sio.whosmat(output_file)
                variables_info = [(name, shape, dtype) for name, shape, dtype in mat_info]
                
                result['metadata'] = {
                    'output_file': output_file,
                    'input_file': input_file,
                    'variables': variables_info,
                    'file_size': output_path.stat().st_size,
                    'grid_shape': (time_len, rows, cols),
                    'time_points_count': time_len,
                    'include_metadata': include_metadata
                }
                
                logger.info("MAT文件转换完成！")
                logger.info(f"输出文件: {output_file}")
                logger.info(f"文件大小: {result['metadata']['file_size']:,} bytes")
                logger.info("包含的变量:")
                for name, shape, dtype in variables_info:
                    logger.info(f"  {name}: {shape} ({dtype})")
                
                result['output_file'] = output_file
                
            except Exception as e:
                logger.warning(f"无法读取MAT文件信息: {e}")
                # 即使无法读取信息，文件可能仍然有效
                result['output_file'] = output_file
                result['metadata']['output_file'] = output_file
                result['metadata']['file_size'] = output_path.stat().st_size
        else:
            raise FileNotFoundError("MAT文件未生成")
            
    except Exception as e:
        logger.error(f"NPZ到MAT转换失败: {str(e)}")
        result['success'] = False
        result['error'] = str(e)
    
    return result

def main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(description="NPZ到MATLAB文件转换")
    
    # 路径参数
    parser.add_argument("--input-file", default="output/my_processed_data_use_all_points.npz",
                       help="输入NPZ文件路径")
    parser.add_argument("--output-file", default="my_processed_data.mat",
                       help="输出MAT文件路径")
    
    # 处理参数
    parser.add_argument("--no-metadata", action="store_true", help="不包含元数据")
    
    # 其他参数
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="日志级别")
    parser.add_argument("--quiet", action="store_true", help="静默模式")
    
    args = parser.parse_args()
    
    # 运行转换
    result = convert_npz_to_mat(
        input_file=args.input_file,
        output_file=args.output_file,
        include_metadata=not args.no_metadata,
        verbose=not args.quiet,
        log_level=args.log_level
    )
    
    # 输出结果
    if result['success']:
        print(f"✓ NPZ到MAT转换完成: {result['output_file']}")
        return 0
    else:
        print(f"✗ NPZ到MAT转换失败: {result.get('error', '未知错误')}")
        return 1

# 兼容性：如果直接运行脚本，使用默认参数
if __name__ == "__main__":
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        # 有参数，使用命令行模式
        sys.exit(main())
    else:
        # 无参数，使用默认参数（向后兼容）
        logger.info("使用默认参数运行NPZ到MAT转换")
        
        # 使用更符合现有代码的默认路径
        input_npz_file = "output/my_processed_data_use_all_points.npz"
        output_mat_file = "my_processed_data.mat"
        include_metadata = True
        
        result = convert_npz_to_mat(
            input_file=input_npz_file,
            output_file=output_mat_file,
            include_metadata=include_metadata
        )
        
        if not result['success']:
            sys.exit(1)