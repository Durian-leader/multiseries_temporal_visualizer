#!/usr/bin/env python3
"""
手动基线矫正处理脚本

此脚本用于在数据处理流程中插入手动基线矫正步骤，位于00select_start_idx.py和01csv2npz.py之间。
支持两种模式：
1. 自动模式：对所有CSV文件自动应用第一点和最后一点的线性基线矫正
2. 手动模式：逐个打开GUI工具，手动选择每个文件的基线点

用法:
    python 00_5_manual_baseline_correction.py -i <输入文件夹> -o <输出文件夹> [选项]

参数:
    -i, --input       输入CSV文件夹路径（00select_start_idx.py的输出）
    -o, --output      输出CSV文件夹路径（01csv2npz.py的输入）
    -m, --manual      启用手动模式（GUI选择基线点）
    -a, --auto        启用自动模式（仅使用首末点）
    -v, --verbose     显示详细处理信息
    -x, --xcol        X轴列名或索引（默认为第一列）
    -y, --ycol        Y轴列名或索引（默认为第二列）
"""

import os
import sys
import argparse
import pandas as pd
import numpy as np
from scipy import interpolate
from pathlib import Path
import time
import tkinter as tk
from tkinter import messagebox, simpledialog
import subprocess

# 导入现有的基线矫正工具
current_dir = Path(__file__).parent
utils_dir = current_dir / "utils" / "dataprocess"
sys.path.insert(0, str(utils_dir))

try:
    from baseline_correction import BaselineCorrectionTool
except ImportError:
    print("警告: 无法导入基线矫正GUI工具，仅支持自动模式")
    BaselineCorrectionTool = None

def auto_baseline_correction(file_path, output_dir, x_col=0, y_col=1, verbose=False):
    """
    自动基线矫正：使用首末两点进行线性基线矫正
    
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
        if verbose:
            print(f"自动处理: {file_path}")
        
        # 读取CSV文件
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
            print(f"  基线点: ({first_x:.4f}, {first_y:.4f}) 到 ({last_x:.4f}, {last_y:.4f})")
        
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
        
        # 创建输出DataFrame
        result_df = pd.DataFrame()
        result_df[x_column] = df[x_column]
        result_df[y_column] = corrected_values
        
        if verbose:
            original_range = f"{y_data.min():.4f} 到 {y_data.max():.4f}"
            corrected_range = f"{corrected_values.min():.4f} 到 {corrected_values.max():.4f}"
            print(f"  矫正范围: {original_range} → {corrected_range}")
        
        # 保存结果
        output_file = output_dir / file_path.name
        result_df.to_csv(output_file, index=False)
        
        if verbose:
            print(f"  已保存: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"处理 {file_path} 时出错: {str(e)}")
        return False

def manual_baseline_correction(file_path, output_dir, verbose=False):
    """
    手动基线矫正：打开GUI工具进行手动选择
    
    参数:
        file_path (Path): 输入CSV文件路径
        output_dir (Path): 输出目录路径
        verbose (bool): 是否显示详细信息
    
    返回:
        bool: 处理成功返回True，否则返回False
    """
    if BaselineCorrectionTool is None:
        print("错误: GUI工具不可用，请使用自动模式")
        return False
    
    try:
        if verbose:
            print(f"手动处理: {file_path}")
        
        # 创建临时GUI应用
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        # 显示处理信息
        response = messagebox.askyesnocancel(
            "手动基线矫正",
            f"准备处理文件: {file_path.name}\n\n"
            f"是否需要手动调整基线？\n\n"
            f"YES - 打开GUI工具手动选择基线点\n"
            f"NO - 使用自动模式（首末点连线）\n"
            f"CANCEL - 跳过此文件"
        )
        
        if response is None:  # Cancel
            print(f"  跳过文件: {file_path}")
            root.destroy()
            return True
        elif response is False:  # No - 自动模式
            root.destroy()
            return auto_baseline_correction(file_path, output_dir, verbose=verbose)
        
        # Yes - 手动模式
        root.destroy()
        
        # 启动GUI工具
        gui_root = tk.Tk()
        app = BaselineCorrectionTool(gui_root)
        
        # 自动加载文件
        df = pd.read_csv(file_path)
        app.original_data = df
        app.corrected_data = df.copy()
        app.x_column = df.columns[0]
        app.y_column = df.columns[1]
        app.file_name = file_path.name
        app.selected_points = []
        app.baseline_data = None
        
        # 更新状态和图表
        app.status_label['text'] = f"已加载: {app.file_name}"
        app.update_plots()
        
        # 运行GUI
        gui_root.mainloop()
        
        # 检查是否有矫正数据
        if app.corrected_data is not None and "corrected" in app.corrected_data:
            # 保存矫正后的数据
            result_df = pd.DataFrame()
            result_df[app.x_column] = app.corrected_data[app.x_column]
            result_df[app.y_column] = app.corrected_data["corrected"]
            
            output_file = output_dir / file_path.name
            result_df.to_csv(output_file, index=False)
            
            if verbose:
                print(f"  手动矫正完成，已保存: {output_file}")
            return True
        else:
            # 没有矫正数据，使用自动模式作为后备
            print(f"  未进行矫正，使用自动模式处理: {file_path}")
            return auto_baseline_correction(file_path, output_dir, verbose=verbose)
        
    except Exception as e:
        print(f"手动处理 {file_path} 时出错: {str(e)}")
        return False

def main():
    """主函数"""
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="CSV文件基线矫正处理")
    parser.add_argument("-i", "--input", required=True, help="输入CSV文件夹路径")
    parser.add_argument("-o", "--output", required=True, help="输出CSV文件夹路径")
    parser.add_argument("-m", "--manual", action="store_true", help="启用手动模式（GUI选择基线点）")
    parser.add_argument("-a", "--auto", action="store_true", help="启用自动模式（仅使用首末点）")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细处理信息")
    parser.add_argument("-x", "--xcol", default=0, help="X轴列名或索引（默认为第一列）")
    parser.add_argument("-y", "--ycol", default=1, help="Y轴列名或索引（默认为第二列）")
    
    args = parser.parse_args()
    
    # 检查模式参数
    if not args.manual and not args.auto:
        print("请指定处理模式: -m (手动) 或 -a (自动)")
        return 1
        
    if args.manual and args.auto:
        print("不能同时指定手动和自动模式")
        return 1
    
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
    
    # 获取所有CSV文件
    csv_files = [f for f in input_dir.glob("*.csv") if f.is_file()]
    
    if not csv_files:
        print(f"在 '{input_dir}' 中没有找到CSV文件")
        return 0
    
    # 按文件名排序
    csv_files.sort()
    
    print(f"找到 {len(csv_files)} 个CSV文件待处理")
    print(f"处理模式: {'手动' if args.manual else '自动'}")
    
    # 处理统计
    start_time = time.time()
    success_count = 0
    
    # 处理每个文件
    for i, file_path in enumerate(csv_files, 1):
        print(f"\n[{i}/{len(csv_files)}] 处理文件: {file_path.name}")
        
        if args.manual:
            success = manual_baseline_correction(file_path, output_dir, args.verbose)
        else:
            success = auto_baseline_correction(file_path, output_dir, args.xcol, args.ycol, args.verbose)
        
        if success:
            success_count += 1
    
    # 输出统计信息
    elapsed_time = time.time() - start_time
    print(f"\n处理完成:")
    print(f"  成功: {success_count}/{len(csv_files)} 个文件")
    print(f"  总耗时: {elapsed_time:.2f} 秒")
    print(f"  输出目录: {output_dir}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())