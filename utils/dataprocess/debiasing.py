import os
import glob
import pandas as pd
import numpy as np
import argparse
from pathlib import Path
from loguru import logger
import sys

def shift_columns_to_zero(df):
    """
    处理DataFrame中的每一列，使其第一个值为0
    
    Args:
        df: 输入的DataFrame
        
    Returns:
        处理后的DataFrame，每列的第一个值都为0
    """
    df_shifted = df.copy()
    
    # 对每一列进行处理
    for col in df.columns:
        # 获取该列的第一个值
        first_val = df[col].iloc[0]
        # 将该列的所有值减去第一个值
        df_shifted[col] = df[col] - first_val
        
    return df_shifted

def find_min_length(input_folder):
    """
    找出文件夹中所有CSV文件的最小行数
    
    Args:
        input_folder: 包含CSV文件的输入文件夹路径
        
    Returns:
        最小行数和对应的文件名
    """
    # 获取输入文件夹中的所有CSV文件
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))
    
    if not csv_files:
        logger.error(f"在 {input_folder} 中没有找到CSV文件")
        raise ValueError(f"在 {input_folder} 中没有找到CSV文件")
    
    # 初始化最小行数为一个很大的数
    min_length = float('inf')
    min_file = ""
    
    # 遍历每个文件，找出最小行数
    for file_path in csv_files:
        try:
            # 使用pandas读取文件并获取行数
            df = pd.read_csv(file_path)
            length = len(df)
            
            if length < min_length:
                min_length = length
                min_file = os.path.basename(file_path)
                
        except Exception as e:
            logger.error(f"读取文件 {file_path} 时出错: {e}")
    
    logger.info(f"最短文件是 {min_file}，行数为 {min_length}")
    return min_length, min_file

def debias_csv_folder(input_folder, output_folder, truncate_to_min=False):
    """
    处理输入文件夹中的所有CSV文件，将每列数据偏移到以第一个值为0
    
    Args:
        input_folder: 包含CSV文件的输入文件夹路径
        output_folder: 处理后文件的输出文件夹路径
        truncate_to_min: 是否将所有文件截断为最短文件的长度
    """
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)
    
    # 获取输入文件夹中的所有CSV文件
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))
    
    if not csv_files:
        logger.warning(f"在 {input_folder} 中没有找到CSV文件")
        return
    
    logger.info(f"找到 {len(csv_files)} 个CSV文件")
    
    # 如果需要截断文件，先找出最小行数
    min_length = None
    if truncate_to_min:
        min_length, min_file = find_min_length(input_folder)
        logger.info(f"将截断所有文件到 {min_length} 行 (与 {min_file} 一致)")
    
    # 处理每个文件
    for file_path in csv_files:
        try:
            # 获取文件名
            file_name = os.path.basename(file_path)
            logger.info(f"处理文件: {file_name}")
            
            # 读取CSV文件
            df = pd.read_csv(file_path)
            
            # 如果需要截断文件
            if truncate_to_min and len(df) > min_length:
                logger.info(f"截断文件 {file_name} 从 {len(df)} 行到 {min_length} 行")
                df = df.iloc[:min_length]
            
            # 偏移每列，使第一个值为0
            df_shifted = shift_columns_to_zero(df)
            
            # 保存处理后的文件
            output_path = os.path.join(output_folder, file_name)
            df_shifted.to_csv(output_path, index=False)
            
            logger.info(f"已保存到: {output_path}")
            
        except Exception as e:
            logger.error(f"处理文件 {file_path} 时出错: {e}")
    
    logger.info(f"所有文件处理完成。结果保存在: {output_folder}")

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='将CSV文件中的每一列数据偏移，使其第一个值为0')
    parser.add_argument('--input', '-i', required=True, help='输入文件夹路径（包含CSV文件）')
    parser.add_argument('--output', '-o', required=True, help='输出文件夹路径（存放处理后的CSV文件）')
    parser.add_argument('--truncate', '-t', action='store_true', help='将所有文件截断为最短文件的长度')
    
    args = parser.parse_args()
    
    # 处理文件夹
    debias_csv_folder(args.input, args.output, truncate_to_min=args.truncate)

if __name__ == "__main__":
    logger.configure(
    handlers=[
        {"sink": sys.stdout, "level": "INFO"},
        {"sink": "vibration_data_loader.log", "level": "DEBUG", "rotation": "10 MB"},
        ]
    )
    input_folder = "./output/data_csv_start-idx-reselected"
    output_folder = "./output/data_csv_start-idx-reselected_debiased"
    debias_csv_folder(input_folder, output_folder, truncate_to_min=True)
