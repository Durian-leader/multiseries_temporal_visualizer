import numpy as np
import scipy.io as sio
import os
from loguru import logger
import sys

# 配置日志
logger.remove()
logger.configure(
    handlers=[
        {"sink": sys.stdout, "level": "INFO"},
        {"sink": "npz_to_mat_converter.log", "level": "DEBUG", "rotation": "10 MB"},
    ]
)

# 文件路径配置 - 修改这些变量来适应你的需求
input_npz_file = "output\my_processed_data_use_all_points.npz"  # 输入的NPZ文件
output_mat_file = "my_processed_data.mat"  # 输出的MAT文件

# 是否包含元数据
include_metadata = True

try:
    # 加载NPZ文件
    logger.info(f"正在加载NPZ文件: {input_npz_file}")
    data = np.load(input_npz_file, allow_pickle=True)
    
    # 检查必要的键是否存在
    if 'grid_data' not in data or 'time_points' not in data:
        logger.error("NPZ文件中缺少必要的数据：grid_data 或 time_points")
        sys.exit(1)
    
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
                # 确保数据是MATLAB兼容的格式
                value = data[key]
                if isinstance(value, np.ndarray) and value.size == 1:
                    value = float(value)  # 转换单元素数组为标量
                mat_data[key] = value
        
        # 处理文件名网格（如果存在）
        if 'filename_grid' in data:
            # 将文件名网格转换为字符串列表列表
            filenames = data['filename_grid']
            # 确保传递给MATLAB的是字符串数组
            if isinstance(filenames, np.ndarray) and filenames.dtype == 'O':
                # 将None值替换为空字符串，以防止MATLAB出错
                filename_list = [[str(name) if name is not None else '' for name in row] 
                               for row in filenames]
                mat_data['filename_grid'] = filename_list
    
    # 保存为MAT文件
    logger.info(f"正在保存MAT文件: {output_mat_file}")
    sio.savemat(output_mat_file, mat_data)
    
    logger.info(f"转换完成: {input_npz_file} -> {output_mat_file}")
    logger.info(f"MAT文件包含以下变量: {list(mat_data.keys())}")
    
except Exception as e:
    logger.error(f"转换过程中出错: {e}")
    sys.exit(1)

logger.info("脚本执行完毕")