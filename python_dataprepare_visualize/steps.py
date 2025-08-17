#!/usr/bin/env python3
"""
数据处理功能统一接口模块

提供完整数据处理流水线的统一函数接口，包含从TXT文件到MAT文件的所有处理功能。
每个函数都提供一致的参数接口和错误处理机制。
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Union

# 设置路径以确保正确导入
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))
sys.path.append(str(current_dir.parent))

# 导入所需模块
from utils.dataprocess.vibration_data_loader import VibrationDataLoader
from utils.dataprocess.wavelet_denoise import WaveletDenoiser
from utils.dataprocess.start_idx_visualized_select import StartIdxVisualizedSelect
from utils.dataprocess.debiasing import debias_csv_folder
from csv2npz import convert_csv_to_npz
from npz_to_mat import convert_npz_to_mat

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)


def convert_txt_to_csv(
    input_dir: str,
    output_dir: str,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    TXT文件转换为CSV格式
    
    参数:
        input_dir: 输入TXT文件目录
        output_dir: 输出CSV文件目录  
        verbose: 是否显示详细信息
        
    返回:
        包含处理结果的字典
    """
    try:
        # 确保输出目录存在
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 执行TXT到CSV的批量转换
        result = VibrationDataLoader.convert_txt_to_csv_batch(input_dir, output_dir)
        
        if verbose:
            logger.info(f"TXT to CSV conversion completed: {input_dir} -> {output_dir}")
        
        return {
            "success": True,
            "input_dir": input_dir,
            "output_dir": output_dir,
            "files_processed": len(result) if isinstance(result, list) else 0,
            "message": "TXT to CSV conversion completed successfully"
        }
        
    except Exception as e:
        logger.error(f"TXT to CSV conversion failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "TXT to CSV conversion failed"
        }


def apply_wavelet_denoise(
    input_dir: str,
    output_dir: str,
    columns: Union[List[str], None] = None,
    wavelet: str = "db6",
    wavelet_level: int = 6,
    keep_nodes: Union[List[str], None] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    小波去噪处理
    
    参数:
        input_dir: 输入CSV文件目录
        output_dir: 输出去噪CSV文件目录
        columns: 需要去噪的列名列表，默认为["Time", "Signal"]
        wavelet: 小波类型，默认为"db6"
        wavelet_level: 小波分解层数，默认为6
        keep_nodes: 保留的小波节点，默认为["aaaaaa"]
        verbose: 是否显示详细信息
        
    返回:
        包含处理结果的字典
    """
    try:
        # 设置默认参数
        if columns is None:
            columns = ["Time", "Signal"]
        if keep_nodes is None:
            keep_nodes = ["aaaaaa"]
        
        # 确保输出目录存在
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 创建小波去噪器并执行批量处理
        denoiser = WaveletDenoiser(
            wavelet=wavelet, 
            level=wavelet_level, 
            keep_nodes=keep_nodes
        )
        
        result = denoiser.denoise_csv_batch(
            input_folder=input_dir,
            output_folder=output_dir,
            columns=columns
        )
        
        if verbose:
            logger.info(f"Wavelet denoising completed: {input_dir} -> {output_dir}")
            logger.info(f"Wavelet: {wavelet}, Level: {wavelet_level}, Nodes: {keep_nodes}")
        
        return {
            "success": True,
            "input_dir": input_dir,
            "output_dir": output_dir,
            "wavelet": wavelet,
            "level": wavelet_level,
            "keep_nodes": keep_nodes,
            "files_processed": len(result) if isinstance(result, list) else 0,
            "message": "Wavelet denoising completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Wavelet denoising failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Wavelet denoising failed"
        }


def select_start_indices(
    input_dir: str,
    output_dir: str,
    vg_delay: float = 0.0025,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    起始点选择（交互式GUI）
    
    参数:
        input_dir: 输入CSV文件目录
        output_dir: 输出起始点选择后的CSV文件目录
        vg_delay: Vg信号延迟时间（秒），默认为0.0025（2.5ms）
        verbose: 是否显示详细信息
        
    返回:
        包含处理结果的字典
    """
    try:
        # 确保输出目录存在
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 创建起始点选择处理器并运行
        processor_idx = StartIdxVisualizedSelect(
            input_dir,
            output_dir,
            vg_delay=vg_delay
        )
        
        result = processor_idx.run()
        
        if verbose:
            logger.info(f"Start index selection completed: {input_dir} -> {output_dir}")
            logger.info(f"Vg delay: {vg_delay}s")
        
        return {
            "success": True,
            "input_dir": input_dir,
            "output_dir": output_dir,
            "vg_delay": vg_delay,
            "files_processed": 0 if result is None else getattr(result, 'files_processed', 0),
            "message": "Start index selection completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Start index selection failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Start index selection failed"
        }


def apply_debiasing(
    input_dir: str,
    output_dir: str,
    truncate_to_min: bool = True,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    去偏处理
    
    处理输入文件夹中的所有CSV文件，将每列数据偏移到以第一个值为0
    
    参数:
        input_dir: 输入CSV文件目录
        output_dir: 输出去偏处理后的CSV文件目录
        truncate_to_min: 是否截断到最小长度，默认为True
        verbose: 是否显示详细信息
        
    返回:
        包含处理结果的字典
    """
    try:
        # 确保输出目录存在
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 执行去偏处理
        result = debias_csv_folder(
            input_dir,
            output_dir,
            truncate_to_min=truncate_to_min
        )
        
        if verbose:
            logger.info(f"Debiasing completed: {input_dir} -> {output_dir}")
            logger.info(f"Truncate to min: {truncate_to_min}")
        
        return {
            "success": True,
            "input_dir": input_dir,
            "output_dir": output_dir,
            "truncate_to_min": truncate_to_min,
            "files_processed": 0 if result is None else getattr(result, 'files_processed', 0),
            "message": "Debiasing completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Debiasing failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Debiasing failed"
        }


def apply_baseline_correction(
    input_dir: str,
    output_dir: str,
    mode: str = "auto",
    xcol: Union[str, None] = None,
    ycol: Union[str, None] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    基线矫正处理
    
    支持自动模式（首末点连接）和手动模式（GUI交互选择）
    
    参数:
        input_dir: 输入CSV文件目录
        output_dir: 输出基线矫正后的CSV文件目录
        mode: 处理模式，"auto"为自动模式，"manual"为手动模式
        xcol: X轴列名或索引，默认为第一列
        ycol: Y轴列名或索引，默认为第二列
        verbose: 是否显示详细信息
        
    返回:
        包含处理结果的字典
    """
    try:
        # 确保输出目录存在
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 构建命令行参数
        script_path = current_dir / "00_5_manual_baseline_correction.py"
        cmd = [
            sys.executable, str(script_path),
            "-i", input_dir,
            "-o", output_dir
        ]
        
        # 添加模式参数
        if mode == "auto":
            cmd.append("-a")
        elif mode == "manual":
            cmd.append("-m")
        else:
            raise ValueError(f"Invalid mode: {mode}. Must be 'auto' or 'manual'")
        
        # 添加详细输出参数
        if verbose:
            cmd.append("-v")
        
        # 添加列参数
        if xcol:
            cmd.extend(["-x", str(xcol)])
        if ycol:
            cmd.extend(["-y", str(ycol)])
        
        # 执行基线矫正脚本
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if verbose:
            logger.info(f"Baseline correction completed: {input_dir} -> {output_dir}")
            logger.info(f"Mode: {mode}")
            if result.stdout:
                logger.info(f"Output: {result.stdout}")
        
        return {
            "success": True,
            "input_dir": input_dir,
            "output_dir": output_dir,
            "mode": mode,
            "xcol": xcol,
            "ycol": ycol,
            "stdout": result.stdout,
            "message": "Baseline correction completed successfully"
        }
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Baseline correction script failed: {e.stderr}")
        return {
            "success": False,
            "error": e.stderr,
            "stdout": e.stdout,
            "message": "Baseline correction failed"
        }
    except Exception as e:
        logger.error(f"Baseline correction failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Baseline correction failed"
        }


def convert_csv_to_npz_file(
    input_folder: str,
    output_file: str,
    rows: int = 4,
    cols: int = 6,
    use_all_points: bool = True,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    CSV转换为NPZ格式
    
    参数:
        input_folder: 输入CSV文件夹路径
        output_file: 输出NPZ文件路径
        rows: 网格行数，默认为4
        cols: 网格列数，默认为6
        use_all_points: 是否使用所有数据点，默认为True
        verbose: 是否显示详细信息
        
    返回:
        包含处理结果的字典
    """
    try:
        # 确保输出目录存在
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # 执行CSV到NPZ的转换
        result = convert_csv_to_npz(
            input_folder=input_folder,
            output_file=output_file,
            rows=rows,
            cols=cols,
            use_all_points=use_all_points,
            verbose=verbose
        )
        
        if verbose:
            logger.info(f"CSV to NPZ conversion completed: {input_folder} -> {output_file}")
            logger.info(f"Grid size: {rows}×{cols}, Use all points: {use_all_points}")
        
        return {
            "success": True,
            "input_folder": input_folder,
            "output_file": output_file,
            "rows": rows,
            "cols": cols,
            "use_all_points": use_all_points,
            "result": result,
            "message": "CSV to NPZ conversion completed successfully"
        }
        
    except Exception as e:
        logger.error(f"CSV to NPZ conversion failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "CSV to NPZ conversion failed"
        }


def convert_npz_to_mat_file(
    input_file: str,
    output_file: str,
    include_metadata: bool = True,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    NPZ转换为MAT格式
    
    参数:
        input_file: 输入NPZ文件路径
        output_file: 输出MAT文件路径
        include_metadata: 是否包含元数据，默认为True
        verbose: 是否显示详细信息
        
    返回:
        包含处理结果的字典
    """
    try:
        # 确保输出目录存在
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # 执行NPZ到MAT的转换
        result = convert_npz_to_mat(
            input_file=input_file,
            output_file=output_file,
            include_metadata=include_metadata,
            verbose=verbose
        )
        
        if verbose:
            logger.info(f"NPZ to MAT conversion completed: {input_file} -> {output_file}")
            logger.info(f"Include metadata: {include_metadata}")
        
        return {
            "success": True,
            "input_file": input_file,
            "output_file": output_file,
            "include_metadata": include_metadata,
            "result": result,
            "message": "NPZ to MAT conversion completed successfully"
        }
        
    except Exception as e:
        logger.error(f"NPZ to MAT conversion failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "NPZ to MAT conversion failed"
        }


def run_full_pipeline(
    input_txt_dir: str,
    output_base_dir: str = "./output",
    rows: int = 4,
    cols: int = 6,
    vg_delay: float = 0.0025,
    wavelet: str = "db6",
    wavelet_level: int = 6,
    baseline_mode: str = "auto",
    use_all_points: bool = True,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    运行完整的数据处理流水线
    
    参数:
        input_txt_dir: 输入TXT文件目录
        output_base_dir: 输出基础目录
        rows: 网格行数
        cols: 网格列数  
        vg_delay: Vg信号延迟时间
        wavelet: 小波类型
        wavelet_level: 小波分解层数
        baseline_mode: 基线矫正模式（"auto"或"manual"）
        use_all_points: 是否使用所有数据点
        verbose: 是否显示详细信息
        
    返回:
        包含所有步骤处理结果的字典
    """
    results = {}
    
    try:
        # 创建输出目录结构
        base_path = Path(output_base_dir)
        csv_dir = base_path / "01_csv"
        denoised_dir = base_path / "02_denoised"
        start_idx_dir = base_path / "03_start_idx"
        debiased_dir = base_path / "04_debiased" 
        baseline_dir = base_path / "05_baseline_corrected"
        npz_file = base_path / "my_processed_data.npz"
        mat_file = base_path / "my_processed_data.mat"
        
        if verbose:
            logger.info("Starting full data processing pipeline...")
            logger.info(f"Input directory: {input_txt_dir}")
            logger.info(f"Output base directory: {output_base_dir}")
        
        # TXT转CSV
        results["txt_to_csv"] = convert_txt_to_csv(input_txt_dir, str(csv_dir), verbose)
        if not results["txt_to_csv"]["success"]:
            return results
        
        # 小波去噪
        results["wavelet_denoise"] = apply_wavelet_denoise(
            str(csv_dir), str(denoised_dir), 
            wavelet=wavelet, wavelet_level=wavelet_level, verbose=verbose
        )
        if not results["wavelet_denoise"]["success"]:
            return results
        
        # 起始点选择
        results["start_idx_selection"] = select_start_indices(
            str(denoised_dir), str(start_idx_dir), 
            vg_delay=vg_delay, verbose=verbose
        )
        if not results["start_idx_selection"]["success"]:
            return results
        
        # 去偏处理
        results["debiasing"] = apply_debiasing(
            str(start_idx_dir), str(debiased_dir), verbose=verbose
        )
        if not results["debiasing"]["success"]:
            return results
        
        # 基线矫正
        results["baseline_correction"] = apply_baseline_correction(
            str(debiased_dir), str(baseline_dir), 
            mode=baseline_mode, verbose=verbose
        )
        if not results["baseline_correction"]["success"]:
            return results
        
        # CSV转NPZ
        results["csv_to_npz"] = convert_csv_to_npz_file(
            str(baseline_dir), str(npz_file),
            rows=rows, cols=cols, use_all_points=use_all_points, verbose=verbose
        )
        if not results["csv_to_npz"]["success"]:
            return results
        
        # NPZ转MAT
        results["npz_to_mat"] = convert_npz_to_mat_file(
            str(npz_file), str(mat_file), verbose=verbose
        )
        
        # 总结
        results["pipeline"] = {
            "success": all(step["success"] for step in results.values()),
            "input_dir": input_txt_dir,
            "output_dir": output_base_dir,
            "final_npz": str(npz_file),
            "final_mat": str(mat_file),
            "parameters": {
                "rows": rows,
                "cols": cols,
                "vg_delay": vg_delay,
                "wavelet": wavelet,
                "wavelet_level": wavelet_level,
                "baseline_mode": baseline_mode,
                "use_all_points": use_all_points
            },
            "message": "Full pipeline completed successfully" if all(step["success"] for step in results.values()) else "Pipeline failed"
        }
        
        if verbose and results["pipeline"]["success"]:
            logger.info("Full data processing pipeline completed successfully!")
            logger.info(f"Final NPZ file: {npz_file}")
            logger.info(f"Final MAT file: {mat_file}")
        
        return results
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        results["pipeline"] = {
            "success": False,
            "error": str(e),
            "message": "Pipeline execution failed"
        }
        return results


if __name__ == "__main__":
    # 示例用法
    input_dir = "./input/data"  
    output_dir = "./output"
    
    # 运行完整流水线
    results = run_full_pipeline(
        input_txt_dir=input_dir,
        output_base_dir=output_dir,
        rows=4,
        cols=6,
        vg_delay=0.0025,
        wavelet="db6",
        wavelet_level=6,
        baseline_mode="auto",
        use_all_points=True,
        verbose=True
    )
    
    # 打印结果摘要
    print("\n=== Pipeline Results Summary ===")
    for step_name, result in results.items():
        status = "✓" if result.get("success", False) else "✗"
        message = result.get("message", "Unknown status")
        print(f"{status} {step_name}: {message}")