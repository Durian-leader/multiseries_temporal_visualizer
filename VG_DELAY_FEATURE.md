# Vg信号时间偏移功能说明

## 功能概述

StartIdxVisualizedSelect类现在支持在读取Vg文件时自动应用时间偏移，实现"所见即所得"的信号对齐体验。用户在界面上看到的对齐关系就是实际数据处理时使用的对齐关系。

## 新增参数

### `vg_delay` (float)
- **默认值**: `0.0025` (2.5毫秒)
- **单位**: 秒
- **说明**: Vg信号相对于原始信号的时间延时
- **可配置**: 在类初始化时动态设置

## 使用方法

### 基本使用
```python
from utils.dataprocess.start_idx_visualized_select import StartIdxVisualizedSelect

# 使用默认延时 (2.5ms)
processor = StartIdxVisualizedSelect(
    input_folder="./input/data",
    output_folder="./output/processed"
)

# 自定义延时
processor = StartIdxVisualizedSelect(
    input_folder="./input/data", 
    output_folder="./output/processed",
    vg_delay=0.003  # 3ms延时
)

# 无延时
processor = StartIdxVisualizedSelect(
    input_folder="./input/data",
    output_folder="./output/processed", 
    vg_delay=0.0  # 无延时
)
```

### 在00select_start_idx.py中的使用
```python
# 3. 使用StartIdxVisualizedSelect进行起始点选择
logger.info("开始进行数据起始点选择")
processor_idx = StartIdxVisualizedSelect(
    "./output/data_csv_denoised",
    "./output/data_csv_denoised_start-idx-reselected",
    vg_delay=0.0025  # Vg信号延时2.5ms用于信号对齐
)
processor_idx.run()
```

## 技术实现

### 时间偏移应用机制
1. **文件读取阶段**: 在`read_data_file`方法中自动检测V结尾的文件
2. **自动偏移**: 对Vg文件的时间列自动添加配置的偏移量
3. **统一时间域**: 两个信号在加载后即处于同一时间参考系
4. **所见即所得**: 用户看到的对齐就是实际的数据对齐

### 关键特性
- **读取时处理**: 偏移在文件读取阶段就完成，避免后续处理复杂性
- **透明操作**: 加载后两个信号在时间域完全对齐，无需特殊处理
- **精确截取**: 选择点对应的时间就是实际截取的时间
- **简化逻辑**: 消除了显示和处理之间的时间差异

## 界面变化

### 标题显示
- Vg信号子图标题会显示延时信息
- 例如: `"Vg Signal: 11V.txt (延时2.5ms)"`
- 无延时时显示: `"Vg Signal: 11V.txt (无延时)"`

### 日志输出
```
找到 24 个有Vg配对的数据文件
Vg信号延时设置: 2.5ms
正在处理文件: ./input/11.txt
对应的Vg文件: ./input/11V.txt
成功读取CSV文件: ./input/11V.txt
已对Vg文件应用 2.5ms 时间偏移
已保存截断数据到 ./output/11.csv (基于视觉对齐选择的起始点)
```

## 应用场景

### 适用情况
- **硬件延时补偿**: 补偿测量系统中的固有延时
- **信号同步**: 对齐来自不同传感器的信号
- **时序校正**: 修正数据采集过程中的时间偏差

### 延时值设置建议
- **2.5ms**: 默认值，适用于大多数情况
- **0-10ms**: 常见的硬件延时范围
- **自定义值**: 根据具体测量系统确定

## 注意事项

1. **方向性**: 正值表示Vg信号相对原始信号的延后
2. **精度**: 延时精度取决于数据采样率
3. **一致性**: 同一批数据应使用相同的延时设置
4. **验证**: 建议通过已知特征点验证延时设置的正确性

## 兼容性

- **向后兼容**: 不指定`vg_delay`参数时使用默认值2.5ms
- **灵活配置**: 可在任何使用场景中动态调整延时值
- **无副作用**: 延时设置不影响其他功能的正常使用