# 安装指南

这个指南提供了运行多序列时间数据可视化工具所需的所有依赖项的分步安装说明。

## 系统要求

- **Python版本**：3.7或更高版本
- **操作系统**：Windows、macOS或Linux
- **内存**：推荐4GB+内存用于大型数据集
- **存储空间**：1GB+可用空间用于处理输出

## 快速安装

### 方法1：使用pip安装（推荐）

```bash
# 克隆或下载代码库
cd multiseries_temporal_visualizer

# 安装核心依赖项
pip install -r requirements.txt

# 验证安装
python -c "import numpy, pandas, matplotlib, scipy, pywt, loguru, tqdm; print('✓ 所有包已成功安装')"
```

### 方法2：手动安装

```bash
# 核心科学计算库
pip install numpy pandas scipy

# 可视化库
pip install matplotlib

# 小波分析
pip install PyWavelets

# 日志记录和进度条
pip install loguru tqdm

# 可选：增强绘图功能（如需要）
pip install plotly>=5.0.0
```

## 虚拟环境设置（推荐）

使用虚拟环境有助于避免包冲突：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows系统：
venv\Scripts\activate
# macOS/Linux系统：
source venv/bin/activate

# 安装依赖项
pip install -r requirements.txt

# 完成后停用（可选）
deactivate
```

## FFmpeg安装（视频生成必备）

**强烈推荐**安装FFmpeg以生成高质量MP4视频。如果没有FFmpeg，系统将退而求其次使用较低质量的GIF或HTML格式。

### Windows系统

**方法1：使用winget（Windows 10/11）**
```bash
winget install ffmpeg
```

**方法2：手动安装**
1. 从[FFmpeg官方网站](https://ffmpeg.org/download.html#build-windows)或[gyan.dev](https://www.gyan.dev/ffmpeg/builds/)下载FFmpeg
2. 下载"release"构建版本（不是static）并解压到`C:\ffmpeg`
3. 将FFmpeg添加到PATH环境变量：
   - 按`Win + X`并选择"系统"
   - 点击"高级系统设置" → "环境变量"
   - 在"系统变量"中找到"Path"，点击"编辑"
   - 点击"新建"并添加：`C:\ffmpeg\bin`
   - 点击"确定"保存所有更改
4. **重启命令提示符/PowerShell**
5. 验证安装：`ffmpeg -version`

### macOS系统

**方法1：使用Homebrew（推荐）**
```bash
# 如果尚未安装Homebrew，先安装
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装FFmpeg
brew install ffmpeg
```

**方法2：使用MacPorts**
```bash
sudo port install ffmpeg
```

### Linux系统

**Ubuntu/Debian：**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Fedora：**
```bash
sudo dnf install ffmpeg
```

**CentOS/RHEL：**
```bash
# 首先启用EPEL仓库
sudo yum install epel-release
sudo yum install ffmpeg
```

**Arch Linux：**
```bash
sudo pacman -S ffmpeg
```

## Jupyter笔记本设置

为了获得集成流水线体验：

```bash
# 安装Jupyter
pip install jupyter notebook

# 可选：安装JupyterLab以获得增强界面
pip install jupyterlab

# 启动Jupyter Notebook
jupyter notebook

# 或启动JupyterLab
jupyter lab
```

## GUI依赖项

工具包包含用于基线校正和起始点选择的交互式GUI工具。

### tkinter（通常预装）

大多数Python安装默认包含tkinter。如果没有：

**Ubuntu/Debian：**
```bash
sudo apt install python3-tk
```

**Fedora：**
```bash
sudo dnf install tkinter
```

**macOS/Windows：**通常与Python一起预装

## 非英文字符字体支持

为了在可视化中正确渲染中文字符：

### Windows系统
支持的默认字体：
- SimHei（黑体）
- Microsoft YaHei（微软雅黑）
- SimSun（宋体）

**如果字符显示不正确：**
1. 转到设置 → 时间和语言 → 语言
2. 添加中文（简体）或中文（繁体）
3. 提示时安装语言包

### macOS系统
支持的默认字体：
- PingFang SC（苹方-简）
- Heiti SC（黑体-简）
- STHeiti（华文黑体）

**如需要：**
```bash
# 通过Homebrew安装额外的中文字体
brew install --cask font-source-han-sans
```

### Linux系统

**Ubuntu/Debian：**
```bash
sudo apt install fonts-wqy-microhei fonts-wqy-zenhei
sudo apt install fonts-noto-cjk  # 可选的综合字体包
```

**Fedora：**
```bash
sudo dnf install wqy-microhei-fonts wqy-zenhei-fonts
sudo dnf install google-noto-sans-cjk-fonts  # 可选
```

**Arch Linux：**
```bash
sudo pacman -S wqy-microhei wqy-zenhei
```

## MATLAB集成（可选）

为了获得增强的3D可视化和出版质量图表：

1. **安装MATLAB** R2018b或更新版本
2. **确保MATLAB在系统PATH中**
3. **验证安装：**
   ```bash
   matlab -batch "disp('MATLAB正常工作')"
   ```
4. **测试MAT文件兼容性：**
   ```matlab
   % 在MATLAB命令窗口中
   data = load('my_processed_data.mat');
   disp(fieldnames(data));
   ```

## 验证和测试

### 基本验证

```bash
# 测试核心Python包
python -c "
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy
import pywt
import loguru
import tqdm
print('✓ 所有核心包正常工作')
"
```

### FFmpeg验证

```bash
# 检查FFmpeg安装
ffmpeg -version

# 测试matplotlib FFmpeg集成
python -c "
import matplotlib.animation as animation
writers = animation.writers.list()
print('可用的写入器:', writers)
if 'ffmpeg' in writers:
    print('✓ FFmpeg集成正常工作')
else:
    print('⚠ FFmpeg不可用 - 视频将使用备用格式')
"
```

### 字体验证

```python
# 测试中文字体支持
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 列出可用字体
fonts = [f.name for f in fm.fontManager.ttflist if 'SimHei' in f.name or 'PingFang' in f.name or 'WenQuanYi' in f.name]
print("可用的中文字体:", fonts)

# 用中文字符测试绘图
plt.figure(figsize=(6, 4))
plt.plot([1, 2, 3], [1, 4, 2])
plt.title('测试中文显示')
plt.xlabel('时间')
plt.ylabel('信号')
plt.savefig('font_test.png', dpi=150, bbox_inches='tight')
print("✓ 字体测试已保存为'font_test.png'")
```

### GUI测试

```python
# 测试tkinter可用性
try:
    import tkinter as tk
    root = tk.Tk()
    root.title("GUI测试")
    tk.Label(root, text="✓ GUI正常工作").pack()
    print("✓ GUI测试窗口应该出现")
    # 取消注释下一行以显示窗口
    # root.mainloop()
    root.destroy()
except ImportError:
    print("⚠ tkinter不可用 - GUI功能将不工作")
```

## 快速开始测试

通过运行最小工作流程测试完整安装：

```bash
# 导航到项目目录
cd multiseries_temporal_visualizer

# 测试数据加载（假设您有示例数据）
python -c "
from python_dataprepare_visualize.utils.dataprocess.vibration_data_loader import VibrationDataLoader
print('✓ 数据加载器正常工作')
"

# 测试Jupyter笔记本（将在浏览器中打开）
jupyter notebook main.ipynb
```

## 故障排除

### 常见问题和解决方案

**"没有名为'X'的模块"错误：**
```bash
# 确保您在正确的环境中
pip list | grep package_name

# 重新安装缺失的包
pip install --upgrade package_name
```

**找不到FFmpeg：**
```bash
# Windows：PATH更改后重启命令提示符
# macOS/Linux：检查PATH
echo $PATH | grep ffmpeg

# 验证FFmpeg位置
which ffmpeg  # macOS/Linux
where ffmpeg  # Windows
```

**处理过程中的内存错误：**
- 减少网格大小（例如，使用4×6而不是6×6）
- 在处理脚本中启用采样模式
- 关闭其他应用程序以释放内存

**GUI不显示：**
- 确保SSH连接启用了X11转发
- 在WSL上，安装X服务器如VcXsrv
- 检查tkinter安装

**视频生成缓慢：**
- 降低DPI设置（例如，100而不是150）
- 降低帧率（例如，24fps而不是30fps）
- 使用更短的视频片段进行测试

**中文字符不显示：**
- 为您的平台安装适当的字体
- 清除matplotlib字体缓存：`rm ~/.matplotlib/fontlist-v*.json`
- 安装字体后重启Python

### 性能优化提示

1. **使用SSD存储**以获得更快的I/O操作
2. **增加内存**用于更大的数据集（推荐8GB+）
3. **启用GPU加速**（如果使用MATLAB可视化）
4. **使用采样模式**进行初始测试和开发

### 平台特定说明

**Windows子系统Linux (WSL)：**
- 安装Windows版FFmpeg以获得更好的集成
- 使用VcXsrv运行GUI应用程序
- 挂载Windows驱动器以访问数据

**macOS Apple Silicon (M1/M2)：**
- 使用conda或mamba以获得更好的ARM64支持
- 某些包可能需要Rosetta 2

**Linux服务器/无头模式：**
- 使用`matplotlib.use('Agg')`后端
- 安装虚拟帧缓冲区：`sudo apt install xvfb`
- 使用以下方式运行GUI工具：`xvfb-run python script.py`

## 高级配置

### 环境变量

在项目根目录创建`.env`文件：

```bash
# 可选的环境变量
MATPLOTLIB_BACKEND=TkAgg
NUMEXPR_MAX_THREADS=4
OMP_NUM_THREADS=4
```

### 自定义配置

在您的脚本中修改默认设置：

```python
# 在您的处理脚本中
import matplotlib
matplotlib.rcParams['font.size'] = 12
matplotlib.rcParams['figure.dpi'] = 150
matplotlib.rcParams['savefig.dpi'] = 300
```

## 获取帮助

如果您遇到问题：

1. **检查本指南中的故障排除部分**
2. **仔细查看错误消息** - 它们通常包含解决方案
3. **使用上述验证脚本测试各个组件**
4. **检查系统资源**（内存、磁盘空间、CPU使用率）

## 下一步

安装完成后：

1. **阅读**[README_CN.md](README_CN.md)了解使用说明
2. **试用**集成Jupyter笔记本：`jupyter notebook main.ipynb`
3. **使用快速开始命令处理示例数据**
4. **探索**高级功能和MATLAB集成

您的安装现已完成，可以开始进行科学数据可视化了！