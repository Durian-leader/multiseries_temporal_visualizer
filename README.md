# 振动数据处理与可视化工具

这个项目提供了一套完整的用于加载、处理、可视化和分析振动数据的Python工具套件。项目包含多个模块，应按以下顺序使用：

## 基础数据处理流程

1. `vibration_data_loader.py` - 加载和转换原始振动数据
2. `start_idx_visualized_select.py` - 可视化选择数据起始点
3. `debiasing.py` - 对数据进行去偏处理

## 高级数据处理与可视化

4. `data_processor.py` - 进一步数据处理和插值
5. `visualization_generator.py` - 生成高质量的可视化及动画

## 模块详细说明

### 1. 振动数据加载器 (vibration_data_loader.py)

#### 功能描述

这个模块提供了用于加载、处理和转换振动数据文件的工具类。主要功能包括：

- 从TXT文件读取振动数据和元数据
- 提取数据列的单位信息
- 将数据绘制为时间序列图
- 将数据导出为CSV格式
- 批量转换文件夹中的TXT文件为CSV文件

#### 使用方法

```python
# 批量转换TXT文件为CSV
from vibration_data_loader import VibrationDataLoader

# 将input/data2文件夹中的所有TXT文件转换为CSV，并保存到output/data2_csv文件夹
VibrationDataLoader.convert_txt_to_csv_batch("./input/data2", "./output/data2_csv")
```

单个文件的加载和处理：

```python
# 加载单个振动数据文件
loader = VibrationDataLoader.from_txt("./input/data2/example.txt")

# 绘制时间序列图
fig, ax = loader.plot_time_series()
plt.show()

# 导出为CSV
loader.to_csv("./output/example.csv")
```

### 2. 数据起始点选择器 (start_idx_visualized_select.py)

#### 功能描述

这个脚本提供了一个交互式界面，用于可视化选择每个数据文件的起始点。主要功能包括：

- 读取并显示CSV文件的数据
- 通过点击界面选择数据的起始点
- 从选定点开始截取数据并保存为新的CSV文件
- 批量处理多个文件

#### 使用方法

```python
from start_idx_visualized_select import StartIdxVisualizedSelect

# 创建处理器实例
processor = StartIdxVisualizedSelect(
    input_folder="./output/data2_csv",  # 输入文件夹（包含由loader生成的CSV文件）
    output_folder="./output/data2_csv_start-idx-reselected"  # 输出文件夹（存放截取后的CSV文件）
)

# 运行交互式选择过程
processor.run()
```

使用界面：
1. 点击图表上的任意位置选择起始点（会显示一条红色虚线）
2. 点击"Save & Next"按钮（或按'n'键）保存当前选择并进入下一个文件
3. 点击"Skip File"按钮（或按'k'键）跳过当前文件

### 3. 数据去偏处理 (debiasing.py)

#### 功能描述

这个脚本用于对数据进行去偏处理，主要功能包括：

- 处理每列数据，使其第一个值为0（去偏处理）
- 可选择将所有文件截断至最短文件的长度
- 批量处理文件夹中的所有CSV文件

#### 使用方法

```python
from debiasing import debias_csv_folder

# 处理已选择起始点的数据文件
debias_csv_folder(
    input_folder="./output/data2_csv_start-idx-reselected",  # 输入文件夹（包含选定起始点的CSV文件）
    output_folder="./output/data2_csv_start-idx-reselected_debiased",  # 输出文件夹（存放去偏后的CSV文件）
    truncate_to_min=True  # 是否将所有文件截断至最短文件的长度
)
```

或者使用命令行：

```bash
python debiasing.py --input ./output/data2_csv_start-idx-reselected --output ./output/data2_csv_start-idx-reselected_debiased --truncate
```

### 4. 数据处理器 (data_processor.py)

#### 功能描述

这个模块提供了高级数据处理功能，主要包括：

- 将多个CSV文件组织成网格结构
- 自动对时间序列数据进行同步和插值
- 创建统一的时间点采样
- 支持保存和加载处理后的数据

#### 使用方法

```python
from data_processor import DataProcessor

# 创建数据处理器
processor = DataProcessor(
    input_folder="./output/data2_csv_start-idx-reselected_debiased",  # 去偏后的数据文件夹
    rows=6,  # 数据网格的行数
    cols=6,  # 数据网格的列数
    sampling_points=500  # 采样点数量
)

# 获取处理后的数据
processed_data = processor.get_processed_data()

# 保存处理后的数据
processor.save_processed_data("processed_data.npz")

# 加载之前保存的数据
new_processor = DataProcessor()
new_processor.load_processed_data("processed_data.npz")
```

### 5. 可视化生成器 (visualization_generator.py)

#### 功能描述

这个模块提供了高质量的可视化生成功能，主要包括：

- 生成热图视频/图像
- 生成3D表面视频/图像（支持多种视角和动画效果）
- 生成带横纵剖面的热图视频/图像
- 支持多种颜色映射方案
- 支持保存各种格式的静态图像和动画视频

#### 使用方法

```python
from visualization_generator import VisualizationGenerator

# 创建可视化生成器
viz_gen = VisualizationGenerator(
    processed_data=processed_data,  # 从DataProcessor获取的处理后数据
    colormap="viridis",  # 颜色映射名称
    output_folder="./output/videos"  # 输出文件夹
)

# 生成热图视频
viz_gen.generate_heatmap_video(
    output_file="heatmap.mp4",
    title="信号强度热图"
)

# 生成3D表面视频（带旋转视角）
viz_gen.generate_3d_surface_video(
    output_file="3d_surface.mp4",
    title="3D信号表面",
    rotate_view=True,
    initial_elev=30,
    initial_azim=45
)

# 生成特定时间点的静态图像
middle_time = (processed_data['min_time'] + processed_data['max_time']) / 2
viz_gen.generate_heatmap_at_time(
    target_time=middle_time,
    output_file="heatmap.png",
    title="信号强度热图"
)

# 生成所有类型的视频
viz_gen.generate_all_videos(video_quality="high")
```

### 6. 主程序 (main.py)

#### 功能描述

主程序提供了命令行界面，用于快速生成各种可视化内容，功能包括：

- 自动处理输入数据文件夹中的数据
- 支持生成各种类型的视频和静态图像
- 提供丰富的命令行参数，灵活配置可视化效果
- 支持预处理数据的保存和加载

#### 使用方法

```bash
# 生成所有类型的视频
python main.py --input ./output/data2_csv_start-idx-reselected_debiased --rows 6 --cols 6

# 使用特定颜色映射方案
python main.py --input ./output/data2_csv_start-idx-reselected_debiased --rows 6 --cols 6 --colormap jet

# 生成3D表面视频并自定义视角
python main.py --input ./output/data2_csv_start-idx-reselected_debiased --rows 6 --cols 6 --type 3d \
  --elev 45 --azim 30 --rot-speed 0.5
```

## 完整处理流程

以下是完整的振动数据处理与可视化流程：

### 第一阶段：基础数据处理

1. **数据加载和转换**：
   ```python
   # 步骤1：将原始TXT文件转换为CSV
   from vibration_data_loader import VibrationDataLoader
   
   VibrationDataLoader.convert_txt_to_csv_batch(
       "./input/data2",  # 原始TXT文件所在文件夹
       "./output/data2_csv"  # 转换后CSV文件的输出文件夹
   )
   ```

2. **选择数据起始点**：
   ```python
   # 步骤2：选择每个文件的数据起始点
   from start_idx_visualized_select import StartIdxVisualizedSelect
   
   processor = StartIdxVisualizedSelect(
       "./output/data2_csv",  # 步骤1的输出文件夹
       "./output/data2_csv_start-idx-reselected"  # 截取后的输出文件夹
   )
   processor.run()
   ```

3. **数据去偏处理**：
   ```python
   # 步骤3：对数据进行去偏处理
   from debiasing import debias_csv_folder
   
   debias_csv_folder(
       "./output/data2_csv_start-idx-reselected",  # 步骤2的输出文件夹
       "./output/data2_csv_start-idx-reselected_debiased",  # 去偏处理后的输出文件夹
       truncate_to_min=True  # 将所有文件截断至最短文件的长度
   )
   ```

### 第二阶段：高级数据处理与可视化

4. **数据网格处理与插值**：
   ```python
   # 步骤4：创建数据网格并进行插值同步
   from data_processor import DataProcessor
   
   processor = DataProcessor(
       input_folder="./output/data2_csv_start-idx-reselected_debiased",  # 去偏处理后的数据文件夹
       rows=6,  # 数据网格的行数
       cols=6,  # 数据网格的列数
       sampling_points=500  # 采样点数量
   )
   
   # 保存处理后的数据供后续使用
   processor.save_processed_data("processed_data.npz")
   ```

5. **生成可视化内容**：
   ```python
   # 步骤5：创建可视化生成器并生成各种可视化
   from visualization_generator import VisualizationGenerator
   
   # 获取处理后的数据
   processed_data = processor.get_processed_data()
   
   # 创建可视化生成器
   viz_gen = VisualizationGenerator(
       processed_data=processed_data,
       colormap="viridis",  # 颜色映射
       output_folder="./output/videos"  # 输出文件夹
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
   viz_gen.generate_3d_surface_at_time(
       target_time=middle_time,
       output_file="3d_surface.png",
       title="3D信号表面"
   )
   ```


## 主程序

`main.py` 提供了一个命令行工具，可用于快速生成可视化内容：

```bash
# 生成所有类型的视频
python main.py --input ./output/data2_csv_start-idx-reselected_debiased --rows 6 --cols 6 --output ./output/videos

# 只生成3D表面视频
python main.py --input ./output/data2_csv_start-idx-reselected_debiased --rows 6 --cols 6 --type 3d

# 生成特定时间点的静态图像
python main.py --input ./output/data2_csv_start-idx-reselected_debiased --rows 6 --cols 6 --time 0.5

# 查看所有颜色映射选项
python main.py --list-colormaps
```

## 日志

所有脚本都使用loguru进行日志记录，日志文件将保存在当前目录下：
- `vibration_data_loader.log` - 数据加载日志
- `start_idx_select.log` - 起始点选择日志
- `main.log` - 主程序日志
- `logs/visualization_generator.log` - 可视化生成日志

## 依赖项

- Python 3.7+
- pandas
- numpy
- matplotlib
- scipy
- tqdm (进度条显示)
- loguru (日志记录)

## 安装依赖

请参考 `INSTALLATION.md` 文件获取详细的安装指南，或使用以下命令安装基本依赖：

```bash
pip install pandas numpy matplotlib scipy tqdm loguru
```

### 视频生成依赖

为了生成高质量的MP4视频，还需要安装FFmpeg。详细安装步骤请查阅 `INSTALLATION.md`。