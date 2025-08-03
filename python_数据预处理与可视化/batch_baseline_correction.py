#!/usr/bin/env python3
"""
批量基线矫正脚本

此脚本用于批量处理指定文件夹中的所有CSV文件，对每个文件执行基线矫正。
基线将使用每个文件的第一个点和最后一个点连线作为基准。
处理后的文件将保存到指定的输出文件夹中，仅包含原始X列和矫正后的Y列。

用法:
    python batch_baseline_correction.py -i <输入文件夹> -o <输出文件夹> [选项]

可选参数:
    -v, --verbose     显示详细处理信息
    -e, --extension   指定要处理的文件扩展名（默认为.csv）
    -x, --xcol        指定X轴列名或索引（默认为第一列）
    -y, --ycol        指定Y轴列名或索引（默认为第二列）
    -p, --prefix      输出文件名前缀（默认为"corrected_"）
"""

import os
import sys
import argparse
import pandas as pd
import numpy as np
from scipy import interpolate
from pathlib import Path
import time

def process_file(file_path, output_dir, x_col=0, y_col=1, prefix="corrected_", verbose=False):
    """
    处理单个CSV文件并应用基线矫正
    
    参数:
        file_path (Path): 输入CSV文件路径
        output_dir (Path): 输出目录路径
        x_col (str|int): X轴列名或索引
        y_col (str|int): Y轴列名或索引
        verbose (bool): 是否显示详细信息
    
    返回:
        bool: 处理成功返回True，否则返回False
    """
    try:
        # 读取CSV文件
        if verbose:
            print(f"正在处理: {file_path}")
        
        # 尝试读取CSV
        df = pd.read_csv(file_path)
        
        # 确定X和Y列
        x_column = x_col if isinstance(x_col, str) else df.columns[x_col]
        y_column = y_col if isinstance(y_col, str) else df.columns[y_col]
        
        if verbose:
            print(f"  X列: {x_column}, Y列: {y_column}")
            print(f"  数据点数: {len(df)}")
        
        # 获取第一个点和最后一个点
        first_x = df[x_column].iloc[0]
        first_y = df[y_column].iloc[0]
        last_x = df[x_column].iloc[-1]
        last_y = df[y_column].iloc[-1]
        
        if verbose:
            print(f"  第一个点: ({first_x}, {first_y})")
            print(f"  最后一个点: ({last_x}, {last_y})")
        
        # 创建线性插值函数
        baseline_x = [first_x, last_x]
        baseline_y = [first_y, last_y]
        f = interpolate.interp1d(baseline_x, baseline_y, bounds_error=False, fill_value="extrapolate")
        
        # 计算基线值
        x_data = df[x_column].values
        baseline_values = f(x_data)
        
        # 计算矫正后的值
        y_data = df[y_column].values
        corrected_values = y_data - baseline_values
        
        # 创建一个新的DataFrame，只包含X列和矫正后的Y列
        result_df = pd.DataFrame()
        result_df[x_column] = df[x_column]  # 保留原始X列
        result_df[y_column] = corrected_values  # Y列替换为矫正后的值
        
        if verbose:
            print(f"  基线计算完成: 从 {y_data.min():.2f}-{y_data.max():.2f} 矫正到 {corrected_values.min():.2f}-{corrected_values.max():.2f}")
        
        # 创建输出文件路径
        output_file = output_dir / f"{prefix}{file_path.name}"
        
        # 保存结果
        result_df.to_csv(output_file, index=False)
        
        if verbose:
            print(f"  已保存到: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"处理 {file_path} 时出错: {str(e)}")
        return False

def main():
    """主函数"""
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="批量处理CSV文件并进行基线矫正")
    parser.add_argument("-i", "--input", required=True, help="输入文件夹路径")
    parser.add_argument("-o", "--output", required=True, help="输出文件夹路径")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细处理信息")
    parser.add_argument("-e", "--extension", default=".csv", help="要处理的文件扩展名（默认为.csv）")
    parser.add_argument("-x", "--xcol", default=0, help="X轴列名或索引（默认为第一列）")
    parser.add_argument("-y", "--ycol", default=1, help="Y轴列名或索引（默认为第二列）")
    parser.add_argument("-p", "--prefix", default="corrected_", help="输出文件名前缀（默认为'corrected_'）")
    
    args = parser.parse_args()
    
    # 转换为Path对象
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    
    # 检查输入目录
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"错误: 输入路径 '{input_dir}' 不存在或不是一个目录")
        return 1
    
    # 确保输出目录存在
    if not output_dir.exists():
        if args.verbose:
            print(f"创建输出目录: {output_dir}")
        output_dir.mkdir(parents=True)
    
    # 获取所有匹配的CSV文件
    csv_files = [f for f in input_dir.glob(f"*{args.extension}") if f.is_file()]
    
    if not csv_files:
        print(f"在 '{input_dir}' 中没有找到扩展名为 '{args.extension}' 的文件")
        return 0
    
    print(f"找到 {len(csv_files)} 个待处理文件")
    
    # 处理统计
    start_time = time.time()
    success_count = 0
    
    # 处理每个文件
    for file_path in csv_files:
        if process_file(file_path, output_dir, args.xcol, args.ycol, args.prefix, args.verbose):
            success_count += 1
    
    # 输出统计信息
    elapsed_time = time.time() - start_time
    print(f"处理完成: {success_count}/{len(csv_files)} 个文件成功")
    print(f"总耗时: {elapsed_time:.2f} 秒")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

# python batch_baseline_correction.py -i output\data_csv_denoised_start-idx-reselected_debiased -o output\data_3