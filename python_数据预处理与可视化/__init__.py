"""
多时序数据处理和可视化工具包

该包提供了完整的数据处理流水线，包括：
- 数据预处理 (TXT转CSV、去噪、起始点选择、去偏)
- 基线矫正
- 数据格式转换 (CSV到NPZ、NPZ到MAT)
"""

# 导入主要功能函数
try:
    from ._00select_start_idx import run_preprocessing_pipeline
    from ._01csv2npz import convert_csv_to_npz  
    from ._npz_to_mat import convert_npz_to_mat
    
    __all__ = [
        'run_preprocessing_pipeline',
        'convert_csv_to_npz',
        'convert_npz_to_mat'
    ]
    
except ImportError as e:
    # 如果导入失败，提供备用导入方式
    import warnings
    warnings.warn(f"某些模块导入失败: {e}，请检查依赖包是否正确安装", ImportWarning)
    
    __all__ = []

__version__ = "1.0.0"
__author__ = "Data Processing Pipeline"
__description__ = "多时序数据处理和可视化工具包"