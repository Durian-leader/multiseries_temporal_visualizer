# 多序列时间数据可视化工具

这是一个全面的Python工具包，用于处理、分析和可视化多序列时间数据。该工具专注于将振动数据或其他时间序列数据集转换为高质量的可视化效果和动画。

效果演示：
- https://youtu.be/eMQt-ECYRZA
- https://youtu.be/zs1seIiErXs
- https://youtu.be/VFoZmemtraI

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
├── python_数据预处理与可视化/    # 主要处理脚本
│   ├── 00select_start_idx.py   # 交互式起始点选择
│   ├── 01sample.py             # 生成 5 点采样数据
│   ├── 01csv2npz.py            # 将 CSV 转换为 NPZ（所有点）
│   ├── 02picture.py            # 生成静态可视化
│   ├── 03video.py              # 生成视频动画
│   ├── 04查看某个信号小波去噪前后的对比.py  # 小波去噪对比
│   ├── baseline_correction.py  # 交互式基线校正
│   ├── npz_to_mat.py          # 将 NPZ 转换为 MATLAB 格式
│   ├── utils/                  # 工具模块
│   │   ├── dataprocess/        # 数据处理工具
│   │   │   ├── vibration_data_loader.py     # 原始数据加载
│   │   │   ├── start_idx_visualized_select.py  # 起始点选择
│   │   │   ├── debiasing.py    # 基线校正
│   │   │   └── wavelet_denoise.py  # 小波去噪
│   │   └── visualize/          # 可视化工具
│   │       ├── data_processor.py    # 数据网格处理
│   │       └── visualization_generator.py  # 视频/图像生成
│   └── main.ipynb              # Jupyter 笔记本交互使用
├── matlab_数据可视化_比python精美/  # MATLAB 可视化脚本
│   ├── main01_3d.m             # 3D 曲面可视化
│   ├── main02_heatmap.m        # 热图可视化
│   └── main03_heatmapwithprofile.m  # 带剪面的热图
├── CLAUDE.md                  # 开发指南
├── INSTALLATION_CN.md         # 安装说明
└── README_CN.md               # 本文件
```

## 数据处理工作流程

### 快速开始流程

**步骤1：选择数据对齐的起始索引**
```bash
python python_数据预处理与可视化/00select_start_idx.py
```
- 交互式 GUI 为每个数据文件选择起始点
- 输出：对齐起始点的 CSV 文件

**步骤2：选择您的处理路径**

**路径 A - 视频生成（5点采样）：**
```bash
python python_数据预处理与可视化/01sample.py
python python_数据预处理与可视化/03video.py
```

**路径 B - 详细分析（所有点）：**
```bash
python python_数据预处理与可视化/01csv2npz.py
python python_数据预处理与可视化/02picture.py
```

**步骤3（可选）：转换为 MATLAB 格式**
```bash
python python_数据预处理与可视化/npz_to_mat.py
```

### 可选处理步骤

**基线校正：**
```bash
python python_数据预处理与可视化/baseline_correction.py
```
- 交互式 GUI 进行基线漂移校正
- 可在流程的任意阶段应用

**小波去噪：**
```bash
python python_数据预处理与可视化/04查看某个信号小波去噪前后的对比.py
```
- 比较小波去噪前后的信号
- 可配置的小波参数

### 高级用法

**使用 Jupyter 笔记本：**
打开 `python_数据预处理与可视化/main.ipynb` 进行交互式数据探索和处理。

**MATLAB 集成：**
1. 运行 `python_数据预处理与可视化/npz_to_mat.py` 转换处理后的数据
2. 使用 `matlab_数据可视化_比python精美/` 中的 MATLAB 脚本：
   - `main01_3d.m` - 3D 曲面图
   - `main02_heatmap.m` - 热图可视化
   - `main03_heatmapwithprofile.m` - 带剪面的热图

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
- pathlib
- FFmpeg（用于视频生成）
- MATLAB（可选，用于增强可视化）

## 输出格式和可视化

### 视频输出（来自 03video.py）
- **热图动画**：随时间演变的 2D 色彩图 (.mp4)
- **3D 曲面视频**：旋转的 3D 曲面图 (.mp4)
- **组合可视化**：带横截面剪面的热图 (.mp4)

### 静态输出（来自 02picture.py）
- **时间点可视化**：特定时间点的热图 (.png)
- **数据导出**：选定时间点的 CSV 文件
- **网格可视化**：测量点的空间布置

### MATLAB 输出
- **高质量 3D 曲面**：专业级 3D 可视化
- **增强型热图**：可用于发表的热图可视化
- **剪面分析**：带详细剪面的横截面分析

## 颜色映射选项

该工具包支持多种可视化的颜色映射选项：

- **连续数据**：viridis, plasma, inferno, magma, cividis, turbo
- **经典渐变**：jet, rainbow, ocean, terrain
- **高对比度**：hot, cool, copper
- **科学数据**：RdBu, coolwarm, seismic, spectral
- **单色渐变**：Blues, Reds, Greens, YlOrRd, BuPu
- **色盲友好**：cividis, viridis

详细安装说明，请参见[INSTALLATION_CN.md](INSTALLATION_CN.md)。 