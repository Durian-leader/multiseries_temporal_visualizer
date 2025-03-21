# 振动数据处理与可视化工具系统

本系统是一套完整的振动数据处理与可视化解决方案，支持从原始数据加载到高质量可视化内容生成的全流程处理。系统采用模块化设计，每个模块专注于特定功能，可单独使用或组合使用。

## 系统特点

- **完整的数据处理流水线**：提供从原始数据到可视化的全流程支持
- **交互式数据预处理**：通过图形界面选择数据起始点
- **高质量可视化输出**：支持热图、3D表面图和带剖面的热图等多种可视化形式
- **丰富的配色方案**：支持多种内置配色和自定义渐变色
- **灵活的参数配置**：支持命令行参数和代码API，可高度定制
- **多平台兼容**：支持Windows、macOS和Linux系统
- **完善的中文支持**：界面、日志和可视化内容均支持中文

## 系统架构

系统由五个主要模块组成，按处理流程顺序：

1. **数据加载器 (vibration_data_loader.py)**：
   - 读取原始TXT振动数据文件
   - 提取元数据和单位信息
   - 转换为CSV格式便于后续处理

2. **起始点选择器 (start_idx_visualized_select.py)**：
   - 提供交互式界面选择数据起始点
   - 可视化显示数据曲线
   - 批量处理多个文件

3. **数据去偏处理 (debiasing.py)**：
   - 处理每列数据使其第一个值为0
   - 可选择将所有文件截断至最短文件的长度
   - 批量处理整个文件夹

4. **高级数据处理器 (data_processor.py)**：
   - 将CSV文件组织成网格结构
   - 对时间序列数据进行插值和同步
   - 创建统一的时间点采样

5. **可视化生成器 (visualization_generator.py)**：
   - 生成多种类型的动画和静态图像
   - 支持丰富的视角和配色选项
   - 输出高质量MP4/GIF/HTML格式内容

## 安装指南

### 基本依赖

```bash
pip install numpy pandas matplotlib scipy tqdm loguru
```

### FFmpeg安装（用于生成高质量视频）

请参考 `INSTALLATION.md` 文件获取详细的FFmpeg安装步骤。各平台安装方法概述：

- **Windows**: 下载FFmpeg并添加到系统PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` 或同等命令

## 使用指南

### 基本数据处理流程

#### 1. 数据加载和转换

```python
# 将原始TXT文件转换为CSV
from vibration_data_loader import VibrationDataLoader

VibrationDataLoader.convert_txt_to_csv_batch(
    "./input/data2",  # 原始TXT文件所在文件夹
    "./output/data2_csv"  # 输出文件夹
)
```

#### 2. 选择数据起始点

```python
# 交互式选择每个文件的起始点
from start_idx_visualized_select import StartIdxVisualizedSelect

processor = StartIdxVisualizedSelect(
    "./output/data2_csv",  # 输入文件夹
    "./output/data2_csv_start-idx-reselected"  # 输出文件夹
)
processor.run()
```

使用交互界面：
- 点击图表选择起始点（显示红色虚线）
- 点击"Save & Next"（或按'n'键）保存并进入下一个文件
- 点击"Skip File"（或按'k'键）跳过当前文件

#### 3. 数据去偏处理

```python
# 数据去偏处理
from debiasing import debias_csv_folder

debias_csv_folder(
    "./output/data2_csv_start-idx-reselected",  # 输入文件夹
    "./output/data2_csv_start-idx-reselected_debiased",  # 输出文件夹
    truncate_to_min=True  # 是否将所有文件截断至最短文件长度
)
```

#### 4. 高级数据处理

```python
# 创建数据网格并进行插值同步
from data_processor import DataProcessor

processor = DataProcessor(
    input_folder="./output/data2_csv_start-idx-reselected_debiased",
    rows=6,  # 数据网格的行数
    cols=6,  # 数据网格的列数
    sampling_points=500  # 采样点数量
)

# 保存处理后的数据供后续使用
processed_data = processor.get_processed_data()
processor.save_processed_data("processed_data.npz")
```

#### 5. 生成可视化内容

```python
# 创建可视化生成器
from visualization_generator import VisualizationGenerator

viz_gen = VisualizationGenerator(
    processed_data=processed_data,
    colormap="viridis",
    output_folder="./videos"
)

# 生成各种可视化
viz_gen.generate_all_videos()  # 生成所有类型的视频

# 生成特定时间点的静态图像
middle_time = (processed_data['min_time'] + processed_data['max_time']) / 2
viz_gen.generate_heatmap_at_time(
    target_time=middle_time,
    output_file="heatmap.png",
    title="信号强度热图"
)
```

### 使用命令行工具

系统提供了命令行工具（main.py）用于快速生成可视化内容：

```bash
# 生成所有类型的视频
python main.py --input ./output/data2_csv_start-idx-reselected_debiased --rows 6 --cols 6

# 生成3D表面视频
python main.py --input ./output/data2_csv_start-idx-reselected_debiased --rows 6 --cols 6 --type 3d

# 生成特定时间点的静态图像
python main.py --input ./output/data2_csv_start-idx-reselected_debiased --rows 6 --cols 6 --time 0.5

# 查看所有配色方案
python main.py --list-colormaps
```

## 高级功能

### 数据预处理和复用

对于大型数据集，可以先处理并保存数据，然后在多次可视化时复用：

```bash
# 处理数据并保存
python main.py --input ./large_data --rows 10 --cols 10 --save-processed

# 使用预处理数据
python main.py --processed-data ./videos/processed_data.npz --type 3d
```

### 3D视图增强功能

#### 视频生成功能 (`generate_3d_surface_video`)

- **固定视角模式**：完全固定视角，不进行任何旋转
  ```bash
  python main.py --input ./data_csv --rows 6 --cols 6 --type 3d --fixed-view --elev 30 --azim 45
  ```

- **自定义视角序列**：按照预定义的视角序列进行逐帧切换
  ```bash
  python main.py --input ./data_csv --rows 6 --cols 6 --type 3d --fixed-view --view-angles "20,30;40,120;60,210;30,300"
  ```

- **旋转模式**：完整360度旋转或小幅度摆动
  ```bash
  python main.py --input ./data_csv --rows 6 --cols 6 --type 3d --rot-speed 0.7 --full-rotation
  ```

#### 静态图像生成功能 (`generate_3d_surface_at_time`)

- **多视角模式**：一次性生成多个不同视角的3D表面图
  ```bash
  python main.py --input ./data_csv --rows 6 --cols 6 --time 0.5 --view-angles "20,30;60,45;40,120;30,210"
  ```

### 配色方案

系统支持多种配色方案，包括：

- **连续数据配色**：viridis, plasma, inferno, magma, cividis, turbo
- **经典渐变**：jet, rainbow, ocean, terrain
- **高对比**：hot, cool, copper
- **科学数据常用**：RdBu, coolwarm, seismic, spectral
- **单色渐变**：Blues, Reds, Greens, YlOrRd, BuPu
- **色盲友好方案**：cividis, viridis

也可以自定义渐变色，例如：`--custom-gradient "#FF0000" "#0000FF"`（从红色到蓝色）

## 文件夹结构

```
project/
├── input/
│   └── data2/          # 原始TXT振动数据文件
├── output/
│   ├── data2_csv/      # 转换后的CSV文件
│   ├── data2_csv_start-idx-reselected/  # 选择起始点后的CSV文件
│   └── data2_csv_start-idx-reselected_debiased/  # 去偏处理后的数据
├── videos/             # 可视化输出文件夹（视频和图像）
├── logs/               # 日志文件夹
├── vibration_data_loader.py  # 数据加载和转换脚本
├── start_idx_visualized_select.py  # 数据起始点选择脚本
├── debiasing.py  # 数据去偏处理脚本
├── data_processor.py  # 高级数据处理脚本
├── visualization_generator.py  # 可视化生成脚本
├── main.py  # 主程序（可视化命令行工具）
└── INSTALLATION.md  # 安装指南
```

## 故障排除

- **FFmpeg相关问题**：请确保FFmpeg正确安装并添加到PATH
- **中文显示问题**：确保安装了适当的中文字体（详见`INSTALLATION.md`）
- **内存错误**：对于大型数据集，考虑降低`sampling_points`参数值
- **文件格式问题**：确保原始数据文件格式正确，包含至少两列数据

## 扩展开发

系统设计为模块化结构，可以轻松扩展：

- 添加新的可视化类型到 `visualization_generator.py`
- 扩展数据处理功能到 `data_processor.py`
- 在 `main.py` 中添加新的命令行参数

## 示例结果

使用本系统可以生成的典型可视化内容包括：

1. **热图动画**：显示整个时间序列的信号强度变化
2. **3D表面动画**：立体展示信号值随位置和时间的变化
3. **带剖面的热图**：同时显示横纵剖面的信号值
4. **特定时间点的静态图像**：针对关键时间点的详细分析

## 日志系统

所有模块都使用loguru进行日志记录，日志文件将保存在相应位置：
- `vibration_data_loader.log` - 数据加载日志
- `start_idx_select.log` - 起始点选择日志
- `main.log` - 主程序日志
- `logs/visualization_generator.log` - 可视化生成日志