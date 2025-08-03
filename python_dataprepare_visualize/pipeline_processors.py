#!/usr/bin/env python3
"""
统一数据处理流水线接口模块

这个模块提供统一的接口来调用各个数据处理步骤，使得notebook和脚本调用更加一致。
每个处理器都提供标准化的配置参数和返回值。
"""

import os
import sys
import numpy as np
import pandas as pd
import scipy.io as sio
from pathlib import Path
from loguru import logger
from typing import Dict, Any, Optional, Tuple, List, Union
import argparse
import time
import warnings

# 添加工具模块路径
current_dir = Path(__file__).parent
utils_dir = current_dir / "utils"
sys.path.insert(0, str(utils_dir))
sys.path.insert(0, str(current_dir))

# 导入处理模块
try:
    from utils.dataprocess.vibration_data_loader import VibrationDataLoader
    from utils.dataprocess.wavelet_denoise import WaveletDenoiser
    from utils.dataprocess.start_idx_visualized_select import StartIdxVisualizedSelect
    from utils.dataprocess.debiasing import debias_csv_folder
    from utils.visualize.data_processor import DataProcessor
    from utils.visualize.visualization_generator import VisualizationGenerator
except ImportError as e:
    logger.warning(f"导入模块时出现警告: {e}")

# 统一配置类
class ProcessorConfig:
    """统一的处理器配置基类"""
    
    def __init__(self, **kwargs):
        # 通用配置
        self.verbose = kwargs.get('verbose', True)
        self.log_level = kwargs.get('log_level', 'INFO')
        
        # 更新配置
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    def validate(self) -> bool:
        """验证配置有效性"""
        return True

class ProcessorResult:
    """统一的处理器结果类"""
    
    def __init__(self, success: bool, message: str = "", 
                 data: Any = None, metadata: Dict[str, Any] = None):
        self.success = success
        self.message = message
        self.data = data
        self.metadata = metadata or {}
        self.timestamp = time.time()
    
    def __str__(self):
        status = "成功" if self.success else "失败"
        return f"ProcessorResult({status}: {self.message})"

class DataPreprocessorConfig(ProcessorConfig):
    """数据预处理配置"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 路径配置
        self.input_dir = kwargs.get('input_dir', './input/data')
        self.output_dir = kwargs.get('output_dir', './output/data_csv_denoised_start-idx-reselected_debiased')
        
        # 中间输出路径
        self.csv_output_dir = kwargs.get('csv_output_dir', './output/data_csv')
        self.denoised_output_dir = kwargs.get('denoised_output_dir', './output/data_csv_denoised')
        self.start_idx_output_dir = kwargs.get('start_idx_output_dir', './output/data_csv_denoised_start-idx-reselected')
        
        # 处理参数
        self.wavelet = kwargs.get('wavelet', 'db6')
        self.wavelet_level = kwargs.get('wavelet_level', 6)
        self.keep_nodes = kwargs.get('keep_nodes', ['aaaaaa'])
        self.vg_delay = kwargs.get('vg_delay', 0.0025)
        self.truncate_to_min = kwargs.get('truncate_to_min', True)
        
        # 处理控制
        self.enable_txt_to_csv = kwargs.get('enable_txt_to_csv', True)
        self.enable_denoising = kwargs.get('enable_denoising', True)
        self.enable_start_idx_selection = kwargs.get('enable_start_idx_selection', True)
        self.enable_debiasing = kwargs.get('enable_debiasing', True)

class BaselineCorrectionConfig(ProcessorConfig):
    """基线矫正配置"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.input_dir = kwargs.get('input_dir', '')
        self.output_dir = kwargs.get('output_dir', '')
        self.mode = kwargs.get('mode', 'auto')  # 'auto', 'manual', 'skip'
        self.x_col = kwargs.get('x_col', 0)
        self.y_col = kwargs.get('y_col', 1)

class DataConverterConfig(ProcessorConfig):
    """数据转换配置"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.input_dir = kwargs.get('input_dir', '')
        self.output_file = kwargs.get('output_file', '')
        self.rows = kwargs.get('rows', 4)
        self.cols = kwargs.get('cols', 6)
        self.use_all_points = kwargs.get('use_all_points', True)

class MatConverterConfig(ProcessorConfig):
    """MAT转换配置"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.input_file = kwargs.get('input_file', '')
        self.output_file = kwargs.get('output_file', '')
        self.include_metadata = kwargs.get('include_metadata', True)

class DataPreprocessor:
    """统一的数据预处理器"""
    
    @staticmethod
    def process(config: DataPreprocessorConfig) -> ProcessorResult:
        """执行数据预处理流水线"""
        try:
            logger.info("开始数据预处理流水线")
            
            # 创建必要的目录
            for dir_path in [config.csv_output_dir, config.denoised_output_dir, 
                           config.start_idx_output_dir, config.output_dir]:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
            
            metadata = {}
            
            # Step 1: TXT to CSV
            if config.enable_txt_to_csv:
                logger.info("步骤1: TXT文件转换为CSV格式")
                VibrationDataLoader.convert_txt_to_csv_batch(
                    config.input_dir,
                    config.csv_output_dir
                )
                
                # 检查输出
                csv_files = list(Path(config.csv_output_dir).glob("*.csv"))
                metadata['csv_files_count'] = len(csv_files)
                logger.info(f"转换完成，生成 {len(csv_files)} 个CSV文件")
            
            # Step 2: 小波去噪
            if config.enable_denoising:
                logger.info("步骤2: 小波去噪处理")
                denoiser = WaveletDenoiser(
                    wavelet=config.wavelet,
                    level=config.wavelet_level,
                    keep_nodes=config.keep_nodes
                )
                denoiser.denoise_csv_batch(
                    input_folder=config.csv_output_dir,
                    output_folder=config.denoised_output_dir,
                    columns=["Time Signal"]
                )
                
                # 检查输出
                denoised_files = list(Path(config.denoised_output_dir).glob("*.csv"))
                metadata['denoised_files_count'] = len(denoised_files)
                logger.info(f"去噪完成，处理 {len(denoised_files)} 个文件")
            
            # Step 3: 起始点选择
            if config.enable_start_idx_selection:
                logger.info("步骤3: 数据起始点选择")
                processor_idx = StartIdxVisualizedSelect(
                    config.denoised_output_dir,
                    config.start_idx_output_dir,
                    vg_delay=config.vg_delay
                )
                processor_idx.run()
                
                # 检查输出
                start_idx_files = list(Path(config.start_idx_output_dir).glob("*.csv"))
                metadata['start_idx_files_count'] = len(start_idx_files)
                logger.info(f"起始点选择完成，处理 {len(start_idx_files)} 个文件")
            
            # Step 4: 去偏处理
            if config.enable_debiasing:
                logger.info("步骤4: 数据去偏处理")
                debias_csv_folder(
                    config.start_idx_output_dir,
                    config.output_dir,
                    truncate_to_min=config.truncate_to_min
                )
                
                # 检查输出
                final_files = list(Path(config.output_dir).glob("*.csv"))
                metadata['final_files_count'] = len(final_files)
                logger.info(f"去偏处理完成，生成 {len(final_files)} 个最终文件")
            
            return ProcessorResult(
                success=True,
                message=f"数据预处理完成，最终输出: {config.output_dir}",
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"数据预处理失败: {str(e)}")
            return ProcessorResult(
                success=False,
                message=f"数据预处理失败: {str(e)}"
            )

class BaselineCorrector:
    """统一的基线矫正器"""
    
    @staticmethod
    def process(config: BaselineCorrectionConfig) -> ProcessorResult:
        """执行基线矫正"""
        try:
            if config.mode == 'skip':
                return ProcessorResult(
                    success=True,
                    message="跳过基线矫正",
                    data={'output_dir': config.input_dir}
                )
            
            logger.info(f"开始基线矫正 (模式: {config.mode})")
            
            # 确保输出目录存在
            Path(config.output_dir).mkdir(parents=True, exist_ok=True)
            
            # 调用基线矫正脚本
            import subprocess
            cmd = [
                sys.executable,
                str(current_dir / "00_5_manual_baseline_correction.py"),
                '-i', str(config.input_dir),
                '-o', str(config.output_dir)
            ]
            
            if config.mode == 'auto':
                cmd.append('-a')
            elif config.mode == 'manual':
                cmd.append('-m')
            
            if config.verbose:
                cmd.append('-v')
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # 检查输出
                output_files = list(Path(config.output_dir).glob("*.csv"))
                
                return ProcessorResult(
                    success=True,
                    message=f"基线矫正完成，生成 {len(output_files)} 个文件",
                    data={'output_dir': config.output_dir},
                    metadata={'files_count': len(output_files)}
                )
            else:
                return ProcessorResult(
                    success=False,
                    message=f"基线矫正失败: {result.stderr}"
                )
                
        except Exception as e:
            logger.error(f"基线矫正失败: {str(e)}")
            return ProcessorResult(
                success=False,
                message=f"基线矫正失败: {str(e)}"
            )

class DataConverter:
    """统一的数据转换器 (CSV to NPZ)"""
    
    @staticmethod
    def process(config: DataConverterConfig) -> ProcessorResult:
        """执行CSV到NPZ转换"""
        try:
            logger.info("开始CSV到NPZ转换")
            
            # 确保输出目录存在
            Path(config.output_file).parent.mkdir(parents=True, exist_ok=True)
            
            # 使用DataProcessor处理数据
            processor = DataProcessor(
                input_folder=config.input_dir,
                rows=config.rows,
                cols=config.cols,
                use_all_points=config.use_all_points
            )
            
            # 保存处理后的数据
            processor.save_processed_data(config.output_file)
            
            # 验证输出文件
            if Path(config.output_file).exists():
                # 读取数据获取元信息
                data = np.load(config.output_file, allow_pickle=True)
                metadata = {
                    'output_file': config.output_file,
                    'grid_shape': data['grid_data'].shape if 'grid_data' in data else None,
                    'time_points_count': len(data['time_points']) if 'time_points' in data else 0,
                    'file_size': Path(config.output_file).stat().st_size
                }
                
                return ProcessorResult(
                    success=True,
                    message=f"CSV到NPZ转换完成: {config.output_file}",
                    data={'output_file': config.output_file},
                    metadata=metadata
                )
            else:
                return ProcessorResult(
                    success=False,
                    message="NPZ文件未生成"
                )
                
        except Exception as e:
            logger.error(f"CSV到NPZ转换失败: {str(e)}")
            return ProcessorResult(
                success=False,
                message=f"CSV到NPZ转换失败: {str(e)}"
            )

class MatConverter:
    """统一的MAT转换器 (NPZ to MAT)"""
    
    @staticmethod
    def process(config: MatConverterConfig) -> ProcessorResult:
        """执行NPZ到MAT转换"""
        try:
            logger.info("开始NPZ到MAT转换")
            
            # 确保输出目录存在
            Path(config.output_file).parent.mkdir(parents=True, exist_ok=True)
            
            # 加载NPZ数据
            data = np.load(config.input_file, allow_pickle=True)
            
            # 检查必要的键
            if 'grid_data' not in data or 'time_points' not in data:
                return ProcessorResult(
                    success=False,
                    message="NPZ文件中缺少必要的数据：grid_data 或 time_points"
                )
            
            # 准备MAT数据
            mat_data = {
                'grid_data': data['grid_data'],
                'time_points': data['time_points'],
            }
            
            # 添加元数据
            if config.include_metadata:
                metadata_keys = ['min_signal', 'max_signal', 'min_time', 'max_time', 'rows', 'cols']
                for key in metadata_keys:
                    if key in data:
                        value = data[key]
                        # 确保标量值正确转换
                        mat_data[key] = float(value) if hasattr(value, 'size') and value.size == 1 else value
            
            # 保存MAT文件
            sio.savemat(config.output_file, mat_data)
            
            # 验证输出
            if Path(config.output_file).exists():
                # 获取文件信息
                mat_info = sio.whosmat(config.output_file)
                metadata = {
                    'output_file': config.output_file,
                    'variables': [(name, shape, dtype) for name, shape, dtype in mat_info],
                    'file_size': Path(config.output_file).stat().st_size
                }
                
                return ProcessorResult(
                    success=True,
                    message=f"NPZ到MAT转换完成: {config.output_file}",
                    data={'output_file': config.output_file},
                    metadata=metadata
                )
            else:
                return ProcessorResult(
                    success=False,
                    message="MAT文件未生成"
                )
                
        except Exception as e:
            logger.error(f"NPZ到MAT转换失败: {str(e)}")
            return ProcessorResult(
                success=False,
                message=f"NPZ到MAT转换失败: {str(e)}"
            )

# 统一的流水线管理器
class PipelineManager:
    """统一的数据处理流水线管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = {}
    
    def run_full_pipeline(self) -> Dict[str, ProcessorResult]:
        """运行完整流水线"""
        
        # Step 1: 数据预处理
        if self.config.get('enable_preprocessing', True):
            preprocess_config = DataPreprocessorConfig(**self.config.get('preprocessing', {}))
            self.results['preprocessing'] = DataPreprocessor.process(preprocess_config)
            
            if not self.results['preprocessing'].success:
                logger.error("数据预处理失败，终止流水线")
                return self.results
        
        # Step 2: 基线矫正
        if self.config.get('enable_baseline_correction', False):
            baseline_config = BaselineCorrectionConfig(**self.config.get('baseline_correction', {}))
            self.results['baseline_correction'] = BaselineCorrector.process(baseline_config)
            
            # 更新后续步骤的输入路径
            if self.results['baseline_correction'].success:
                csv_input_dir = self.results['baseline_correction'].data['output_dir']
            else:
                csv_input_dir = preprocess_config.output_dir
        else:
            csv_input_dir = self.config['preprocessing']['output_dir']
        
        # Step 3: CSV到NPZ转换
        if self.config.get('enable_csv_to_npz', True):
            converter_config = DataConverterConfig(**self.config.get('csv_to_npz', {}))
            converter_config.input_dir = csv_input_dir
            self.results['csv_to_npz'] = DataConverter.process(converter_config)
            
            if not self.results['csv_to_npz'].success:
                logger.error("CSV到NPZ转换失败，终止流水线")
                return self.results
        
        # Step 4: NPZ到MAT转换
        if self.config.get('enable_npz_to_mat', True):
            mat_config = MatConverterConfig(**self.config.get('npz_to_mat', {}))
            if 'csv_to_npz' in self.results and self.results['csv_to_npz'].success:
                mat_config.input_file = self.results['csv_to_npz'].data['output_file']
            self.results['npz_to_mat'] = MatConverter.process(mat_config)
        
        return self.results

# 命令行接口支持
def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="统一数据处理流水线")
    parser.add_argument("--config", type=str, help="配置文件路径")
    parser.add_argument("--step", type=str, choices=['preprocess', 'baseline', 'csv2npz', 'npz2mat', 'full'],
                       default='full', help="执行的步骤")
    
    args = parser.parse_args()
    
    # 这里可以添加配置文件加载和命令行参数处理逻辑
    print("命令行接口 - 待实现")

if __name__ == "__main__":
    main()