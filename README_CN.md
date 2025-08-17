# 多系列时序数据可视化系统

- [English](README.md)

一个全面的Python和MATLAB工具包，用于处理、分析和可视化科学实验中的多系列时序数据，特别专注于OECT（有机电化学晶体管）溶胀测量及类似的材料科学应用。

## 演示视频
- https://youtu.be/eMQt-ECYRZA
- https://youtu.be/zs1seIiErXs  
- https://youtu.be/VFoZmemtraI

## 核心特性

### 🎯 集成化流水线界面
- **统一Jupyter笔记本**: 通过`main.ipynb`提供完整的交互式处理流水线
- **程序化API**: 通过`steps.py`提供清晰的函数接口以实现自动化
- **实时进度跟踪**: 全面的日志记录和错误处理
- **灵活处理**: 支持完整流水线和单步操作

### 🔄 完整数据处理流水线
- **原始数据加载**: 将TXT文件转换为CSV格式并解析元数据
- **交互式起始点选择**: 可视化GUI界面，支持Vg信号的时间对齐
- **去偏处理**: 自动基线偏移校正和数据截断
- **网格数据组织**: 将单独的时间序列转换为空间网格格式
- **格式转换**: NPZ转MATLAB MAT格式，实现跨平台兼容性

### 📊 高级可视化功能
- **高质量视频生成**: 热图、3D表面图和截面轮廓图
- **静态可视化**: 时间点快照和数据导出
- **MATLAB集成**: 使用MATLAB脚本实现专业级可视化
- **多种配色方案**: 20+种科学配色方案，包括viridis、plasma、turbo

### 🛠 用户友好界面
- **集成化工作流**: 主笔记本自动处理完整流水线
- **交互式GUI工具**: 起始点选择和基线校正
- **命令行界面**: 为高级用户提供单独脚本访问
- **实时验证**: 处理过程中的数据预览和错误恢复

## 快速开始

### 方法1：集成化Jupyter笔记本（推荐）
```bash
jupyter notebook main.ipynb
```
该笔记本提供完整的交互式流水线，包括：
- 自动错误处理的顺序步骤执行
- 详细日志记录的实时进度跟踪
- 直接在笔记本单元格中配置参数
- 自动输出目录管理
- 内置结果验证和总结报告

### 方法2：程序化API
```python
from python_dataprepare_visualize.steps import *

# 步骤1：TXT转CSV格式转换
result1 = convert_txt_to_csv('data/origin', 'data/csv')

# 步骤2：交互式起始点选择
result2 = select_start_indices('data/csv', 'data/csv_起始点选择', vg_delay=0.0025)

# 步骤3：去偏处理和截断
result3 = apply_debiasing('data/csv_起始点选择', 'data/csv_起始点选择_去偏')

# 步骤4：转换为NPZ格式
result4 = convert_csv_to_npz_file('data/csv_起始点选择_去偏', 'data/data.npz', rows=4, cols=6)

# 步骤5：生成MATLAB文件
result5 = convert_npz_to_mat_file('data/data.npz', 'data/data.mat')
```

### 方法3：独立脚本
```bash
# 高级用户仍可以访问独立组件
python python_dataprepare_visualize/csv2npz.py \
  --input-folder ./data/processed \
  --output-file ./data/output.npz \
  --rows 4 --cols 6

python python_dataprepare_visualize/npz_to_mat.py \
  --input-file ./data/output.npz \
  --output-file ./data/output.mat
```

## 项目架构

```
multiseries_temporal_visualizer/
├── main.ipynb                          # 🎯 主集成流水线
├── python_dataprepare_visualize/       # 核心处理包
│   ├── steps.py                        # 🔧 所有处理步骤的统一API
│   ├── csv2npz.py                      # CSV到NPZ转换
│   ├── npz_to_mat.py                   # NPZ到MATLAB转换
│   ├── 00_5_manual_baseline_correction.py  # 基线校正脚本
│   ├── batch_baseline_correction.py    # 批量基线处理
│   └── utils/                          # 核心工具
│       ├── dataprocess/                # 数据处理组件
│       │   ├── vibration_data_loader.py      # 带元数据的TXT/CSV加载器
│       │   ├── start_idx_visualized_select.py # 对齐的交互式GUI
│       │   ├── baseline_correction.py         # GUI基线校正
│       │   ├── debiasing.py                   # 数据偏移校正
│       │   └── wavelet_denoise.py             # 小波滤波
│       └── visualize/                  # 可视化组件
│           ├── data_processor.py              # 网格数据组织
│           ├── visualization_generator.py     # 视频/图像生成
│           ├── extract_timepoint.py           # 时间点提取
│           └── example.py                     # 使用示例
├── matlab_数据可视化_比python精美/      # MATLAB可视化套件
│   ├── main01_3d.m                     # 3D表面动画
│   └── main03_heatmapwithprofile.m     # 带轮廓的热图
├── data/                               # 组织化数据结构
│   ├── origin/                         # 原始TXT文件
│   ├── csv/                           # 转换后的CSV文件
│   ├── csv_起始点选择/                 # 起始点对齐数据
│   ├── csv_起始点选择_去偏/            # 去偏和截断数据
│   ├── data.npz                       # 网格组织数据
│   └── data.mat                       # MATLAB兼容输出
├── datasets/                          # 实验数据集存档
├── logs/                              # 处理日志
└── requirements.txt                   # Python依赖项
```

## 数据处理工作流

### 核心流水线（集成化）
主笔记本（`main.ipynb`）执行以下完整工作流：

1. **TXT → CSV转换**（`convert_txt_to_csv`）
   - 解析原始测量文件并提取元数据
   - 处理各种文件格式和编码

2. **起始点选择**（`select_start_indices`）
   - 双信号显示的交互式GUI（Vg + 测量信号）
   - 可配置的Vg延迟补偿（默认：2.5ms）
   - 高级缩放/平移控制以实现精确对齐

3. **去偏处理**（`apply_debiasing`）
   - 偏移校正至零基线
   - 可选截断至最小公共长度
   - 优雅处理缺失数据

4. **网格组织**（`convert_csv_to_npz_file`）
   - 时间序列的空间排列（例如4×6网格）
   - 时间同步和插值
   - 带进度跟踪的内存高效处理

5. **MATLAB导出**（`convert_npz_to_mat_file`）
   - 完整元数据保留
   - MATLAB可视化的兼容数据结构

### 关键处理特性
- **统一错误处理**: 每个步骤返回标准化的成功/错误信息
- **进度跟踪**: 集成loguru的实时日志记录
- **内存管理**: 大型数据集的高效处理
- **配置灵活性**: 所有参数易于调整

## 高级功能

### 交互式起始点选择
GUI界面提供：

- **双信号显示**: Vg电压和测量信号的同步可视化
- **硬件延迟补偿**：
  - 典型OECT测量的默认2.5ms Vg延迟
  - 不同系统的0-10ms可配置范围
  - 在文件加载期间透明应用
- **高级导航**：
  - 以光标位置为中心的鼠标滚轮缩放
  - 信号图之间的同步X轴缩放
  - 每个子图的独立Y轴缩放
  - Shift+拖拽或中键点击实现平滑平移
- **键盘快捷键**：
  - 'n' 保存并进入下一个文件
  - 'k' 跳过当前文件
  - 'r' 重置缩放至原始视图

### 去偏和数据准备
- **基线校正**: 使用第一个数据点作为参考的自动偏移去除
- **长度标准化**: 可选截断以确保一致的时间序列长度
- **质量验证**: 自动检测损坏或不完整的数据文件

### MATLAB集成
处理完成后，使用MATLAB脚本进行出版级质量的可视化：

```matlab
% 加载处理后的数据
data = load('data/data.mat');

% 生成专业可视化
main01_3d                    % 带旋转的3D表面动画
main03_heatmapwithprofile   % 带截面轮廓的热图
```

MATLAB脚本提供：
- 高分辨率3D表面动画
- 集成截面轮廓的热图
- 专业配色方案和布局优化
- 可自定义参数的视频导出功能

## 配置选项

### 处理参数
所有参数都可以在主笔记本或通过API配置：

```python
# Vg信号对齐
vg_delay = 0.0025  # OECT测量的默认2.5ms

# 网格配置
rows = 4           # 空间网格行数
cols = 6           # 空间网格列数

# 数据处理
truncate_to_min = True  # 标准化时间序列长度
use_all_points = True   # 使用全分辨率 vs. 采样
```

### Vg信号延迟示例
```python
# 标准OECT测量系统
vg_delay = 0.0025  # 2.5ms

# 预同步数据
vg_delay = 0.0     # 无延迟补偿
```

### 网格配置选项
- **标准布局**: 4×6（24个测量点）
- **高密度**: 6×6（36个测量点）
- **自定义排列**: 任何行×列组合
- **缺失点处理**: 不完整网格的优雅处理

## 系统要求

### 核心依赖项
- Python 3.7+
- NumPy, pandas, matplotlib, scipy
- loguru（日志记录）, tqdm（进度条）
- tkinter（GUI组件）

### 可选依赖项
- **FFmpeg**: 高质量MP4视频输出（推荐）
- **MATLAB**: 增强可视化（可选）

### 安装
```bash
# 克隆仓库
git clone <repository-url>
cd multiseries_temporal_visualizer

# 安装Python依赖项
pip install -r requirements.txt
```

## 使用示例

### 基本流水线执行
```python
# 使用默认设置运行完整流水线
results = {}

# 使用错误处理执行每个步骤
from python_dataprepare_visualize.steps import *

results["txt_to_csv"] = convert_txt_to_csv('data/origin', 'data/csv')
results["start_idx_selection"] = select_start_indices('data/csv', 'data/csv_起始点选择', vg_delay=0.0025)
results["debiasing"] = apply_debiasing('data/csv_起始点选择', 'data/csv_起始点选择_去偏')
results["csv_to_npz"] = convert_csv_to_npz_file('data/csv_起始点选择_去偏', 'data/data.npz', rows=4, cols=6)
results["npz_to_mat"] = convert_npz_to_mat_file('data/data.npz', 'data/data.mat')

# 检查结果
for step_name, result in results.items():
    status = "✓" if result.get("success", False) else "✗"
    print(f"{status} {step_name}: {result.get('message', 'Unknown')}")
```

### 高级基线校正
```python
# 自动基线校正
from python_dataprepare_visualize.steps import apply_baseline_correction

result = apply_baseline_correction(
    input_dir='data/processed',
    output_dir='data/baseline_corrected',
    mode="auto"  # 或"manual"用于GUI界面
)
```

## 性能优化

### 内存管理
- **分块处理**: 大型数据集按可管理的块进行处理
- **进度监控**: 实时内存使用跟踪
- **高效数据结构**: 使用NumPy数组实现最佳性能

### 处理速度
- **优化算法**: 高效的信号处理和数据组织
- **并行就绪**: 为批处理的轻松并行化而设计
- **智能缓存**: 缓存中间结果以避免重复计算

## 故障排除

### 常见问题
- **内存错误**: 减少网格大小或启用采样模式
- **GUI显示问题**: 确保远程会话的正确X11转发
- **文件格式错误**: 验证一致的文件命名（11.txt, 11V.txt模式）
- **MATLAB集成**: 确保导出的MAT文件中的兼容数据结构

### 性能提示
- **从笔记本开始**: 使用`main.ipynb`进行初步探索
- **批量处理**: 使用程序化API处理多个数据集
- **内存监控**: 在大型数据集处理期间监控内存使用
- **质量vs速度**: 根据需求调整采样参数

有关开发指南和技术细节，请参见[CLAUDE.md](CLAUDE.md)。

## 引用

如果您在研究中使用此软件，请引用：

```bibtex
@software{multiseries_temporal_visualizer,
  title={多系列时序数据可视化系统：OECT溶胀信号处理与可视化系统},
  author={[您的姓名]},
  year={2025},
  url={https://github.com/your-username/multiseries_temporal_visualizer}
}
```