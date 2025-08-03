import os
import glob
import re
import numpy as np
import pandas as pd
import scipy.interpolate as interp
from loguru import logger
from typing import List, Dict, Tuple, Optional, Union
from pathlib import Path
import sys
import argparse
import matplotlib.pyplot as plt

# # 设置日志
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger('DataProcessor')

class DataProcessor:
    """
    处理时间序列数据的类
    
    功能包括:
    - 从CSV文件加载数据
    - 创建文件路径网格
    - 数据插值和同步
    """
    
    def __init__(self,
                 input_folder: str = None,
                 rows: int = None,
                 cols: int = None,
                 sampling_points: int = 500,
                 use_all_points: bool = False):
        """
        初始化数据处理器
        
        Args:
            input_folder: 包含CSV文件的输入文件夹路径
            rows: 数据网格的行数
            cols: 数据网格的列数
            sampling_points: 采样点数量（仅在use_all_points=False时使用）
            use_all_points: 是否使用所有原始数据点而不进行降采样
        """
        self.input_folder = input_folder
        self.rows = rows
        self.cols = cols
        self.sampling_points = sampling_points
        self.use_all_points = use_all_points
        
        # 数据容器
        self.file_paths_grid = None
        self.filename_grid = None
        self.data = {}
        self.grid_data = None
        self.time_points = None
        self.min_signal = float('inf')
        self.max_signal = float('-inf')
        self.min_time = float('inf')
        self.max_time = float('-inf')
        
        # 初始化数据
        if self.input_folder:
            logger.info("初始化DataProcessor...")
            self._create_file_grid()
            self._load_data()
            self._synchronize_time_points()
    
    def _create_file_grid(self):
        """创建文件路径网格，使用自然排序"""
        logger.info(f"从 {self.input_folder} 创建文件网格...")
        
        # 获取所有CSV文件
        csv_files = glob.glob(os.path.join(self.input_folder, "*.csv"))
        
        if not csv_files:
            raise ValueError(f"在 {self.input_folder} 中没有找到CSV文件")
        
        # 自然排序函数
        def natural_sort_key(s):
            return [int(text) if text.isdigit() else text.lower() 
                    for text in re.split(r'(\d+)', os.path.basename(s))]
        
        # 排序文件
        csv_files.sort(key=natural_sort_key)
        
        # 初始化空网格
        self.file_paths_grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.filename_grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        
        # 按行优先顺序填充网格
        for idx, file_path in enumerate(csv_files):
            if idx >= self.rows * self.cols:
                logger.warning(f"文件数量({len(csv_files)})超过网格大小({self.rows}×{self.cols})，将截断")
                break
                
            row = idx // self.cols
            col = idx % self.cols
            self.file_paths_grid[row][col] = file_path
            self.filename_grid[row][col] = os.path.basename(file_path)
        
        logger.info(f"创建了 {self.rows}×{self.cols} 的文件网格")
    
    def _load_data(self):
        """从所有CSV文件加载数据"""
        logger.info("加载数据...")
        
        for i in range(self.rows):
            for j in range(self.cols):
                file_path = self.file_paths_grid[i][j]
                
                # 跳过空单元格
                if file_path is None or not file_path:
                    continue
                
                try:
                    # 读取CSV文件
                    df = pd.read_csv(file_path)
                    
                    # 确保至少有2列
                    if len(df.columns) < 2:
                        logger.warning(f"文件 {file_path} 的列数少于2列")
                        continue
                    
                    # 假设第一列是时间，第二列是信号
                    time_col = df.columns[0]
                    signal_col = df.columns[1]
                    
                    # 转换为数值
                    df[time_col] = pd.to_numeric(df[time_col], errors='coerce')
                    df[signal_col] = pd.to_numeric(df[signal_col], errors='coerce')
                    
                    # 删除NaN值
                    df = df.dropna(subset=[time_col, signal_col])
                    
                    # 如果没有数据则跳过
                    if len(df) == 0:
                        logger.warning(f"文件 {file_path} 中没有有效数据")
                        continue
                    
                    # 更新最小/最大值
                    self.min_time = min(self.min_time, df[time_col].min())
                    self.max_time = max(self.max_time, df[time_col].max())
                    self.min_signal = min(self.min_signal, df[signal_col].min())
                    self.max_signal = max(self.max_signal, df[signal_col].max())
                    
                    # 存储数据
                    self.data[(i, j)] = {
                        'file_path': file_path,
                        'filename': os.path.basename(file_path),
                        'time': df[time_col].values,
                        'signal': df[signal_col].values
                    }
                    
                except Exception as e:
                    logger.error(f"处理文件 {file_path} 时出错: {e}")
        
        if not self.data:
            raise ValueError("没有找到有效的数据文件")
            
        logger.info(f"加载了 {len(self.data)} 个文件的数据")
        logger.info(f"时间范围: {self.min_time:.4f} 到 {self.max_time:.4f}")
        logger.info(f"信号范围: {self.min_signal:.4f} 到 {self.max_signal:.4f}")
    
    def _synchronize_time_points(self):
        """创建公共时间点并将所有信号插值到这些点"""
        logger.info("同步时间点...")
        
        if self.use_all_points:
            # 收集所有唯一的时间点
            all_time_points = set()
            for (i, j), item in self.data.items():
                all_time_points.update(item['time'])
            
            # 转换为排序的数组
            self.time_points = np.array(sorted(all_time_points))
            logger.info(f"使用所有原始数据点: {len(self.time_points)} 个时间点")
        else:
            # 创建等间隔的时间点
            self.time_points = np.linspace(self.min_time, self.max_time, self.sampling_points)
            logger.info(f"创建了 {len(self.time_points)} 个等间隔时间点")
        
        # 预分配3D网格数据: [时间, 行, 列]
        self.grid_data = np.full((len(self.time_points), self.rows, self.cols), np.nan)
        
        # 将每个信号插值到公共时间点
        for (i, j), item in self.data.items():
            # 创建插值函数(线性插值)
            f = interp.interp1d(
                item['time'], 
                item['signal'], 
                bounds_error=False, 
                fill_value=(item['signal'][0], item['signal'][-1])
            )
            
            # 插值到公共时间点
            interpolated_signal = f(self.time_points)
            
            # 存储到3D网格
            self.grid_data[:, i, j] = interpolated_signal
            
            # 同时存储到原始数据字典
            item['interp_signal'] = interpolated_signal
        
        logger.info(f"完成了 {len(self.time_points)} 个时间点的数据同步")
    
    def get_processed_data(self) -> Dict:
        """
        获取处理后的数据
        
        Returns:
            Dict: 包含处理后数据的字典
        """
        return {
            'grid_data': self.grid_data,
            'time_points': self.time_points,
            'min_signal': self.min_signal,
            'max_signal': self.max_signal,
            'min_time': self.min_time,
            'max_time': self.max_time,
            'rows': self.rows,
            'cols': self.cols,
            'filename_grid': self.filename_grid,
            'data': self.data
        }
    
    def save_processed_data(self, output_file: str = 'processed_data.npz'):
        """
        保存处理后的数据到文件
        
        Args:
            output_file: 输出文件路径
        """
        logger.info(f"保存处理后的数据到 {output_file}")
        
        # 将文件名网格转换为numpy数组以便保存
        filename_array = np.array(self.filename_grid, dtype=object)
        
        # 只保存 numpy 数组和基本类型
        np.savez(
            output_file,
            grid_data=self.grid_data,
            time_points=self.time_points,
            min_signal=self.min_signal,
            max_signal=self.max_signal,
            min_time=self.min_time,
            max_time=self.max_time,
            rows=self.rows,
            cols=self.cols,
            filename_grid=filename_array
        )
        
        logger.info(f"数据已保存")
    
    def load_processed_data(self, input_file: str):
        """
        从文件加载处理后的数据
        
        Args:
            input_file: 输入文件路径
        """
        logger.info(f"从 {input_file} 加载处理后的数据")
        
        try:
            data = np.load(input_file, allow_pickle=True)

            self.rows = int(data['rows'])
            self.cols = int(data['cols'])
            self.use_all_points = True
            self.sampling_points = len(data['time_points'])

            self.grid_data = data['grid_data']
            self.time_points = data['time_points']
            self.min_signal = float(data['min_signal'])
            self.max_signal = float(data['max_signal'])
            self.min_time = float(data['min_time'])
            self.max_time = float(data['max_time'])


            
            # 加载文件名网格（如果存在）
            if 'filename_grid' in data:
                self.filename_grid = data['filename_grid'].tolist()
                logger.info(f"已加载文件名网格")
            else:
                self.filename_grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
                logger.warning(f"输入文件中没有文件名网格，已创建空网格")
            
            logger.info(f"已加载处理后的数据，形状: {self.grid_data.shape}")
            logger.info(f"时间范围: {self.min_time:.4f} 到 {self.max_time:.4f}")
            logger.info(f"信号范围: {self.min_signal:.4f} 到 {self.max_signal:.4f}")
            
            return True
            
        except Exception as e:
            logger.error(f"加载数据时出错: {e}")
            return False
    
    def get_time_at_index(self, index: int) -> float:
        """
        获取指定索引的时间点
        
        Args:
            index: 时间点索引
            
        Returns:
            float: 对应的时间值
        """
        if index < 0 or index >= len(self.time_points):
            raise ValueError(f"索引 {index} 超出范围 [0, {len(self.time_points)-1}]")
            
        return self.time_points[index]
    
    def find_nearest_time_index(self, target_time: float) -> int:
        """
        找到最接近目标时间的时间点索引
        
        Args:
            target_time: 目标时间
            
        Returns:
            int: 最接近的时间点索引
        """
        return np.abs(self.time_points - target_time).argmin()


# 示例用法
if __name__ == "__main__":

    logger.configure(
        handlers=[
            {"sink": sys.stdout, "level": "INFO"},
            {"sink": "vibration_data_loader.log", "level": "DEBUG", "rotation": "10 MB"},
            ]
        )
    # 创建数据处理器
    processor = DataProcessor(
        input_folder="./output/data_csv_start-idx-reselected_debiased",
        rows=6,
        cols=6,
        sampling_points=500
    )
    
    # 保存处理后的数据
    processor.save_processed_data("my_processed_data.npz")
    
    # 使用所有原始数据点的示例
    processor_all_points = DataProcessor(
        input_folder="./output/data_csv_start-idx-reselected_debiased",
        rows=6,
        cols=6,
        use_all_points=True
    )
    
    # 保存处理后的数据
    processor_all_points.save_processed_data("my_processed_data_all_points.npz")
    
    # 创建新的处理器并加载数据
    new_processor = DataProcessor()
    
    # 加载之前保存的数据
    new_processor.load_processed_data("my_processed_data_all_points.npz")
    
    # 获取处理后的数据
    processed_data = new_processor.get_processed_data()
    
    print(f"网格数据形状: {processed_data['grid_data'].shape}")
    print(f"时间点数量: {len(processed_data['time_points'])}")
