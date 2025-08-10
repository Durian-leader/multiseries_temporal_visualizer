# 多序列时间数据可视化工具

一个全面的Python和MATLAB工具包，专门用于处理、分析和可视化来自科学实验的多序列时间数据，特别适用于材料科学中的振动/膨胀测量。

## 演示视频
- https://youtu.be/eMQt-ECYRZA
- https://youtu.be/zs1seIiErXs  
- https://youtu.be/VFoZmemtraI

## 核心功能

### 🔄 完整数据处理流水线
- **原始数据加载**：TXT文件转CSV格式，包含元数据解析
- **小波去噪**：可配置的小波包去噪，使用db6小波
- **交互式起始点选择**：支持Vg信号的时间对齐可视化GUI
- **基线校正**：自动和手动基线漂移校正
- **网格数据组织**：将单个时间序列转换为空间网格格式
- **格式转换**：NPZ到MATLAB MAT格式的跨平台兼容性

### 📊 高级可视化
- **高质量视频生成**：热力图、3D表面图和横截面剖面图
- **静态可视化**：时间点快照和数据导出
- **MATLAB集成**：使用MATLAB脚本进行专业级可视化
- **多种色彩方案**：20+种科学色彩映射，包括viridis、plasma、turbo
- **交互式控制**：缩放、平移和重置功能

### 🛠 用户友好界面
- **集成Jupyter笔记本**：具有进度跟踪和错误处理的完整流水线
- **命令行界面**：具有广泛配置选项的灵活脚本
- **GUI工具**：交互式基线校正和起始点选择
- **实时预览**：处理过程中的数据验证和可视化

## 快速开始

### 方法1：集成Jupyter笔记本（推荐）
```bash
jupyter notebook main.ipynb
```
该笔记本提供完整的交互式流水线，具有：
- 实时进度跟踪
- 全面错误处理
- 每步数据验证
- 内置可视化预览

### 方法2：命令行流水线
```bash
# 步骤1：数据预处理（TXT→CSV，包含去噪和对齐）
python python_dataprepare_visualize/00select_start_idx.py \
  --input-dir ./input/data \
  --output-dir ./output/processed_csv \
  --rows 4 --cols 6

# 步骤2：可选基线校正
python python_dataprepare_visualize/00_5_manual_baseline_correction.py \
  -i ./output/processed_csv \
  -o ./output/baseline_corrected_csv \
  -a  # 自动模式，或使用-m进行手动GUI

# 步骤3：转换为NPZ格式
python python_dataprepare_visualize/01csv2npz.py \
  --input-folder ./output/baseline_corrected_csv \
  --output-file ./output/my_processed_data.npz \
  --rows 4 --cols 6

# 步骤4：生成MATLAB文件
python python_dataprepare_visualize/npz_to_mat.py \
  --input-file ./output/my_processed_data.npz \
  --output-file ./my_processed_data.mat
```

### 方法3：单独处理脚本
```bash
# 视频生成（5点采样）
python python_dataprepare_visualize/01sample.py
python python_dataprepare_visualize/03video.py

# 详细分析（所有数据点）
python python_dataprepare_visualize/02picture.py
```

## 项目架构

```
multiseries_temporal_visualizer/
├── main.ipynb                          # 🎯 集成流水线笔记本
├── python_dataprepare_visualize/       # 核心处理脚本
│   ├── 00select_start_idx.py          # 数据预处理流水线
│   ├── 00_5_manual_baseline_correction.py  # 基线校正
│   ├── 01sample.py                     # 5点采样
│   ├── 01csv2npz.py                    # CSV到NPZ转换
│   ├── 02picture.py                    # 静态可视化
│   ├── 03video.py                      # 视频生成
│   ├── npz_to_mat.py                   # NPZ到MATLAB转换
│   └── utils/                          # 核心工具
│       ├── dataprocess/                # 数据处理工具
│       │   ├── vibration_data_loader.py      # TXT/CSV数据加载器
│       │   ├── start_idx_visualized_select.py # 交互式起始点选择
│       │   ├── baseline_correction.py         # GUI基线校正
│       │   ├── wavelet_denoise.py             # 小波去噪
│       │   └── debiasing.py                   # 基线漂移校正
│       └── visualize/                  # 可视化工具
│           ├── data_processor.py              # 网格数据处理
│           ├── visualization_generator.py     # 视频/图像生成
│           └── extract_timepoint.py           # 时间点提取
├── matlab_数据可视化_比python精美/      # MATLAB可视化脚本
│   ├── main01_3d.m                     # 3D表面图
│   ├── main02_heatmap.m                # 热力图可视化
│   └── main03_heatmapwithprofile.m     # 带剖面的热力图
├── input/data/                         # 原始数据文件（TXT格式）
├── output/                             # 处理输出
└── logs/                              # 处理日志
```

## 数据处理工作流程

### 核心流水线
1. **原始数据（TXT文件）** → `00select_start_idx.py` → **对齐的CSV文件**
2. **对齐的CSV** → `00_5_manual_baseline_correction.py` → **基线校正的CSV**
3. **校正的CSV** → `01csv2npz.py` → **NPZ网格数据**
4. **NPZ数据** → `npz_to_mat.py` → **MATLAB MAT文件**
5. **MAT文件** → **MATLAB脚本** → **高质量可视化**

### 关键处理特性
- **Vg信号支持**：自动时间延迟补偿（默认：2.5毫秒）
- **网格组织**：可配置的空间排列（如4×6网格）
- **内存效率**：大数据集的分块处理
- **数据验证**：全面的错误检查和恢复

## 高级功能

### 交互式起始点选择
- **双信号显示**：Vg电压和原始信号在同步子图中比较显示
- **可视化对齐**：所见即所得的时间对齐，支持可配置Vg延时
- **时间延迟补偿**：自动Vg信号偏移（默认：2.5毫秒）实现正确对齐
- **高级缩放控制**：
  - 以光标为中心的鼠标滚轮缩放
  - 双信号图X轴同步缩放
  - 各信号Y轴独立缩放
- **精确导航功能**：
  - Shift+拖拽或中键拖拽进行平移
  - 'r'键或重置视图按钮恢复原始视图
  - 智能缩放保持已选择的起始点标记
- **键盘快捷键**：'n'下一个，'k'跳过，'r'重置视图
- **硬件延时补偿**：可配置Vg延时（0-10毫秒）用于测量系统对齐

### 基线校正模式
- **自动模式**：使用首末点进行线性校正
- **手动模式**：自定义基线点选择的交互式GUI
- **跳过模式**：不需要时绕过校正

### 小波去噪
- **可配置小波**：默认db6，可自定义级别
- **选择性滤波**：保留特定频率成分
- **前后对比**：去噪效果的可视化验证

### 可视化选项
- **热力图动画**：时间演进的2D彩色图
- **3D表面视频**：具有可定制角度的旋转3D表面图
- **剖面分析**：带热力图的横截面视图
- **静态快照**：特定时间点的高分辨率图像
- **多种导出格式**：MP4、GIF、PNG、CSV数据导出

### 色彩映射选项
- **科学色彩图**：viridis、plasma、inferno、magma、cividis、turbo
- **经典渐变**：jet、rainbow、ocean、terrain、hot、cool
- **发散方案**：RdBu、coolwarm、seismic、spectral
- **单色渐变**：Blues、Reds、Greens、YlOrRd、BuPu
- **色盲友好**：cividis、viridis针对辅助功能优化

## MATLAB可视化

生成MAT文件后，使用MATLAB脚本进行增强可视化：

```matlab
% 加载处理后的数据
data = load('my_processed_data.mat');

% 运行可视化脚本
main01_3d          % 3D表面动画
main02_heatmap     % 热力图可视化
main03_heatmapwithprofile  % 带横截面剖面的热力图
```

## 配置选项

### 网格设置
- **灵活尺寸**：可配置行×列（如4×6、6×6）
- **自然文件排序**：文件命名模式的自动处理
- **缺失文件处理**：不完整网格的优雅处理

### 处理参数
- **小波设置**：类型（db6），分解级别（6），节点选择
- **Vg信号对齐**：
  - 默认延迟：2.5毫秒用于硬件补偿
  - 可配置范围：0-10毫秒适应不同测量系统
  - 文件加载时实时应用，实现所见即所得对齐
  - 自动检测Vg文件（以'V.txt'或'V.csv'结尾的文件）
- **时间设置**：信号截断选项，采样率处理
- **内存管理**：所有点与采样处理模式
- **输出控制**：灵活的文件命名和目录结构

### 视频生成
- **质量设置**：可配置DPI（150）、比特率、帧率（30帧/秒）
- **格式选项**：MP4（FFmpeg）、GIF（Pillow）、HTML备用
- **视觉增强**：时间戳、颜色条、自定义标题
- **视图控制**：固定或旋转3D视图、仰角/方位角设置

## 高级使用示例

### Vg信号延迟配置

```python
from python_dataprepare_visualize.utils.dataprocess.start_idx_visualized_select import StartIdxVisualizedSelect

# 大多数测量系统的默认2.5毫秒延迟
processor = StartIdxVisualizedSelect(
    input_folder="./input/data",
    output_folder="./output/processed",
    vg_delay=0.0025  # 2.5ms默认值
)

# 特定硬件设置的自定义延迟
processor = StartIdxVisualizedSelect(
    input_folder="./input/data", 
    output_folder="./output/processed",
    vg_delay=0.003  # 3ms用于响应较慢的系统
)

# 预对齐数据无延迟
processor = StartIdxVisualizedSelect(
    input_folder="./input/data",
    output_folder="./output/processed", 
    vg_delay=0.0  # 无延迟补偿
)

processor.run()
```

### 交互式起始点选择工作流程

1. **初始概览**：查看Vg和原始数据的完整信号轨迹
2. **缩放到区域**：使用鼠标滚轮放大到感兴趣的时间区域
3. **精细调整位置**：Shift+拖拽平移并居中关键转换点
4. **精确选择**：点击选择具有像素级精度的起始点
5. **验证选择**：按'r'重置视图并确认选择看起来正确
6. **保存并继续**：按'n'保存截断的数据并移至下一个文件

### 鼠标和键盘控制

| 控制方式 | 操作 |
|---------|------|
| 左键点击 | 选择起始点 |
| 鼠标滚轮 | 以光标为中心缩放 |
| Shift + 拖拽 | 平移视图（X轴同步，Y轴独立） |
| 中键 + 拖拽 | 替代平移方法 |
| 'r' 键 | 重置为原始视图 |
| 'n' 键 | 保存选择并处理下一个文件 |
| 'k' 键 | 跳过当前文件 |

## 系统要求

### 核心依赖
- Python 3.7+
- NumPy、pandas、matplotlib、scipy
- PyWavelets（小波分析）
- loguru（日志记录）、tqdm（进度条）
- tkinter（GUI组件）

### 可选依赖
- **FFmpeg**：高质量MP4视频输出（推荐）
- **MATLAB**：增强可视化（可选）

### 平台支持
- **跨平台**：Windows、macOS、Linux
- **字体处理**：每平台的自动中文字体选择
- **路径兼容性**：使用pathlib实现跨平台路径

## 性能优化

### 内存管理
- **分块处理**：处理大数据集而不会内存溢出
- **采样选项**：5点采样与所有点处理模式
- **高效数据结构**：NumPy数组优化性能

### 处理速度
- **并行操作**：高效的数据加载和处理
- **进度跟踪**：实时进度条和日志记录
- **错误恢复**：对数据格式变化的鲁棒处理

## 故障排除

### 常见问题
- **FFmpeg安装**：安装以获取高质量视频（参见INSTALLATION_CN.md）
- **内存错误**：使用采样模式或减少网格大小
- **字体渲染**：安装平台特定的中文字体
- **文件格式**：确保一致的文件命名约定

### 性能提示
- **网格大小**：从较小的网格（4×6）开始测试
- **采样**：使用5点采样进行快速迭代
- **视频质量**：根据要求调整DPI/比特率
- **批处理**：高效处理多个实验

有关详细安装说明，请参见[INSTALLATION_CN.md](INSTALLATION_CN.md)。

有关开发指导，请参见[CLAUDE.md](CLAUDE.md)。