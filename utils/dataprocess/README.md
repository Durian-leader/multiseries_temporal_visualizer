# 振动数据处理工具

这个项目提供了一套用于加载、可视化和处理振动数据的Python工具。项目包含三个主要脚本，应按以下顺序使用：

1. `vibration_data_loader.py` - 加载和转换振动数据
2. `start_idx_visualized_select.py` - 可视化选择数据起始点
3. `debiasing.py` - 对数据进行去偏处理

## 1. 振动数据加载器 (vibration_data_loader.py)

### 功能描述

这个模块提供了用于加载、处理和转换振动数据文件的工具类。主要功能包括：

- 从TXT文件读取振动数据和元数据
- 提取数据列的单位信息
- 将数据绘制为时间序列图
- 将数据导出为CSV格式
- 批量转换文件夹中的TXT文件为CSV文件

### 使用方法

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

## 2. 数据起始点选择器 (start_idx_visualized_select.py)

### 功能描述

这个脚本提供了一个交互式界面，用于可视化选择每个数据文件的起始点。主要功能包括：

- 读取并显示CSV文件的数据
- 通过点击界面选择数据的起始点
- 从选定点开始截取数据并保存为新的CSV文件
- 批量处理多个文件

### 使用方法

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

## 3. 数据去偏处理 (debiasing.py)

### 功能描述

这个脚本用于对数据进行去偏处理，主要功能包括：

- 处理每列数据，使其第一个值为0（去偏处理）
- 可选择将所有文件截断至最短文件的长度
- 批量处理文件夹中的所有CSV文件

### 使用方法

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

## 完整处理流程

以下是完整的振动数据处理流程：

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
       "./output/data2_csv_start-idx-reselected_debiased",  # 最终结果的输出文件夹
       truncate_to_min=True  # 将所有文件截断至最短文件的长度
   )
   ```


## 日志

所有脚本都使用loguru进行日志记录，日志文件将保存在当前目录下：
- `vibration_data_loader.log`
- `start_idx_select.log`
- `vibration_data_loader.log`

## 依赖项

- Python 3.7+
- pandas
- numpy
- matplotlib
- loguru

## 安装依赖

```bash
pip install pandas numpy matplotlib loguru
```