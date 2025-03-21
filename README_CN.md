# 多序列时间数据可视化工具

这是一个全面的Python工具包，用于处理、分析和可视化多序列时间数据。该工具专注于将振动数据或其他时间序列数据集转换为高质量的可视化效果和动画。

## 功能特点

- **数据处理流程**：将原始数据文件转换为同步的、便于分析的格式
- **交互式数据选择**：直观地选择数据的起始点和感兴趣区域
- **高质量可视化**：生成热图、3D表面图和剖面图
- **视频生成**：创建展示数据随时间变化的流畅动画
- **灵活配置**：自定义颜色、分辨率和视觉风格
- **数据提取**：提取特定时间点的数据进行详细分析

## 项目结构

```
multiseries_temporal_visualizer/
├── utils/                      # 核心工具模块
│   ├── dataprocess/            # 数据处理工具
│   │   ├── vibration_data_loader.py    # 原始数据加载和转换
│   │   ├── start_idx_visualized_select.py  # 交互式起始点选择
│   │   └── debiasing.py        # 数据归一化和去偏
│   └── visualize/              # 可视化工具
│       ├── data_processor.py   # 数据同步和插值
│       └── visualization_generator.py  # 生成可视化和动画
├── input/                      # 输入数据目录 
│   └── data/                   # 原始数据文件
├── output/                     # 输出目录结构
│   ├── data_csv/               # 转换后的CSV文件
│   ├── data_csv_start-idx-reselected/  # 选择起始点后的文件
│   └── videos/                 # 生成的视频和可视化效果
├── extract_timepoint.py        # 提取特定时间点的数据
└── INSTALLATION.md             # 详细安装说明
```

## 数据处理工作流程

### 1. 数据加载与转换

将原始TXT文件转换为CSV格式：

```python
from utils.dataprocess.vibration_data_loader import VibrationDataLoader

# 将文件夹中的所有TXT文件转换为CSV
VibrationDataLoader.convert_txt_to_csv_batch(
    "./input/data",  # 包含TXT文件的输入文件夹
    "./output/data_csv"  # CSV文件的输出文件夹
)
```

### 2. 交互式数据起始点选择

使用交互界面为每个数据文件选择起始点：

```python
from utils.dataprocess.start_idx_visualized_select import StartIdxVisualizedSelect

processor = StartIdxVisualizedSelect(
    "./output/data_csv",  # 包含CSV文件的输入文件夹
    "./output/data_csv_start-idx-reselected"  # 处理后文件的输出文件夹
)
processor.run()
```

使用界面：
- 点击图表上的任意位置选择起始点（显示为红色虚线）
- 点击"Save & Next"（或按'n'键）保存并进入下一个文件
- 点击"Skip File"（或按'k'键）跳过当前文件

### 3. 数据去偏处理

通过将每个序列的第一个值设为零来归一化数据：

```python
from utils.dataprocess.debiasing import debias_csv_folder

debias_csv_folder(
    "./output/data_csv_start-idx-reselected",  # 选择起始点后的输入文件夹 
    "./output/data_csv_start-idx-reselected_debiased",  # 去偏后数据的输出文件夹
    truncate_to_min=True  # 将所有文件截断至最短文件的长度
)
```

### 4. 数据网格处理与同步

将多个CSV文件组织成网格结构并同步其时间点：

```python
from utils.visualize.data_processor import DataProcessor

# 创建一个6x6网格的数据处理器
processor = DataProcessor(
    input_folder="./output/data_csv_start-idx-reselected_debiased",
    rows=6,
    cols=6,
    sampling_points=500  # 采样点数量
)

# 保存处理后的数据供后续使用
processor.save_processed_data("my_processed_data.npz")
```

### 5. 可视化生成

使用处理后的数据创建高质量可视化：

```python
from utils.visualize.visualization_generator import VisualizationGenerator

# 获取处理后的数据
processed_data = processor.get_processed_data()

# 创建可视化生成器
viz_gen = VisualizationGenerator(
    processed_data=processed_data,
    colormap="viridis",  # 颜色映射
    output_folder="./output/videos"  # 输出文件夹
)

# 生成所有类型的视频
viz_gen.generate_all_videos()

# 生成特定时间点的热图
middle_time = (processed_data['min_time'] + processed_data['max_time']) / 2
viz_gen.generate_heatmap_at_time(
    target_time=middle_time,
    output_file="heatmap.png",
    title="信号强度热图"
)
```

### 6. 提取特定时间点的数据

提取并可视化特定时间点的数据：

```python
from extract_timepoint import extract_timepoint_data, visualize_grid

# 提取特定时间点的数据
time_point, data_grid, metadata = extract_timepoint_data(
    "my_processed_data.npz",
    target_time=1.5  # 目标时间点
)

# 可视化提取的数据
fig = visualize_grid(
    time_point,
    data_grid,
    title="t=1.5时刻的数据",
    filename_grid=metadata.get('filename_grid'),
    show_filenames=True
)
```

## 可用的可视化类型

1. **热图视频**：以2D色彩图显示随时间变化的强度
   ```python
   viz_gen.generate_heatmap_video(output_file="heatmap.mp4", title="信号强度热图")
   ```

2. **3D表面视频**：将数据显示为3D表面，支持旋转视角
   ```python
   viz_gen.generate_3d_surface_video(
       output_file="3d_surface.mp4",
       title="3D信号表面",
       rotate_view=True,
       initial_elev=30,
       initial_azim=45
   )
   ```

3. **带剖面的热图视频**：组合显示热图和剖面线
   ```python
   viz_gen.generate_heatmap_with_profiles_video(
       output_file="heatmap_with_profiles.mp4",
       title="带信号剖面的热图"
   )
   ```

4. **静态可视化**：生成特定时间点的静态图像
   ```python
   viz_gen.generate_heatmap_at_time(target_time=1.5, output_file="heatmap_t1.5.png")
   viz_gen.generate_3d_surface_at_time(target_time=1.5, output_file="surface_t1.5.png")
   ```

## 颜色映射选项

该工具包支持多种可视化的颜色映射选项：

- **连续数据**：viridis, plasma, inferno, magma, cividis, turbo
- **经典渐变**：jet, rainbow, ocean, terrain
- **高对比度**：hot, cool, copper
- **科学数据**：RdBu, coolwarm, seismic, spectral
- **单色渐变**：Blues, Reds, Greens, YlOrRd, BuPu
- **色盲友好**：cividis, viridis

## 依赖项

- Python 3.7+
- numpy
- pandas
- matplotlib
- scipy
- tqdm
- loguru
- FFmpeg（用于视频生成）

详细安装说明，请参见[INSTALLATION_CN.md](INSTALLATION_CN.md)。 