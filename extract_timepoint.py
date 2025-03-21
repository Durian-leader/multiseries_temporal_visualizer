import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from loguru import logger
import sys

def extract_timepoint_data(npz_file, target_time=None, time_index=None):
    """
    从处理后的npz文件中提取特定时间点的数据
    
    Args:
        npz_file: npz文件路径
        target_time: 目标时间点 (与time_index二选一)
        time_index: 时间索引 (与target_time二选一)
    
    Returns:
        时间点，对应时间点的数据网格，元数据
    """
    logger.info(f"从 {npz_file} 加载数据...")
    data = np.load(npz_file, allow_pickle=True)
    
    # 提取基本数据
    time_points = data['time_points']
    grid_data = data['grid_data']
    rows = int(data['rows'])
    cols = int(data['cols'])
    min_time = float(data['min_time'])
    max_time = float(data['max_time'])
    
    # 提取文件名网格（如果存在）
    if 'filename_grid' in data:
        filename_grid = data['filename_grid']
        logger.info("加载了文件名网格数据")
    else:
        filename_grid = None
        logger.warning("数据中不包含文件名网格信息")
    
    logger.info(f"数据形状: {grid_data.shape}, 时间范围: {min_time:.4f} - {max_time:.4f}")
    
    # 确定时间索引
    if time_index is not None:
        # 直接使用提供的索引
        if time_index < 0 or time_index >= len(time_points):
            raise ValueError(f"时间索引 {time_index} 超出范围 [0, {len(time_points)-1}]")
        idx = time_index
        logger.info(f"使用指定的时间索引: {idx}, 对应时间点: {time_points[idx]:.4f}")
    elif target_time is not None:
        # 找到最接近目标时间的索引
        idx = np.abs(time_points - target_time).argmin()
        logger.info(f"目标时间 {target_time:.4f}, 最接近的时间点: {time_points[idx]:.4f}, 索引: {idx}")
    else:
        # 默认使用中间时间点
        idx = len(time_points) // 2
        logger.info(f"未指定时间，使用中间时间点: {time_points[idx]:.4f}, 索引: {idx}")
    
    # 提取该时间点的数据网格
    time_slice = grid_data[idx, :, :]
    
    metadata = {
        'time': time_points[idx],
        'time_index': idx,
        'rows': rows,
        'cols': cols,
        'min_time': min_time,
        'max_time': max_time,
        'time_points_count': len(time_points),
        'filename_grid': filename_grid
    }
    
    return time_points[idx], time_slice, metadata

def visualize_grid(time_point, data_grid, title=None, filename_grid=None, show_filenames=False, vmin=None, vmax=None):
    """
    Visualize the data grid
    
    Args:
        time_point: Time point
        data_grid: Data grid
        title: Chart title
        filename_grid: Filename grid
        show_filenames: Whether to display filenames on the grid
        vmin: Minimum value for colormap (optional)
        vmax: Maximum value for colormap (optional)
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(data_grid, cmap='viridis', interpolation='nearest', vmin=vmin, vmax=vmax)
    plt.colorbar(im, ax=ax, label='Signal Value')
    
    # Add title
    if title:
        ax.set_title(title)
    else:
        ax.set_title(f'Data Grid (Time: {time_point:.4f})')
    
    # Set axes
    ax.set_xticks(np.arange(data_grid.shape[1]))
    ax.set_yticks(np.arange(data_grid.shape[0]))
    
    # If there's a filename grid and display is requested, add filenames and values
    if filename_grid is not None and show_filenames:
        for i in range(data_grid.shape[0]):
            for j in range(data_grid.shape[1]):
                # Get the value at this position
                value = data_grid[i, j]
                
                # Create text content
                text_parts = []
                
                # Add filename if available
                if filename_grid[i, j] is not None:
                    # Get short filename (without extension) to avoid length issues
                    short_name = Path(filename_grid[i, j]).stem
                    text_parts.append(short_name)
                
                # Add value in scientific notation
                text_parts.append(f"{value:.2e}")
                
                # Display text in cell center
                display_text = "\n".join(text_parts)
                ax.text(j, i, display_text, ha="center", va="center", 
                       color="w", fontsize=8, alpha=0.8)
    
    plt.tight_layout()
    return fig

def export_filename_grid(metadata, output_path):
    """
    Export the filename grid to a CSV file
    
    Args:
        metadata: Metadata containing the filename grid
        output_path: Path to save the CSV file
    """
    if 'filename_grid' in metadata and metadata['filename_grid'] is not None:
        with open(output_path, 'w') as f:
            for row in metadata['filename_grid']:
                f.write(','.join([str(cell) if cell is not None else '' for cell in row]) + '\n')
        logger.info(f"文件名网格已导出到 {output_path}")
    else:
        logger.warning("没有可用的文件名网格数据，无法导出")

if __name__ == "__main__":
    # 设置日志
    logger.configure(handlers=[{"sink": sys.stdout, "level": "INFO"}])
    
    # 配置参数 - 可根据需要修改这些值
    npz_file = "my_processed_data_all_points.npz"  # NPZ文件路径
    target_time = None  # 目标时间点，设为None则使用时间索引或中间点
    time_index = None  # 时间索引，设为None则使用目标时间或中间点
    output_csv = "extracted_data.csv"  # 输出CSV文件路径，设为None则不导出
    save_fig_path = "data_grid.png"  # 保存图像路径，设为None则不保存
    show_visualization = True  # 是否显示可视化
    show_filenames = True  # 是否在图中显示文件名
    export_filenames_path = "filename_grid.csv"  # 导出文件名网格的路径，设为None则不导出
    vmin = None  # 自定义色彩映射最小值，设为None则使用数据最小值
    vmax = None  # 自定义色彩映射最大值，设为None则使用数据最大值
    
    # 提取数据
    time_point, data_grid, metadata = extract_timepoint_data(
        npz_file, target_time=target_time, time_index=time_index
    )
    
    # 输出数据摘要
    logger.info(f"时间点: {time_point:.4f}, 数据网格形状: {data_grid.shape}")
    
    # 可选: 导出文件名网格
    if export_filenames_path:
        export_filename_grid(metadata, export_filenames_path)
    
    # 可选: 保存为CSV
    if output_csv:
        output_path = Path(output_csv)
        np.savetxt(output_path, data_grid, delimiter=',', 
                  header=f'Time Point: {time_point}', comments='# ')
        logger.info(f"数据已保存到 {output_path}")
    
    # 可选: 可视化
    if show_visualization or save_fig_path:
        fig = visualize_grid(
            time_point, 
            data_grid, 
            filename_grid=metadata.get('filename_grid'),
            show_filenames=show_filenames,
            vmin=vmin,
            vmax=vmax
        )
        
        if save_fig_path:
            fig.savefig(save_fig_path, dpi=300, bbox_inches='tight')
            logger.info(f"图形已保存到 {save_fig_path}")
        
        if show_visualization:
            plt.show()
    
    # 示例：使用不同参数进行提取
    # 可以注释或取消注释以下代码块来测试不同的参数组合
    
    """
    # 示例1: 使用特定索引
    time_point2, data_grid2, metadata2 = extract_timepoint_data(
        npz_file, time_index=100
    )
    
    # 查看结果
    fig2 = visualize_grid(
        time_point2, 
        data_grid2,
        title=f"Data at index 100 (time: {time_point2:.4f})",
        filename_grid=metadata2.get('filename_grid'),
        show_filenames=True
    )
    
    # 保存并显示
    fig2.savefig("data_index_100.png", dpi=300)
    plt.figure(fig2.number)
    plt.show()
    
    # 示例2: 使用特定时间点，并设置colormap范围
    specific_time = metadata['min_time'] + (metadata['max_time'] - metadata['min_time']) * 0.75
    time_point3, data_grid3, metadata3 = extract_timepoint_data(
        npz_file, target_time=specific_time
    )
    
    # 自定义colormap范围
    custom_vmin = data_grid3.min() * 0.8
    custom_vmax = data_grid3.max() * 0.8
    
    # 查看结果
    fig3 = visualize_grid(
        time_point3, 
        data_grid3,
        title=f"Data at 75% of time range",
        filename_grid=metadata3.get('filename_grid'),
        show_filenames=True,
        vmin=custom_vmin,
        vmax=custom_vmax
    )
    
    # 保存并显示
    fig3.savefig("data_75percent_time.png", dpi=300)
    plt.figure(fig3.number)
    plt.show()
    """