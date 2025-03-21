# 安装指南

为了正确运行时间序列数据可视化系统，您需要安装以下依赖项。

## 基本依赖项

```bash
pip install numpy pandas matplotlib scipy tqdm
```

## 视频生成依赖项

要生成动画视频文件(MP4格式)，您需要安装FFmpeg。

### Windows

1. 访问 [FFmpeg官方网站](https://ffmpeg.org/download.html) 或 [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) 下载FFmpeg
2. 下载"ffmpeg-release-full"版本并解压缩到所需位置（如 `C:\FFmpeg`）
3. 将FFmpeg的bin目录添加到系统PATH环境变量:
   - 右键点击"此电脑"→"属性"→"高级系统设置"→"环境变量"
   - 在"系统变量"中找到"Path"，点击"编辑"
   - 添加FFmpeg的bin目录路径，如 `C:\FFmpeg\bin`
   - 点击"确定"保存更改
4. 重启命令提示符或PowerShell以使PATH更改生效
5. 验证安装，在命令提示符中运行:
   ```
   ffmpeg -version
   ```

### macOS

使用Homebrew安装:

```bash
brew install ffmpeg
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install ffmpeg
```

### Linux (Fedora)

```bash
sudo dnf install ffmpeg
```

### Linux (CentOS/RHEL)

```bash
sudo yum install epel-release
sudo yum install ffmpeg
```

## 验证matplotlib与FFmpeg集成

在Python中运行以下代码以检查FFmpeg是否已正确集成:

```python
import matplotlib.animation as animation
print("Available animation writers:", animation.writers.list())
```

如果输出中包含'ffmpeg'，则表示FFmpeg已正确配置。

## 替代方案

如果您无法安装FFmpeg，系统会尝试使用替代方法保存动画:

1. **GIF格式**: 使用Pillow保存为GIF格式（质量较低但兼容性好）
2. **HTML格式**: 保存为可在浏览器中查看的HTML文件

## 中文字体支持（可选）

如果您需要在可视化中使用中文，请确保安装了适当的中文字体:

### Windows
默认支持以下字体:
- SimHei (黑体)
- Microsoft YaHei (微软雅黑)
- SimSun (宋体)

### macOS
默认支持以下字体:
- PingFang SC
- Heiti SC
- STHeiti

### Linux
您可能需要安装:
- WenQuanYi Micro Hei
- WenQuanYi Zen Hei

Ubuntu/Debian安装:
```bash
sudo apt install fonts-wqy-microhei fonts-wqy-zenhei
```

## 疑难解答

如果您在运行时遇到与视频生成相关的错误，请尝试以下解决方案:

1. 确认FFmpeg已正确安装并添加到PATH
2. 检查matplotlib与FFmpeg的集成
3. 尝试使用GIF格式作为替代输出格式
4. 如果问题仍存在，请检查日志输出，并考虑安装指定版本的matplotlib:
   ```bash
   pip install matplotlib==3.5.3
   ```

## 高级用户

如果您希望指定特定的FFmpeg编码器和参数，可以在命令行中使用以下选项:

```bash
python main.py --input ./data_csv --rows 6 --cols 6 --output ./output/videos --fps 30 --quality high
```