import os
import argparse
from loguru import logger
from pathlib import Path
from data_processor import DataProcessor
from visualization_generator import VisualizationGenerator
import sys

def main():
    logger.configure(
        handlers=[
            {"sink": sys.stdout, "level": "INFO"},
            {"sink": "main.log", "level": "DEBUG", "rotation": "10 MB"},
            ]
        )
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='生成高质量时间序列数据可视化视频')
    
    # 数据相关参数
    parser.add_argument('--input', '-i', required=True, help='输入文件夹路径（包含CSV文件）')
    parser.add_argument('--output', '-o', default='./output/videos', help='输出文件夹路径')
    parser.add_argument('--rows', '-r', type=int, required=True, help='数据网格的行数')
    parser.add_argument('--cols', '-c', type=int, required=True, help='数据网格的列数')
    parser.add_argument('--sampling', '-s', type=int, default=500, help='采样点数量')
    parser.add_argument('--processed-data', '-p', help='直接使用预处理数据文件(.npz)而不是原始CSV')
    parser.add_argument('--save-processed', action='store_true', help='保存处理后的数据到.npz文件')
    
    # 可视化相关参数
    parser.add_argument('--fps', '-f', type=int, default=30, help='视频帧率')
    parser.add_argument('--dpi', '-d', type=int, default=150, help='视频分辨率(DPI)')
    parser.add_argument('--colormap', '-m', default='viridis', help='颜色映射名称 (使用 --list-colormaps 查看所有选项)')
    parser.add_argument('--custom-gradient', nargs=2, metavar=('COLOR1', 'COLOR2'), 
                        help='自定义渐变色, 提供两个颜色值(RGB或HEX), 例如: "#FF0000" "#0000FF"')
    parser.add_argument('--list-colormaps', action='store_true', help='列出所有可用的配色方案')
    parser.add_argument('--quality', '-q', choices=['low', 'medium', 'high'], default='high', help='视频质量')
    parser.add_argument('--type', '-t', choices=['all', 'heatmap', '3d', 'profiles'], default='all',
                       help='要生成的视频类型')
    
    # 3D视图参数
    parser.add_argument('--rotate', action='store_true', help='是否旋转3D视图')
    parser.add_argument('--no-rotate', action='store_false', dest='rotate', help='不旋转3D视图')
    parser.add_argument('--fixed-view', action='store_true', help='使用固定视角（优先级高于rotate）')
    parser.add_argument('--view-angles', type=str, help='自定义视角列表，格式为"elev1,azim1;elev2,azim2;..."')
    parser.add_argument('--elev', type=float, default=30.0, help='3D视图初始仰角')
    parser.add_argument('--azim', type=float, default=30.0, help='3D视图初始方位角')
    parser.add_argument('--rot-speed', type=float, default=1.0, help='3D视图旋转速度')
    parser.add_argument('--full-rotation', action='store_true', help='3D视图进行完整360度旋转')
    parser.add_argument('--partial-rotation', action='store_false', dest='full_rotation', help='3D视图在初始视角附近小幅摆动')
    
    # 特定时间点图像生成参数
    parser.add_argument('--time', type=float, help='生成特定时间点的静态图像而非视频')
    parser.add_argument('--time-start', action='store_true', help='生成时间序列开始时刻的静态图像')
    parser.add_argument('--time-middle', action='store_true', help='生成时间序列中间时刻的静态图像')
    parser.add_argument('--time-end', action='store_true', help='生成时间序列结束时刻的静态图像')
    parser.add_argument('--time-all', action='store_true', help='生成时间序列开始、中间和结束三个时刻的静态图像')
    
    # 设置默认值
    parser.set_defaults(rotate=True, full_rotation=True)
    
    args = parser.parse_args()
    
    # 确保输出文件夹存在
    os.makedirs(args.output, exist_ok=True)
    
    # 如果请求列出配色方案，打印并退出
    if args.list_colormaps:
        # 临时创建一个VisualizationGenerator实例，只用于列出配色方案
        processed_data = {
            'grid_data': None,
            'time_points': None,
            'min_signal': 0,
            'max_signal': 1,
            'min_time': 0,
            'max_time': 1,
            'rows': 1,
            'cols': 1,
            'data': {}
        }
        temp_viz = VisualizationGenerator(
            processed_data=processed_data,
            output_folder="."
        )
        temp_viz.list_available_colormaps()
        return 0
    
    try:
        # 处理数据
        processed_data = {}
        
        if args.processed_data:
            # 如果提供了预处理数据文件，直接加载
            logger.info(f"从文件 {args.processed_data} 加载预处理数据")
            import numpy as np
            
            try:
                data = np.load(args.processed_data)
                
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
                
                logger.info(f"已加载预处理数据，形状: {processed_data['grid_data'].shape}")
                
            except Exception as e:
                logger.error(f"加载预处理数据时出错: {e}")
                return 1
        else:
            # 创建数据处理器并处理数据
            logger.info(f"从文件夹 {args.input} 加载和处理数据")
            
            processor = DataProcessor(
                input_folder=args.input,
                rows=args.rows,
                cols=args.cols,
                sampling_points=args.sampling
            )
            
            # 获取处理后的数据
            processed_data = processor.get_processed_data()
            
            # 如果需要，保存处理后的数据
            if args.save_processed:
                output_file = os.path.join(args.output, "processed_data.npz")
                processor.save_processed_data(output_file)
                logger.info(f"已保存处理后的数据到 {output_file}")
        
        # 创建可视化生成器
        viz_gen = VisualizationGenerator(
            processed_data=processed_data,
            fps=args.fps,
            dpi=args.dpi,
            colormap=args.colormap,
            custom_gradient=args.custom_gradient,
            output_folder=args.output
        )
        
        # 检查是否生成特定时间点的静态图像
        if args.time is not None or args.time_start or args.time_middle or args.time_end or args.time_all:
            # 如果指定了具体时间
            if args.time is not None:
                if args.type == 'all' or args.type == 'heatmap':
                    viz_gen.generate_heatmap_at_time(
                        target_time=args.time,
                        title=f"信号强度热图 (时间: {args.time:.4f})"
                    )
                
                if args.type == 'all' or args.type == '3d':
                    # 3D表面图 - 添加视角处理
                    view_angles = None
                    if args.view_angles:
                        try:
                            # 期望格式为"elev1,azim1;elev2,azim2;..."
                            view_angles = []
                            angle_pairs = args.view_angles.split(';')
                            for pair in angle_pairs:
                                if ',' in pair:
                                    elev, azim = map(float, pair.split(','))
                                    view_angles.append((elev, azim))
                            logger.info(f"已解析 {len(view_angles)} 个自定义视角")
                        except Exception as e:
                            logger.error(f"解析视角列表时出错: {e}")
                            logger.error("格式应为 'elev1,azim1;elev2,azim2;...'")
                            view_angles = None
                    
                    viz_gen.generate_3d_surface_at_time(
                        target_time=args.time,
                        elev=args.elev,
                        azim=args.azim,
                        view_angles=view_angles,
                        title=f"3D信号表面 (时间: {args.time:.4f})"
                    )
                
                if args.type == 'all' or args.type == 'profiles':
                    viz_gen.generate_heatmap_with_profiles_at_time(
                        target_time=args.time,
                        title=f"带剖面热图 (时间: {args.time:.4f})"
                    )
                
                logger.info(f"已生成时间点 {args.time:.4f} 的静态图像")
            
            # 如果请求特定时间点
            if args.time_all or args.time_start:
                min_time = processed_data['min_time']
                viz_gen.generate_heatmap_at_time(
                    target_time=min_time,
                    output_file="time_series_start.png",
                    title="信号强度热图 (开始时刻)"
                )
                logger.info(f"已生成开始时刻 {min_time:.4f} 的热图")
            
            if args.time_all or args.time_middle:
                middle_time = (processed_data['min_time'] + processed_data['max_time']) / 2
                viz_gen.generate_heatmap_at_time(
                    target_time=middle_time,
                    output_file="time_series_middle.png",
                    title="信号强度热图 (中间时刻)"
                )
                logger.info(f"已生成中间时刻 {middle_time:.4f} 的热图")
            
            if args.time_all or args.time_end:
                max_time = processed_data['max_time']
                viz_gen.generate_heatmap_at_time(
                    target_time=max_time,
                    output_file="time_series_end.png",
                    title="信号强度热图 (结束时刻)"
                )
                logger.info(f"已生成结束时刻 {max_time:.4f} 的热图")
                
            return 0
        
        # 根据类型生成视频
        if args.type == 'all':
            viz_gen.generate_all_videos(args.quality)
        elif args.type == 'heatmap':
            viz_gen.generate_heatmap_video()
        elif args.type == '3d':
            # 解析视角列表（如果提供）
            view_angles = None
            if args.view_angles:
                try:
                    # 期望格式为"elev1,azim1;elev2,azim2;..."
                    view_angles = []
                    angle_pairs = args.view_angles.split(';')
                    for pair in angle_pairs:
                        if ',' in pair:
                            elev, azim = map(float, pair.split(','))
                            view_angles.append((elev, azim))
                    logger.info(f"已解析 {len(view_angles)} 个自定义视角")
                except Exception as e:
                    logger.error(f"解析视角列表时出错: {e}")
                    logger.error("格式应为 'elev1,azim1;elev2,azim2;...'")
                    view_angles = None
            
            # 生成3D表面视频
            viz_gen.generate_3d_surface_video(
                rotate_view=args.rotate,
                initial_elev=args.elev,
                initial_azim=args.azim,
                rotation_speed=args.rot_speed,
                full_rotation=args.full_rotation,
                fixed_view=args.fixed_view,
                view_angles=view_angles
            )
        elif args.type == 'profiles':
            viz_gen.generate_heatmap_with_profiles_video()
        
        logger.info("视频生成完成!")
        
    except Exception as e:
        logger.error(f"生成视频时出错: {e}")
        logger.exception(e)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())