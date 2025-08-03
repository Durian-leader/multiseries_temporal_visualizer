"""
多时序数据处理和可视化工具包

该包提供了完整的数据处理流水线，包括：
- 数据预处理 (TXT转CSV、去噪、起始点选择、去偏)
- 基线矫正
- 数据格式转换 (CSV到NPZ、NPZ到MAT)
"""

# 导入主要功能函数
try:
    # 修复导入路径，使用实际存在的文件名
    from ._00select_start_idx import run_preprocessing_pipeline
    from ._01csv2npz import convert_csv_to_npz  
    from ._npz_to_mat import convert_npz_to_mat
    
    __all__ = [
        'run_preprocessing_pipeline',
        'convert_csv_to_npz',
        'convert_npz_to_mat'
    ]
    
except ImportError as e:
    # 尝试直接从原文件导入
    try:
        import sys
        import os
        from pathlib import Path
        
        # 添加当前目录到路径
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        
        # 直接导入原始文件中的函数
        import importlib.util
        
        # 导入预处理函数
        spec1 = importlib.util.spec_from_file_location("select_start_idx", current_dir / "00select_start_idx.py")
        module1 = importlib.util.module_from_spec(spec1)
        spec1.loader.exec_module(module1)
        run_preprocessing_pipeline = module1.run_preprocessing_pipeline
        
        # 导入CSV转NPZ函数
        spec2 = importlib.util.spec_from_file_location("csv2npz", current_dir / "01csv2npz.py")
        module2 = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(module2)
        convert_csv_to_npz = module2.convert_csv_to_npz
        
        # 导入NPZ转MAT函数
        spec3 = importlib.util.spec_from_file_location("npz_to_mat", current_dir / "npz_to_mat.py")
        module3 = importlib.util.module_from_spec(spec3)
        spec3.loader.exec_module(module3)
        convert_npz_to_mat = module3.convert_npz_to_mat
        
        __all__ = [
            'run_preprocessing_pipeline',
            'convert_csv_to_npz',
            'convert_npz_to_mat'
        ]
        
    except Exception as e2:
        # 如果仍然失败，提供错误信息
        import warnings
        warnings.warn(f"所有导入方式都失败: 原始错误={e}, 备用错误={e2}", ImportWarning)
        
        __all__ = []

__version__ = "1.0.0"
__author__ = "Data Processing Pipeline"
__description__ = "多时序数据处理和可视化工具包"