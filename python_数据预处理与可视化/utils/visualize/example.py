#!/usr/bin/env python3
"""
示例脚本，演示如何使用数据处理和可视化模块
"""
import os
from data_processor import DataProcessor
from visualization_generator import VisualizationGenerator
from loguru import logger
import sys

logger.configure(
    handlers=[
        {"sink": sys.stdout, "level": "INFO"},
        {"sink": "example.log", "level": "DEBUG", "rotation": "10 MB"},
    ]
)

# 配置参数
INPUT_FOLDER = "./output/data2_csv_start-idx-reselected_debiased"
OUTPUT_FOLDER = "./output/videos"
ROWS = 6
COLS = 6
SAMPLING_POINTS = 500

# 确保输出文件夹存在
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def process_and_visualize():
    """处理数据并生成可视化"""
    print(f"\n=== 1. 处理数据 ===")
    # 创建数据处理器
    processor = DataProcessor(
        input_folder=INPUT_FOLDER,
        rows=ROWS,
        cols=COLS,
        sampling_points=SAMPLING_POINTS
    )
    
    # 保存处理后的数据
    processed_data_file = os.path.join(OUTPUT_FOLDER, "processed_data.npz")
    processor.save_processed_data(processed_data_file)
    print(f"处理后的数据已保存到: {processed_data_file}")
    
    # 获取处理后的数据
    processed_data = processor.get_processed_data()
    
    print(f"\n=== 2. 使用默认配色方案生成视频 ===")
    # 创建可视化生成器 - 使用默认viridis配色
    viz_gen = VisualizationGenerator(
        processed_data=processed_data,
        colormap="viridis",
        output_folder=OUTPUT_FOLDER
    )
    
    # 生成热图视频
    viz_gen.generate_heatmap_video(
        output_file="heatmap_animation_default.mp4",
        title="信号强度随时间变化 (默认配色)"
    )
    
    print(f"\n=== 3. 使用不同配色方案生成视频 ===")
    # 创建可视化生成器 - 使用jet配色
    jet_viz_gen = VisualizationGenerator(
        processed_data=processed_data,
        colormap="jet",
        output_folder=OUTPUT_FOLDER
    )
    
    # 生成热图视频
    jet_viz_gen.generate_heatmap_video(
        output_file="heatmap_animation_jet.mp4",
        title="信号强度随时间变化 (Jet配色)"
    )
    
    # 创建可视化生成器 - 使用自定义渐变色
    custom_viz_gen = VisualizationGenerator(
        processed_data=processed_data,
        custom_gradient=["#3366FF", "#FF3366"],  # 蓝色到粉红色渐变
        output_folder=OUTPUT_FOLDER
    )
    
    # 生成热图视频
    custom_viz_gen.generate_heatmap_video(
        output_file="heatmap_animation_custom.mp4",
        title="信号强度随时间变化 (自定义渐变)"
    )
    
    print(f"\n=== 4. 生成3D表面视频 ===")
    # 使用热力图配色
    heat_viz_gen = VisualizationGenerator(
        processed_data=processed_data,
        colormap="hot",
        output_folder=OUTPUT_FOLDER
    )
    
    # 生成3D表面视频
    heat_viz_gen.generate_3d_surface_video(
        output_file="3d_surface_animation_hot.mp4",
        title="3D信号表面 (热力图配色)",
        rotate_view=True,
        initial_elev=30,
        initial_azim=45,
        rotation_speed=1.0,
        full_rotation=True
    )
    
    print(f"\n=== 5. 生成带剖面的热图视频 ===")
    # 使用科学数据常用的coolwarm配色
    coolwarm_viz_gen = VisualizationGenerator(
        processed_data=processed_data,
        colormap="coolwarm",
        output_folder=OUTPUT_FOLDER
    )
    
    # 生成带剖面的热图视频
    coolwarm_viz_gen.generate_heatmap_with_profiles_video(
        output_file="heatmap_with_profiles_coolwarm.mp4",
        title="带剖面的热图 (冷暖对比配色)"
    )
    
    print(f"\n=== 6. 生成特定时间点的静态图像 ===")
    # 选择一个中间时间点
    middle_time = (processed_data['min_time'] + processed_data['max_time']) / 2
    
    # 生成三种类型的特定时间点图像
    print(f"生成时间点 {middle_time:.4f} 的静态图像...")
    
    # 1. 热图
    heatmap_file = viz_gen.generate_heatmap_at_time(
        target_time=middle_time,
        output_file="static_heatmap.png",
        title="特定时间点的信号强度热图"
    )
    
    # 2. 3D表面图 - 不同角度
    surface_file1 = viz_gen.generate_3d_surface_at_time(
        target_time=middle_time,
        output_file="static_3d_surface_angle1.png",
        title="特定时间点的3D信号表面",
        elev=30,
        azim=45
    )
    
    surface_file2 = viz_gen.generate_3d_surface_at_time(
        target_time=middle_time,
        output_file="static_3d_surface_angle2.png",
        title="特定时间点的3D信号表面",
        elev=20,
        azim=120
    )
    
    # 3. 带剖面的热图
    profiles_file = viz_gen.generate_heatmap_with_profiles_at_time(
        target_time=middle_time,
        output_file="static_heatmap_with_profiles.png",
        title="特定时间点的带剖面热图"
    )
    
    print(f"\n已生成以下静态图像:")
    print(f"  热图: {heatmap_file}")
    print(f"  3D表面图(角度1): {surface_file1}")
    print(f"  3D表面图(角度2): {surface_file2}")
    print(f"  带剖面热图: {profiles_file}")
    
    print(f"\n=== 7. 生成时间序列的关键时刻图像 ===")
    # 创建一个使用spectral配色的生成器实例用于时间序列比较
    spectral_viz_gen = VisualizationGenerator(
        processed_data=processed_data,
        colormap="spectral",
        output_folder=OUTPUT_FOLDER
    )
    
    # 生成时间序列的起始、中间和结束时刻的热图
    start_time = processed_data['min_time']
    end_time = processed_data['max_time']
    
    spectral_viz_gen.generate_heatmap_at_time(
        target_time=start_time,
        output_file="time_series_start.png",
        title="信号强度热图 (开始时刻)"
    )
    
    spectral_viz_gen.generate_heatmap_at_time(
        target_time=middle_time,
        output_file="time_series_middle.png",
        title="信号强度热图 (中间时刻)"
    )
    
    spectral_viz_gen.generate_heatmap_at_time(
        target_time=end_time,
        output_file="time_series_end.png",
        title="信号强度热图 (结束时刻)"
    )
    
    print(f"已生成时间序列的三个关键时刻热图 (开始、中间、结束)")
    
    print(f"\n所有输出文件已保存到: {OUTPUT_FOLDER}\n")


def load_and_visualize():
    """从保存的处理数据加载并生成可视化"""
    print(f"\n=== 从预处理数据生成可视化 ===")
    
    # 加载预处理数据
    import numpy as np
    processed_data_file = os.path.join(OUTPUT_FOLDER, "processed_data.npz")
    
    try:
        data = np.load(processed_data_file)
        
        # 创建处理数据字典
        processed_data = {
            'grid_data': data['grid_data'],
            'time_points': data['time_points'],
            'min_signal': float(data['min_signal']),
            'max_signal': float(data['max_signal']),
            'min_time': float(data['min_time']),
            'max_time': float(data['max_time']),
            'rows': int(data['rows']),
            'cols': int(data['cols']),
            'data': {}  # 这里简化处理，实际可能需要重建原始数据结构
        }
        
        print(f"已加载预处理数据，形状: {processed_data['grid_data'].shape}")
        
        # 创建可视化生成器
        viz_gen = VisualizationGenerator(
            processed_data=processed_data,
            colormap="viridis",
            output_folder=os.path.join(OUTPUT_FOLDER, "from_processed")
        )
        
        # 生成视频
        viz_gen.generate_heatmap_video(
            output_file="heatmap_from_processed.mp4",
            title="从预处理数据生成的热图"
        )
        
        print(f"已从预处理数据生成视频")
        
    except Exception as e:
        print(f"加载预处理数据时出错: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("=== 时间序列数据可视化示例 ===")
    
    # 如果需要从头开始处理数据和生成可视化
    if not os.path.exists(os.path.join(OUTPUT_FOLDER, "processed_data.npz")):
        print("\n未找到预处理数据文件，将从原始CSV文件处理数据")
        process_and_visualize()
    else:
        # 询问用户是否重新处理数据
        choice = input("\n找到预处理数据文件，是否重新处理数据？(y/n): ")
        if choice.lower() == 'y':
            process_and_visualize()
        else:
            # 从已处理的数据生成可视化
            load_and_visualize()
    
    print("\n程序结束")