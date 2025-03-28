# 安装指南

本指南提供安装运行多序列时间数据可视化工具所需的所有依赖项的说明。

## Python 要求

本项目需要 Python 3.7 或更新版本。我们建议使用虚拟环境进行安装。

### 创建虚拟环境（可选但推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows 系统:
venv\Scripts\activate
# macOS/Linux 系统:
source venv/bin/activate
```

### 基本依赖项

安装所需的Python包：

```bash
pip install numpy pandas matplotlib scipy tqdm loguru
```

## FFmpeg 安装

FFmpeg是生成高质量MP4动画所必需的。如果未安装FFmpeg，系统将退而求其次使用替代格式（GIF或HTML）。

### Windows系统

1. 从[FFmpeg官方网站](https://ffmpeg.org/download.html)或[gyan.dev](https://www.gyan.dev/ffmpeg/builds/)下载FFmpeg
2. 下载"ffmpeg-release-full"版本并解压到您想要的位置（例如，`C:\FFmpeg`）
3. 将FFmpeg的bin目录添加到系统PATH环境变量：
   - 右键点击"此电脑" → "属性" → "高级系统设置" → "环境变量"
   - 在"系统变量"中找到"Path"，点击"编辑"
   - 添加FFmpeg的bin目录路径，例如`C:\FFmpeg\bin`
   - 点击"确定"保存更改
4. 重启命令提示符或PowerShell以使PATH更改生效
5. 通过运行以下命令验证安装：
   ```
   ffmpeg -version
   ```

### macOS系统

使用Homebrew安装FFmpeg：

```bash
# 如果尚未安装Homebrew，先安装Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装FFmpeg
brew install ffmpeg
```

### Ubuntu/Debian Linux系统

```bash
sudo apt update
sudo apt install ffmpeg
```

### Fedora Linux系统

```bash
sudo dnf install ffmpeg
```

### CentOS/RHEL Linux系统

```bash
sudo yum install epel-release
sudo yum install ffmpeg
```

## 验证安装

您可以通过运行以下Python代码来验证matplotlib是否正确配置以使用FFmpeg：

```python
import matplotlib.animation as animation
print("可用的动画写入器:", animation.writers.list())
```

如果输出中出现'ffmpeg'，则配置正确。

## 非拉丁字符的字体支持（可选）

如果您需要在可视化中显示非拉丁字符（如中文）：

### Windows系统
默认支持以下字体：
- SimHei（黑体）
- Microsoft YaHei（微软雅黑）
- SimSun（宋体）

### macOS系统
默认支持以下字体：
- PingFang SC（苹方）
- Heiti SC（黑体-简）
- STHeiti（华文黑体）

### Linux系统
您可能需要安装：

Ubuntu/Debian：
```bash
sudo apt install fonts-wqy-microhei fonts-wqy-zenhei
```

Fedora：
```bash
sudo dnf install wqy-microhei-fonts wqy-zenhei-fonts
```

## 故障排除

如果您遇到与视频生成相关的错误：

1. 确认FFmpeg已正确安装并添加到PATH
2. 使用上面的验证脚本检查matplotlib是否能找到FFmpeg
3. 尝试通过修改文件扩展名强制使用不同的输出格式：
   - `.gif`用于GIF格式（使用Pillow）
   - `.html`用于HTML动画

如果您看到与matplotlib相关的错误，请尝试安装特定版本：

```bash
pip install matplotlib==3.5.3
```

## 高级配置

对于想要指定自定义FFmpeg编码参数的高级用户，可以在运行可视化时使用命令行参数：

```python
viz_gen = VisualizationGenerator(
    processed_data=processed_data,
    fps=30,               # 控制帧率
    dpi=150,              # 控制分辨率
    colormap="viridis",   # 设置颜色方案
    output_folder="./output/videos"
)

# 生成高质量视频
viz_gen.generate_heatmap_video(
    output_file="heatmap.mp4",
    title="信号强度",
    bitrate="8000k"       # 控制视频质量
)
``` 