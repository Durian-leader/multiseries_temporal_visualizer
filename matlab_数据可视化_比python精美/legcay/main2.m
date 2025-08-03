
%% 数据可视化流程 - 使用科研可视化套件
% 本脚本演示如何使用高级可视化函数处理和可视化科研数据

%% 0. 设置中文字体支持
% 检测操作系统，设置适当的中文字体
if ispc % Windows系统
    set(0, 'DefaultAxesFontName', 'SimHei');
    set(0, 'DefaultTextFontName', 'SimHei');
    chinese_font = 'SimHei'; % 黑体
elseif ismac % macOS系统
    set(0, 'DefaultAxesFontName', 'STHeiti');
    set(0, 'DefaultTextFontName', 'STHeiti');
    chinese_font = 'STHeiti'; % 黑体-简
else % Linux系统
    set(0, 'DefaultAxesFontName', 'WenQuanYi Micro Hei');
    set(0, 'DefaultTextFontName', 'WenQuanYi Micro Hei');
    chinese_font = 'WenQuanYi Micro Hei';
end

% 修复负号显示问题
set(0, 'DefaultAxesTickDir', 'out');
set(0, 'DefaultAxesXMinorTick', 'on');
set(0, 'DefaultAxesYMinorTick', 'on');

%% 1. 加载和处理数据
% 加载数据
data = load('my_processed_data.mat');
% 获取原始grid_data和时间点
original_grid_data = data.grid_data;
original_time_points = data.time_points;

% 获取原始形状
[num_frames, num_rows, num_cols] = size(original_grid_data);
fprintf('原始数据: %d 帧, %d 行, %d 列\n', num_frames, num_rows, num_cols);

%% 2. 数据降采样（如有必要）
% 设置目标帧数
target_frames = 500; % 设置你想要的帧数

% 如果原始帧数大于目标帧数，则进行降采样
if num_frames > target_frames
    % 降采样方法: 简单的等距离抽样
    downsample_indices = round(linspace(1, num_frames, target_frames));
    grid_data = original_grid_data(downsample_indices, :, :);
    time_points = original_time_points(downsample_indices);
    fprintf('降采样后: %d 帧, %d 行, %d 列\n', size(grid_data, 1), num_rows, num_cols);
else
    % 如果帧数已经小于或等于目标帧数，就不需要降采样
    fprintf('原始帧数 (%d) 已经小于或等于目标帧数 (%d)，不需要降采样\n', num_frames, target_frames);
    grid_data = original_grid_data;
    time_points = original_time_points;
end

%% 3. 数据分析
% 计算整个数据集的最大值和最小值
min_val = min(grid_data(:));
max_val = max(grid_data(:));
fprintf('数据范围: 最小值 = %.4e, 最大值 = %.4e\n', min_val, max_val);

%% 4. 创建输出目录
output_dir = './visualization_results';
if ~exist(output_dir, 'dir')
    mkdir(output_dir);
end

%% 5. 可视化配置
% 共享可视化选项
common_options = struct();
common_options.labelX = 1:6;            % X轴标签为1-6
common_options.labelY = 2:5;            % Y轴标签为2-5
common_options.timestampLoc = [1.05, 0.95];  % 时间戳放在图像右侧
common_options.fontName = chinese_font;  % 使用中文字体
common_options.ReverseY = false;         % 左下角作为原点
common_options.zlim = [min_val, max_val];% 使用数据实际范围

% 热图动画配置
heatmap_options = common_options;
heatmap_options.title = '变形监测数据可视化 - 热图';
heatmap_options.colorbarLabel = '变形量 (m)';
heatmap_options.filename = fullfile(output_dir, 'heatmap_animation.mp4');
heatmap_options.colormap = 'turbo';
heatmap_options.gridLines = true;

% 3D表面动画配置
surface_options = common_options;
surface_options.title = '变形监测数据可视化 - 3D表面';
surface_options.zLabel = '变形量 (m)';
surface_options.filename = fullfile(output_dir, 'surface_animation.mp4');
surface_options.lighting = 'advanced';
surface_options.rotateView = false;
surface_options.surfaceAlpha = 0.8;

% 剖面动画配置
profile_options = common_options;
profile_options.title = '变形监测数据可视化 - 剖面分析';
profile_options.colorbarLabel = '变形量 (m)';
profile_options.filename = fullfile(output_dir, 'profile_animation.mp4');
profile_options.profileRow = 3;  % 选择一个在labelY范围内的行
profile_options.profileCol = 4;  % 选择一个在labelX范围内的列

%% 6. 执行可视化
% 调用热图动画函数
fprintf('\n正在生成热图动画...\n');
heatmapAnimation(grid_data, time_points, ...
    'Title', heatmap_options.title, ...
    'ColorbarLabel', heatmap_options.colorbarLabel, ...
    'Filename', heatmap_options.filename, ...
    'LabelX', heatmap_options.labelX, ...
    'LabelY', heatmap_options.labelY, ...
    'TimestampLocation', heatmap_options.timestampLoc, ...
    'FontName', heatmap_options.fontName, ...
    'ReverseY', heatmap_options.ReverseY, ...
    'LimitsColor', heatmap_options.zlim, ...
    'Colormap', heatmap_options.colormap, ...
    'GridLines', heatmap_options.gridLines);

% % 调用3D表面动画函数
% fprintf('\n正在生成3D表面动画...\n');
% surfaceAnimation(grid_data, time_points, ...
%     'Title', surface_options.title, ...
%     'ZLabel', surface_options.zLabel, ...
%     'Filename', surface_options.filename, ...
%     'LabelX', surface_options.labelX, ...
%     'LabelY', surface_options.labelY, ...
%     'TimestampLocation', surface_options.timestampLoc, ...
%     'FontName', surface_options.fontName, ...
%     'ReverseY', surface_options.ReverseY, ...
%     'Lighting', surface_options.lighting, ...
%     'RotateView', surface_options.rotateView, ...
%     'LimitsZ', surface_options.zlim, ...
%     'SurfaceAlpha', surface_options.surfaceAlpha);

% 调用剖面动画函数
fprintf('\n正在生成剖面动画...\n');
profileAnimation(grid_data, time_points, ...
    'Title', profile_options.title, ...
    'ColorbarLabel', profile_options.colorbarLabel, ...
    'Filename', profile_options.filename, ...
    'LabelX', profile_options.labelX, ...
    'LabelY', profile_options.labelY, ...
    'TimestampLocation', profile_options.timestampLoc, ...
    'FontName', profile_options.fontName, ...
    'ReverseY', profile_options.ReverseY, ...
    'ProfileRow', profile_options.profileRow, ...
    'ProfileCol', profile_options.profileCol, ...
    'LimitsColor', profile_options.zlim);

%% 7. 完成信息
fprintf('\n所有可视化任务已完成！\n');
fprintf('输出目录: %s\n', output_dir);
fprintf('生成的文件:\n');
fprintf('  - %s\n', heatmap_options.filename);
fprintf('  - %s\n', surface_options.filename);
fprintf('  - %s\n', profile_options.filename);

% %% 数据可视化流程 - 使用科研可视化套件
% % 本脚本演示如何使用高级可视化函数处理和可视化科研数据
% 
% %% 0. 设置中文字体支持
% % 检测操作系统，设置适当的中文字体
% if ispc % Windows系统
%     set(0, 'DefaultAxesFontName', 'SimHei');
%     set(0, 'DefaultTextFontName', 'SimHei');
%     chinese_font = 'SimHei'; % 黑体
% elseif ismac % macOS系统
%     set(0, 'DefaultAxesFontName', 'STHeiti');
%     set(0, 'DefaultTextFontName', 'STHeiti');
%     chinese_font = 'STHeiti'; % 黑体-简
% else % Linux系统
%     set(0, 'DefaultAxesFontName', 'WenQuanYi Micro Hei');
%     set(0, 'DefaultTextFontName', 'WenQuanYi Micro Hei');
%     chinese_font = 'WenQuanYi Micro Hei';
% end
% 
% % 修复负号显示问题
% set(0, 'DefaultAxesTickDir', 'out');
% set(0, 'DefaultAxesXMinorTick', 'on');
% set(0, 'DefaultAxesYMinorTick', 'on');
% 
% %% 1. 加载和处理数据
% % 加载数据
% data = load('my_processed_data.mat');
% % 获取原始grid_data和时间点
% original_grid_data = data.grid_data;
% original_time_points = data.time_points;
% 
% % 获取原始形状
% [num_frames, num_rows, num_cols] = size(original_grid_data);
% fprintf('原始数据: %d 帧, %d 行, %d 列\n', num_frames, num_rows, num_cols);
% 
% %% 2. 数据降采样（如有必要）
% % 设置目标帧数
% target_frames = 500; % 设置你想要的帧数
% 
% % 如果原始帧数大于目标帧数，则进行降采样
% if num_frames > target_frames
%     % 降采样方法: 简单的等距离抽样
%     downsample_indices = round(linspace(1, num_frames, target_frames));
%     grid_data = original_grid_data(downsample_indices, :, :);
%     time_points = original_time_points(downsample_indices);
% 
%     fprintf('降采样后: %d 帧, %d 行, %d 列\n', size(grid_data, 1), num_rows, num_cols);
% else
%     % 如果帧数已经小于或等于目标帧数，就不需要降采样
%     fprintf('原始帧数 (%d) 已经小于或等于目标帧数 (%d)，不需要降采样\n', num_frames, target_frames);
%     grid_data = original_grid_data;
%     time_points = original_time_points;
% end
% 
% %% 3. 数据分析
% % 计算整个数据集的最大值和最小值
% min_val = min(grid_data(:));
% max_val = max(grid_data(:));
% fprintf('数据范围: 最小值 = %.4e, 最大值 = %.4e\n', min_val, max_val);
% 
% %% 4. 设置可视化参数
% % 创建输出目录
% output_dir = './visualization_results';
% if ~exist(output_dir, 'dir')
%     mkdir(output_dir);
% end
% 
% % 设置可视化配置
% options = struct();
% options.zlim = [min_val, max_val];         % 颜色和Z轴范围
% options.timeUnit = 's';                     % 时间单位
% options.title = '变形监测数据可视化';        % 公共标题
% options.colorbarLabel = '变形量 (m)';       % 颜色条标签（中文）
% options.watermark = '© 研究小组 2025';      % 水印文本
% options.resolution = [1920, 1080];         % 高分辨率输出
% options.quality = 95;                       % 高质量视频
% options.fontName = chinese_font;            % 使用中文字体
% 
% % 设置行列刻度标签（1-6列, 2-5行）
% options.labelX = 1:6;                      % 列标签：1到6
% options.labelY = 2:5;                      % 行标签：2到5
% 
% % 为不同类型的可视化设置特定的参数
% surface_options = options;
% surface_options.filename = 'surface_animation.mp4';
% surface_options.lighting = 'advanced';      % 高级光照效果
% surface_options.rotateView = true;          % 启用旋转视图
% surface_options.initialView = [-37.5, 30];  % 初始视角
% surface_options.timestampLoc = [0.65, 0.92]; % 时间戳位置在右上角
% 
% heatmap_options = options;
% heatmap_options.filename = 'heatmap_animation.mp4';
% heatmap_options.gridLines = true;           % 显示网格线
% heatmap_options.colormap = 'turbo';         % 使用turbo颜色映射
% heatmap_options.interpolation = 'bilinear'; % 平滑插值
% heatmap_options.timestampLoc = [0.65, 0.92]; % 时间戳位置在右上角
% 
% profile_options = options;
% profile_options.filename = 'profile_animation.mp4';
% profile_options.profileRow = 2;             % 横向剖面行索引
% profile_options.profileCol = 3;             % 纵向剖面列索引
% profile_options.title = [options.title ' - 剖面分析']; % 特定标题
% profile_options.timestampLoc = [0.65, 0.92]; % 时间戳位置在右上角

% %% 5. 创建3D表面动画
% fprintf('\n正在生成3D表面动画...\n');
% surfaceAnimation(grid_data, time_points, ...
%     'Title', surface_options.title, ...
%     'ZLabel', surface_options.colorbarLabel, ...
%     'ColorbarLabel', surface_options.colorbarLabel, ...
%     'LimitsZ', surface_options.zlim, ...
%     'TimeUnit', surface_options.timeUnit, ...
%     'Lighting', surface_options.lighting, ...
%     'RotateView', surface_options.rotateView, ...
%     'ViewAngle', surface_options.initialView, ...
%     'Filename', surface_options.filename, ...
%     'Directory', output_dir, ...
%     'Resolution', surface_options.resolution, ...
%     'Quality', surface_options.quality, ...
%     'WatermarkText', surface_options.watermark, ...
%     'SurfaceAlpha', 1.0, ...
%     'FontName', surface_options.fontName, ...
%     'LabelX', surface_options.labelX, ...
%     'LabelY', surface_options.labelY, ...
%     'TimestampLocation', surface_options.timestampLoc, ...
%     'BackgroundColor', [1 1 1]);  % 白色背景

%% 6. 创建热图动画
fprintf('\n正在生成热图动画...\n');
heatmapAnimation(grid_data, time_points, ...
    'Title', heatmap_options.title, ...
    'ColorbarLabel', heatmap_options.colorbarLabel, ...
    'LimitsColor', heatmap_options.zlim, ...
    'TimeUnit', heatmap_options.timeUnit, ...
    'Colormap', heatmap_options.colormap, ...
    'GridLines', heatmap_options.gridLines, ...
    'Interpolation', heatmap_options.interpolation, ...
    'Filename', heatmap_options.filename, ...
    'Directory', output_dir, ...
    'Resolution', heatmap_options.resolution, ...
    'Quality', heatmap_options.quality, ...
    'WatermarkText', heatmap_options.watermark, ...
    'FontName', heatmap_options.fontName, ...
    'LabelX', heatmap_options.labelX, ...
    'LabelY', heatmap_options.labelY, ...
    'TimestampLocation', heatmap_options.timestampLoc, ...
    'ReverseY', false);  % 设置左下角为原点（Y轴不反转）

%% 7. 创建带剖面的热图动画
fprintf('\n正在生成带剖面的热图动画...\n');
profileAnimation(grid_data, time_points, ...
    'Title', profile_options.title, ...
    'ColorbarLabel', profile_options.colorbarLabel, ...
    'LimitsColor', profile_options.zlim, ...
    'TimeUnit', profile_options.timeUnit, ...
    'ProfileRow', profile_options.profileRow, ...
    'ProfileCol', profile_options.profileCol, ...
    'Colormap', heatmap_options.colormap, ...
    'GridLines', true, ...
    'Filename', profile_options.filename, ...
    'Directory', output_dir, ...
    'Resolution', profile_options.resolution, ...
    'Quality', profile_options.quality, ...
    'WatermarkText', profile_options.watermark, ...
    'FontName', profile_options.fontName, ...
    'LabelX', profile_options.labelX, ...
    'LabelY', profile_options.labelY, ...
    'TimestampLocation', profile_options.timestampLoc, ...
    'ReverseY', false);  % 设置左下角为原点（Y轴不反转）

%% 8. 完成信息
fprintf('\n所有可视化任务已完成！\n');
fprintf('输出目录: %s\n', output_dir);
fprintf('生成的文件:\n');
fprintf('  - %s\n', surface_options.filename);
fprintf('  - %s\n', heatmap_options.filename);
fprintf('  - %s\n', profile_options.filename);


% 
% %% 数据可视化流程 - 使用科研可视化套件
% % 本脚本演示如何使用高级可视化函数处理和可视化科研数据
% 
% %% 1. 加载和处理数据
% % 加载数据
% data = load('my_processed_data.mat');
% % 获取原始grid_data和时间点
% original_grid_data = data.grid_data;
% original_time_points = data.time_points;
% 
% % 获取原始形状
% [num_frames, num_rows, num_cols] = size(original_grid_data);
% fprintf('原始数据: %d 帧, %d 行, %d 列\n', num_frames, num_rows, num_cols);
% 
% %% 2. 数据降采样（如有必要）
% % 设置目标帧数
% target_frames = 500; % 设置你想要的帧数
% 
% % 如果原始帧数大于目标帧数，则进行降采样
% if num_frames > target_frames
%     % 降采样方法: 简单的等距离抽样
%     downsample_indices = round(linspace(1, num_frames, target_frames));
%     grid_data = original_grid_data(downsample_indices, :, :);
%     time_points = original_time_points(downsample_indices);
% 
%     fprintf('降采样后: %d 帧, %d 行, %d 列\n', size(grid_data, 1), num_rows, num_cols);
% else
%     % 如果帧数已经小于或等于目标帧数，就不需要降采样
%     fprintf('原始帧数 (%d) 已经小于或等于目标帧数 (%d)，不需要降采样\n', num_frames, target_frames);
%     grid_data = original_grid_data;
%     time_points = original_time_points;
% end
% 
% %% 3. 数据分析
% % 计算整个数据集的最大值和最小值
% min_val = min(grid_data(:));
% max_val = max(grid_data(:));
% fprintf('数据范围: 最小值 = %.4e, 最大值 = %.4e\n', min_val, max_val);
% 
% %% 4. 设置可视化参数
% % 创建输出目录
% output_dir = './visualization_results';
% if ~exist(output_dir, 'dir')
%     mkdir(output_dir);
% end
% 
% % 设置可视化配置
% options = struct();
% options.zlim = [min_val, max_val];         % 颜色和Z轴范围
% options.timeUnit = 's';                     % 时间单位
% options.title = '变形监测数据可视化';        % 公共标题
% options.colorbarLabel = 'Swelling (m)';     % 颜色条标签
% options.watermark = '© 研究小组 2025';       % 水印文本
% options.resolution = [1920, 1080];          % 高分辨率输出
% options.quality = 95;                       % 高质量视频
% 
% % 为不同类型的可视化设置特定的参数
% surface_options = options;
% surface_options.filename = 'surface_animation.mp4';
% surface_options.lighting = 'advanced';      % 高级光照效果
% surface_options.rotateView = false;          % 启用旋转视图
% surface_options.initialView = [-37.5, 30];  % 初始视角
% 
% heatmap_options = options;
% heatmap_options.filename = 'heatmap_animation.mp4';
% heatmap_options.gridLines = true;           % 显示网格线
% heatmap_options.colormap = 'turbo';         % 使用turbo颜色映射
% heatmap_options.interpolation = 'bilinear'; % 平滑插值
% 
% profile_options = options;
% profile_options.filename = 'profile_animation.mp4';
% profile_options.profileRow = 2;             % 横向剖面行索引
% profile_options.profileCol = 3;             % 纵向剖面列索引
% profile_options.title = [options.title ' - 剖面分析']; % 特定标题
% 
% %% 5. 创建3D表面动画
% fprintf('\n正在生成3D表面动画...\n');
% surfaceAnimation(grid_data, time_points, ...
%     'Title', surface_options.title, ...
%     'ZLabel', surface_options.colorbarLabel, ...
%     'ColorbarLabel', surface_options.colorbarLabel, ...
%     'LimitsZ', surface_options.zlim, ...
%     'TimeUnit', surface_options.timeUnit, ...
%     'Lighting', surface_options.lighting, ...
%     'RotateView', surface_options.rotateView, ...
%     'ViewAngle', surface_options.initialView, ...
%     'Filename', surface_options.filename, ...
%     'Directory', output_dir, ...
%     'Resolution', surface_options.resolution, ...
%     'Quality', surface_options.quality, ...
%     'WatermarkText', surface_options.watermark, ...
%     'SurfaceAlpha', 1.0, ...
%     'BackgroundColor', [1 1 1]);  % 白色背景
% 
% %% 6. 创建热图动画
% fprintf('\n正在生成热图动画...\n');
% heatmapAnimation(grid_data, time_points, ...
%     'Title', heatmap_options.title, ...
%     'ColorbarLabel', heatmap_options.colorbarLabel, ...
%     'LimitsColor', heatmap_options.zlim, ...
%     'TimeUnit', heatmap_options.timeUnit, ...
%     'Colormap', heatmap_options.colormap, ...
%     'GridLines', heatmap_options.gridLines, ...
%     'Interpolation', heatmap_options.interpolation, ...
%     'Filename', heatmap_options.filename, ...
%     'Directory', output_dir, ...
%     'Resolution', heatmap_options.resolution, ...
%     'Quality', heatmap_options.quality, ...
%     'WatermarkText', heatmap_options.watermark);
% 
% %% 7. 创建带剖面的热图动画
% fprintf('\n正在生成带剖面的热图动画...\n');
% profileAnimation(grid_data, time_points, ...
%     'Title', profile_options.title, ...
%     'ColorbarLabel', profile_options.colorbarLabel, ...
%     'LimitsColor', profile_options.zlim, ...
%     'TimeUnit', profile_options.timeUnit, ...
%     'ProfileRow', profile_options.profileRow, ...
%     'ProfileCol', profile_options.profileCol, ...
%     'Colormap', heatmap_options.colormap, ...
%     'GridLines', true, ...
%     'Filename', profile_options.filename, ...
%     'Directory', output_dir, ...
%     'Resolution', profile_options.resolution, ...
%     'Quality', profile_options.quality, ...
%     'WatermarkText', profile_options.watermark);
% 
% %% 8. 完成信息
% fprintf('\n所有可视化任务已完成！\n');
% fprintf('输出目录: %s\n', output_dir);
% fprintf('生成的文件:\n');
% fprintf('  - %s\n', surface_options.filename);
% fprintf('  - %s\n', heatmap_options.filename);
% fprintf('  - %s\n', profile_options.filename);

% %% 示例1: 创建旋转的3D表面动画
% [X,Y] = meshgrid(-3:0.2:3);
% frames = 100;
% z = zeros(frames, size(X,1), size(X,2));
% t = linspace(0, 2*pi, frames);
% for i = 1:frames
%     z(i,:,:) = peaks(X,Y) * sin(t(i));
% end
% 
% surfaceAnimation(z, t, 'RotateView', true, 'LimitsZ', [-8 8], ...
%                  'Title', '动态峰值函数', 'ZLabel', '高度', ...
%                  'TimeUnit', 's', 'SurfaceAlpha', 0.8, ...
%                  'Lighting', 'advanced');
% 
% %% 示例2: 创建热图动画
% heatmapAnimation(z, t, 'Title', '热力分布动态变化', ...
%                 'ColorbarLabel', '温度 (°C)', ...
%                 'TimeUnit', 's', 'GridLines', true, ...
%                 'Colormap', 'hot');
% 
% %% 示例3: 创建带剖面的热图动画
% profileAnimation(z, t, 'Title', '热点追踪及剖面分析', ...
%                 'ColorbarLabel', '强度', ...
%                 'TimeUnit', 's', 'GridLines', true, ...
%                 'ProfileRow', 20, 'ProfileCol', 25);


%% ScientificVisualization.m
% 科研数据可视化工具包 - 用于创建高质量的科研级动态可视化
% 包含三个核心函数：
% - surfaceAnimation: 创建3D表面动画
% - heatmapAnimation: 创建热图动画
% - profileAnimation: 创建带剖面的热图动画
%
% 作者: Claude AI
% 版本: 1.0
% 日期: 2025-03-27

%% 3D表面动画函数
function outfile = surfaceAnimation(data, times, varargin)
% SURFACEANIMATION 创建高质量3D表面动画视频，适用于科研展示
%
% 用法:
%   outfile = surfaceAnimation(data, times)
%   outfile = surfaceAnimation(data, times, 'Name', Value, ...)
%
% 必需参数:
%   data  - 三维数组，维度为 [时间 x 行 x 列]
%   times - 时间点向量，长度必须与data的第一维一致
%
% 可选名称-值对参数:
%   'Title'         - 图表标题，默认：'Surface Animation'
%   'ZLabel'        - Z轴标签，默认：'Value'
%   'LabelX'        - X轴刻度标签，空单元格数组或数值向量，默认自动生成
%   'LabelY'        - Y轴刻度标签，空单元格数组或数值向量，默认自动生成
%   'LimitsZ'       - Z轴范围 [min max]，默认：自动
%   'Colormap'      - 色彩映射名称，默认：'turbo'
%   'ColorbarLabel' - 颜色条标签，默认：'Value'
%   'TimeFormat'    - 时间标签格式，默认：'Time: %.2f'
%   'TimeUnit'      - 时间单位，附加到时间标签，默认：''
%   'ViewAngle'     - 视角 [方位角 仰角]，默认：[30 30]
%   'RotateView'    - 逻辑值，是否旋转视角，默认：false
%   'Lighting'      - 光照模式，可选：'none', 'basic', 'advanced'，默认：'basic'
%   'SurfaceAlpha'  - 表面透明度 (0-1)，默认：1
%   'Filename'      - 输出文件名，默认：'surface_animation.mp4'
%   'Directory'     - 输出目录，默认：'./animations'
%   'Resolution'    - 分辨率 [宽 高]，默认：[1920 1080]
%   'FrameRate'     - 帧率，默认：30
%   'Quality'       - 视频质量 (1-100)，默认：95
%   'FontName'      - 字体名称，默认：'Arial'
%   'FontSize'      - 基础字体大小，默认：12
%   'FontWeight'    - 字体粗细，默认：'normal'
%   'GridColor'     - 网格颜色，默认：[0.15 0.15 0.15]
%   'BackgroundColor' - 背景颜色，默认：[1 1 1]
%   'WatermarkText' - 水印文本，默认：''
%   'TimestampLocation' - 时间戳位置 [x y]，默认：[0.05 0.92]
%   'ShadeMode'     - 表面着色模式，'flat'或'interp'，默认：'interp'
%   'ShowProgress'  - 逻辑值，是否显示进度条，默认：true
%
% 返回值:
%   outfile - 生成的视频文件完整路径
%
% 示例:
%   % 创建旋转的3D表面动画:
%   [X,Y] = meshgrid(-3:0.2:3);
%   frames = 100;
%   z = zeros(frames, size(X,1), size(X,2));
%   t = linspace(0, 2*pi, frames);
%   for i = 1:frames
%       z(i,:,:) = peaks(X,Y) * sin(t(i));
%   end
%   surfaceAnimation(z, t, 'RotateView', true, 'LimitsZ', [-8 8], ...
%                    'Title', '动态峰值函数', 'ZLabel', '高度', ...
%                    'TimeUnit', 's', 'SurfaceAlpha', 0.8, ...
%                    'Lighting', 'advanced');

% 输入参数解析
p = inputParser;
p.FunctionName = 'surfaceAnimation';
p.KeepUnmatched = false;
p.CaseSensitive = false;

addRequired(p, 'data', @(x) validateattributes(x, {'numeric'}, {'3d'}));
addRequired(p, 'times', @(x) validateattributes(x, {'numeric'}, {'vector'}));

% 内容参数
addParameter(p, 'Title', 'Surface Animation', @ischar);
addParameter(p, 'ZLabel', 'Value', @ischar);
addParameter(p, 'LabelX', {}, @(x) isempty(x) || iscell(x) || isnumeric(x));
addParameter(p, 'LabelY', {}, @(x) isempty(x) || iscell(x) || isnumeric(x));
addParameter(p, 'LimitsZ', [], @(x) isempty(x) || (isnumeric(x) && numel(x)==2));
addParameter(p, 'Colormap', 'turbo', @ischar);
addParameter(p, 'ColorbarLabel', 'Value', @ischar);
addParameter(p, 'TimeFormat', 'Time: %.2f', @ischar);
addParameter(p, 'TimeUnit', '', @ischar);
addParameter(p, 'ViewAngle', [30 30], @(x) isnumeric(x) && numel(x)==2);
addParameter(p, 'RotateView', false, @islogical);
addParameter(p, 'Lighting', 'basic', @(x) ismember(x, {'none', 'basic', 'advanced'}));
addParameter(p, 'SurfaceAlpha', 1, @(x) isnumeric(x) && x>=0 && x<=1);

% 输出参数
addParameter(p, 'Filename', 'surface_animation.mp4', @ischar);
addParameter(p, 'Directory', './animations', @ischar);
addParameter(p, 'Resolution', [1920 1080], @(x) isnumeric(x) && numel(x)==2);
addParameter(p, 'FrameRate', 30, @(x) isnumeric(x) && isscalar(x) && x>0);
addParameter(p, 'Quality', 95, @(x) isnumeric(x) && isscalar(x) && x>=1 && x<=100);

% 样式参数
addParameter(p, 'FontName', 'Arial', @ischar);
addParameter(p, 'FontSize', 12, @(x) isnumeric(x) && isscalar(x) && x>0);
addParameter(p, 'FontWeight', 'normal', @ischar);
addParameter(p, 'GridColor', [0.15 0.15 0.15], @(x) isnumeric(x) && numel(x)==3);
addParameter(p, 'BackgroundColor', [1 1 1], @(x) isnumeric(x) && numel(x)==3);
addParameter(p, 'WatermarkText', '', @ischar);
addParameter(p, 'TimestampLocation', [0.05 0.92], @(x) isnumeric(x) && numel(x)==2);
addParameter(p, 'ShadeMode', 'interp', @(x) ismember(x, {'flat', 'interp'}));
addParameter(p, 'ShowProgress', true, @islogical);

parse(p, data, times, varargin{:});
args = p.Results;

% 检查时间维度
[numFrames, numRows, numCols] = size(data);
if length(times) ~= numFrames
    error('时间向量长度必须与数据第一维相同。');
end

% 预处理时间标签格式
if ~isempty(args.TimeUnit)
    timeFormat = [args.TimeFormat ' ' args.TimeUnit];
else
    timeFormat = args.TimeFormat;
end

% 创建输出目录
if ~exist(args.Directory, 'dir')
    mkdir(args.Directory);
end
outfile = fullfile(args.Directory, args.Filename);

% 确定Z轴范围
if isempty(args.LimitsZ)
    zMin = min(data(:));
    zMax = max(data(:));
    zRange = zMax - zMin;
    zLimits = [zMin - 0.05*zRange, zMax + 0.05*zRange];
else
    zLimits = args.LimitsZ;
end

% 生成网格
[rows, cols] = meshgrid(1:numRows, 1:numCols);
rows = rows';
cols = cols';

% 创建图形和坐标轴
screenSize = get(0, 'ScreenSize');
figPos = [50 50 args.Resolution];
fig = figure('Position', figPos, ...
             'Color', args.BackgroundColor, ...
             'Renderer', 'opengl', ...
             'InvertHardcopy', 'off', ...
             'Visible', 'off'); % 使用离屏渲染以提高性能

% 创建3D轴对象
ax = axes('Parent', fig);

% 设置默认轴标签
if isempty(args.LabelX)
    % 默认X轴标签
    labelX = cellstr(string(1:numCols));
else
    if isnumeric(args.LabelX)
        labelX = cellstr(string(args.LabelX));
    else
        labelX = args.LabelX;
    end
end

if isempty(args.LabelY)
    % 默认Y轴标签
    labelY = cellstr(string(1:numRows));
else
    if isnumeric(args.LabelY)
        labelY = cellstr(string(args.LabelY));
    else
        labelY = args.LabelY;
    end
end

% 应用标签到轴
if numel(labelX) > 10
    % 如果标签过多，只显示部分以避免拥挤
    step = floor(numel(labelX) / 5);
    ticksX = 1:step:numCols;
    set(ax, 'XTick', ticksX);
    set(ax, 'XTickLabel', labelX(ticksX));
else
    set(ax, 'XTick', 1:numCols);
    set(ax, 'XTickLabel', labelX);
end

if numel(labelY) > 10
    % 如果标签过多，只显示部分以避免拥挤
    step = floor(numel(labelY) / 5);
    ticksY = 1:step:numRows;
    set(ax, 'YTick', ticksY);
    set(ax, 'YTickLabel', labelY(ticksY));
else
    set(ax, 'YTick', 1:numRows);
    set(ax, 'YTickLabel', labelY);
end

% 初始化曲面绘图
surf_h = surf(ax, cols, rows, squeeze(data(1,:,:)), ...
              'EdgeColor', 'none', ...
              'FaceAlpha', args.SurfaceAlpha, ...
              'FaceLighting', 'phong');

% 设置着色模式
shading(ax, args.ShadeMode);

% 设置颜色映射
colormap(ax, args.Colormap);

% 设置Z轴范围
set(ax, 'ZLim', zLimits);

% 设置颜色条
c = colorbar(ax);
c.Label.String = args.ColorbarLabel;
c.Label.FontSize = args.FontSize + 1;
c.Label.FontWeight = 'bold';

% 设置轴标签和标题
xlabel(ax, 'Column', 'FontSize', args.FontSize + 1, 'FontWeight', 'bold');
ylabel(ax, 'Row', 'FontSize', args.FontSize + 1, 'FontWeight', 'bold');
zlabel(ax, args.ZLabel, 'FontSize', args.FontSize + 1, 'FontWeight', 'bold');
title(ax, args.Title, 'FontSize', args.FontSize + 4, 'FontWeight', 'bold');

% 设置字体
set(ax, 'FontName', args.FontName);
set(ax, 'FontSize', args.FontSize);
set(ax, 'FontWeight', args.FontWeight);

% 设置网格
grid(ax, 'on');
set(ax, 'GridColor', args.GridColor);
set(ax, 'GridAlpha', 0.3);

% 设置初始视角
view(ax, args.ViewAngle);

% 设置照明
if strcmp(args.Lighting, 'basic')
    % 基本光照
    light('Position', [1 1 1], 'Style', 'infinite');
    lighting phong;
elseif strcmp(args.Lighting, 'advanced')
    % 高级光照 - 多个光源
    light('Position', [1 1 1], 'Style', 'infinite', 'Color', [0.8 0.8 0.9]);
    light('Position', [-3 -1 0.5], 'Style', 'infinite', 'Color', [0.2 0.2 0.3]);
    light('Position', [0 0 -1], 'Style', 'local', 'Color', [0.9 0.9 0.9]);
    lighting phong;
    material dull;
end

% 添加水印
if ~isempty(args.WatermarkText)
    annotation('textbox', [0.5, 0.01, 0, 0], 'String', args.WatermarkText, ...
               'FontSize', args.FontSize - 2, 'FontName', args.FontName, ...
               'EdgeColor', 'none', 'Color', [0.5 0.5 0.5], ...
               'HorizontalAlignment', 'center');
end

% 添加时间戳
if ~isempty(timeFormat)
    time_text = text(ax, args.TimestampLocation(1), args.TimestampLocation(2), ...
                    sprintf(timeFormat, times(1)), ...
                    'Units', 'normalized', ...
                    'FontSize', args.FontSize + 2, ...
                    'FontWeight', 'bold', ...
                    'BackgroundColor', [1 1 1 0.7], ...
                    'Margin', 3);
end

% 设置视频写入器
writerObj = VideoWriter(outfile, 'MPEG-4');
writerObj.FrameRate = args.FrameRate;
writerObj.Quality = args.Quality;
open(writerObj);

% 如果启用旋转，计算视角动画参数
if args.RotateView
    % 计算平滑的旋转角度
    azimuth = linspace(args.ViewAngle(1), args.ViewAngle(1) + 360, numFrames+1);
    azimuth = azimuth(1:end-1); % 移除多余点以确保帧数正确
    
    % 为仰角添加微小波动以增加动态效果
    elevation = args.ViewAngle(2) + 15 * sin(linspace(0, 2*pi, numFrames));
else
    % 固定视角
    azimuth = repmat(args.ViewAngle(1), 1, numFrames);
    elevation = repmat(args.ViewAngle(2), 1, numFrames);
end

% 根据条件初始化进度显示
if args.ShowProgress
    fprintf('生成3D表面动画: %s\n', outfile);
    progress_text = sprintf('完成: %%%.1f', 0);
    progress_bar = waitbar(0, progress_text, 'Name', '3D Surface Animation Progress');
end

% 渲染动画帧
tic;
for frame = 1:numFrames
    % 更新曲面数据
    set(surf_h, 'ZData', squeeze(data(frame,:,:)));
    
    % 更新时间戳
    if ~isempty(timeFormat)
        set(time_text, 'String', sprintf(timeFormat, times(frame)));
    end
    
    % 如果启用视角旋转，更新视角
    if args.RotateView || (frame > 1 && azimuth(frame) ~= azimuth(frame-1))
        view(ax, azimuth(frame), elevation(frame));
    end
    
    % 刷新图形
    drawnow;
    
    % 捕获当前帧
    frame_data = getframe(fig);
    
    % 写入帧到视频
    writeVideo(writerObj, frame_data);
    
    % 更新进度显示
    if args.ShowProgress && mod(frame, max(1, round(numFrames/100))) == 0
        progress = frame / numFrames;
        elapsed = toc;
        estimated_total = elapsed / progress;
        remaining = estimated_total - elapsed;
        
        progress_text = sprintf('完成: %.1f%% - 剩余时间: %.1f秒', progress*100, remaining);
        waitbar(progress, progress_bar, progress_text);
    end
end

% 关闭视频写入器
close(writerObj);

% 关闭进度条
if args.ShowProgress
    delete(progress_bar);
end

% 关闭图形
close(fig);

% 完成信息
if args.ShowProgress
    fprintf('3D表面动画已完成！\n');
    fprintf('总帧数: %d, 视频时长: %.1f秒\n', numFrames, numFrames/args.FrameRate);
    fprintf('输出文件: %s\n', outfile);
    fprintf('总耗时: %.1f秒\n', toc);
end

end

%% 热图动画函数
function outfile = heatmapAnimation(data, times, varargin)
% HEATMAPANIMATION 创建高质量热图动画视频，适用于科研展示
%
% 用法:
%   outfile = heatmapAnimation(data, times)
%   outfile = heatmapAnimation(data, times, 'Name', Value, ...)
%
% 必需参数:
%   data  - 三维数组，维度为 [时间 x 行 x 列]
%   times - 时间点向量，长度必须与data的第一维一致
%
% 可选名称-值对参数:
%   'Title'         - 图表标题，默认：'Heatmap Animation'
%   'LabelX'        - X轴刻度标签，空单元格数组或数值向量，默认自动生成
%   'LabelY'        - Y轴刻度标签，空单元格数组或数值向量，默认自动生成
%   'Colormap'      - 色彩映射名称，默认：'turbo'
%   'ColorbarLabel' - 颜色条标签，默认：'Value'
%   'LimitsColor'   - 颜色范围 [min max]，默认：自动
%   'TimeFormat'    - 时间标签格式，默认：'Time: %.2f'
%   'TimeUnit'      - 时间单位，附加到时间标签，默认：''
%   'AspectRatio'   - 热图纵横比例，可选：'equal', 'auto'，默认：'equal'
%   'Interpolation' - 插值方法，可选：'none','bilinear'等，默认：'bilinear'
%   'Filename'      - 输出文件名，默认：'heatmap_animation.mp4'
%   'Directory'     - 输出目录，默认：'./animations'
%   'Resolution'    - 分辨率 [宽 高]，默认：[1920 1080]
%   'FrameRate'     - 帧率，默认：30
%   'Quality'       - 视频质量 (1-100)，默认：95
%   'FontName'      - 字体名称，默认：'Arial'
%   'FontSize'      - 基础字体大小，默认：12
%   'FontWeight'    - 字体粗细，默认：'normal'
%   'GridLines'     - 逻辑值，是否显示网格线，默认：false
%   'GridColor'     - 网格颜色，默认：[0.15 0.15 0.15]
%   'BackgroundColor' - 背景颜色，默认：[1 1 1]
%   'WatermarkText' - 水印文本，默认：''
%   'TimestampLocation' - 时间戳位置 [x y]，默认：[0.05 0.92]
%   'ReverseY'      - 逻辑值，是否反转Y轴，默认：false
%   'ShowProgress'  - 逻辑值，是否显示进度条，默认：true
%
% 返回值:
%   outfile - 生成的视频文件完整路径
%
% 示例:
%   % 创建简单的热图动画:
%   [X,Y] = meshgrid(-3:0.15:3);
%   frames = 60;
%   z = zeros(frames, size(X,1), size(X,2));
%   t = linspace(0, 4*pi, frames);
%   for i = 1:frames
%       z(i,:,:) = peaks(X,Y) * sin(t(i)/2) * cos(t(i)/4);
%   end
%   heatmapAnimation(z, t, 'Title', '动态热图展示', ...
%                   'ColorbarLabel', '温度 (°C)', ...
%                   'TimeUnit', 's', 'GridLines', true);

% 输入参数解析
p = inputParser;
p.FunctionName = 'heatmapAnimation';
p.KeepUnmatched = false;
p.CaseSensitive = false;

addRequired(p, 'data', @(x) validateattributes(x, {'numeric'}, {'3d'}));
addRequired(p, 'times', @(x) validateattributes(x, {'numeric'}, {'vector'}));

% 内容参数
addParameter(p, 'Title', 'Heatmap Animation', @ischar);
addParameter(p, 'LabelX', {}, @(x) isempty(x) || iscell(x) || isnumeric(x));
addParameter(p, 'LabelY', {}, @(x) isempty(x) || iscell(x) || isnumeric(x));
addParameter(p, 'Colormap', 'turbo', @ischar);
addParameter(p, 'ColorbarLabel', 'Value', @ischar);
addParameter(p, 'LimitsColor', [], @(x) isempty(x) || (isnumeric(x) && numel(x)==2));
addParameter(p, 'TimeFormat', 'Time: %.2f', @ischar);
addParameter(p, 'TimeUnit', '', @ischar);
addParameter(p, 'AspectRatio', 'equal', @(x) ismember(x, {'equal', 'auto'}));
addParameter(p, 'Interpolation', 'bilinear', @ischar);

% 输出参数
addParameter(p, 'Filename', 'heatmap_animation.mp4', @ischar);
addParameter(p, 'Directory', './animations', @ischar);
addParameter(p, 'Resolution', [1920 1080], @(x) isnumeric(x) && numel(x)==2);
addParameter(p, 'FrameRate', 30, @(x) isnumeric(x) && isscalar(x) && x>0);
addParameter(p, 'Quality', 95, @(x) isnumeric(x) && isscalar(x) && x>=1 && x<=100);

% 样式参数
addParameter(p, 'FontName', 'Arial', @ischar);
addParameter(p, 'FontSize', 12, @(x) isnumeric(x) && isscalar(x) && x>0);
addParameter(p, 'FontWeight', 'normal', @ischar);
addParameter(p, 'GridLines', false, @islogical);
addParameter(p, 'GridColor', [0.15 0.15 0.15], @(x) isnumeric(x) && numel(x)==3);
addParameter(p, 'BackgroundColor', [1 1 1], @(x) isnumeric(x) && numel(x)==3);
addParameter(p, 'WatermarkText', '', @ischar);
addParameter(p, 'TimestampLocation', [0.05 0.92], @(x) isnumeric(x) && numel(x)==2);
addParameter(p, 'ReverseY', false, @islogical);
addParameter(p, 'ShowProgress', true, @islogical);

parse(p, data, times, varargin{:});
args = p.Results;

% 检查时间维度
[numFrames, numRows, numCols] = size(data);
if length(times) ~= numFrames
    error('时间向量长度必须与数据第一维相同。');
end

% 预处理时间标签格式
if ~isempty(args.TimeUnit)
    timeFormat = [args.TimeFormat ' ' args.TimeUnit];
else
    timeFormat = args.TimeFormat;
end

% 创建输出目录
if ~exist(args.Directory, 'dir')
    mkdir(args.Directory);
end
outfile = fullfile(args.Directory, args.Filename);

% 确定颜色范围
if isempty(args.LimitsColor)
    colorMin = min(data(:));
    colorMax = max(data(:));
    % 稍微扩展范围以提高视觉效果
    colorRange = colorMax - colorMin;
    colorLimits = [colorMin - 0.02*colorRange, colorMax + 0.02*colorRange];
else
    colorLimits = args.LimitsColor;
end

% 创建图形和坐标轴
fig = figure('Position', [50 50 args.Resolution], ...
             'Color', args.BackgroundColor, ...
             'InvertHardcopy', 'off');

% 创建轴对象并调整大小
pos = [0.1 0.15 0.7 0.7]; % 为标题和颜色条留出空间
ax = axes('Position', pos);

% 设置默认轴标签
if isempty(args.LabelX)
    % 默认X轴标签
    labelX = cellstr(string(1:numCols));
else
    if isnumeric(args.LabelX)
        labelX = cellstr(string(args.LabelX));
    else
        labelX = args.LabelX;
    end
end

if isempty(args.LabelY)
    % 默认Y轴标签
    labelY = cellstr(string(1:numRows));
else
    if isnumeric(args.LabelY)
        labelY = cellstr(string(args.LabelY));
    else
        labelY = args.LabelY;
    end
end

% 应用标签到轴
if numel(labelX) > 10
    % 如果标签过多，只显示部分以避免拥挤
    step = floor(numel(labelX) / 5);
    ticksX = 1:step:numCols;
    set(ax, 'XTick', ticksX);
    set(ax, 'XTickLabel', labelX(ticksX));
else
    set(ax, 'XTick', 1:numCols);
    set(ax, 'XTickLabel', labelX);
end

if numel(labelY) > 10
    % 如果标签过多，只显示部分以避免拥挤
    step = floor(numel(labelY) / 5);
    ticksY = 1:step:numRows;
    set(ax, 'YTick', ticksY);
    set(ax, 'YTickLabel', labelY(ticksY));
else
    set(ax, 'YTick', 1:numRows);
    set(ax, 'YTickLabel', labelY);
end

% 初始化热图
img_h = imagesc(ax, 1:numCols, 1:numRows, squeeze(data(1,:,:)));
if strcmp(args.AspectRatio, 'equal')
    axis(ax, 'equal');
else
    axis(ax, 'normal');
end
axis(ax, 'tight');

% 是否反转Y轴
if args.ReverseY
    set(ax, 'YDir', 'reverse');
end

% 设置颜色映射
colormap(ax, args.Colormap);

% 设置颜色范围
caxis(ax, colorLimits);

% 设置颜色条
c = colorbar(ax, 'Position', [0.85 0.15 0.03 0.7]);
c.Label.String = args.ColorbarLabel;
c.Label.FontSize = args.FontSize + 1;
c.Label.FontWeight = 'bold';

% 设置轴标签和标题
xlabel(ax, 'Column', 'FontSize', args.FontSize + 1, 'FontWeight', 'bold');
ylabel(ax, 'Row', 'FontSize', args.FontSize + 1, 'FontWeight', 'bold');
title(ax, args.Title, 'FontSize', args.FontSize + 4, 'FontWeight', 'bold');

% 设置字体
set(ax, 'FontName', args.FontName);
set(ax, 'FontSize', args.FontSize);
set(ax, 'FontWeight', args.FontWeight);

% 设置网格
if args.GridLines
    grid(ax, 'on');
    set(ax, 'GridColor', args.GridColor);
    set(ax, 'GridAlpha', 0.3);
else
    grid(ax, 'off');
end

% 设置插值方法
set(img_h, 'Interpolation', args.Interpolation);

% 添加水印
if ~isempty(args.WatermarkText)
    annotation('textbox', [0.5, 0.01, 0, 0], 'String', args.WatermarkText, ...
               'FontSize', args.FontSize - 2, 'FontName', args.FontName, ...
               'EdgeColor', 'none', 'Color', [0.5 0.5 0.5], ...
               'HorizontalAlignment', 'center');
end

% 添加时间戳
if ~isempty(timeFormat)
    time_text = text(ax, args.TimestampLocation(1), args.TimestampLocation(2), ...
                    sprintf(timeFormat, times(1)), ...
                    'Units', 'normalized', ...
                    'FontSize', args.FontSize + 2, ...
                    'FontWeight', 'bold', ...
                    'BackgroundColor', [1 1 1 0.7], ...
                    'Margin', 3);
end

% 设置视频写入器
writerObj = VideoWriter(outfile, 'MPEG-4');
writerObj.FrameRate = args.FrameRate;
writerObj.Quality = args.Quality;
open(writerObj);

% 根据条件初始化进度显示
if args.ShowProgress
    fprintf('生成热图动画: %s\n', outfile);
    progress_text = sprintf('完成: %%%.1f', 0);
    progress_bar = waitbar(0, progress_text, 'Name', 'Heatmap Animation Progress');
end

% 渲染动画帧
tic;
for frame = 1:numFrames
    % 更新热图数据
    set(img_h, 'CData', squeeze(data(frame,:,:)));
    
    % 更新时间戳
    if ~isempty(timeFormat)
        set(time_text, 'String', sprintf(timeFormat, times(frame)));
    end
    
    % 刷新图形
    drawnow;
    
    % 捕获当前帧
    frame_data = getframe(fig);
    
    % 写入帧到视频
    writeVideo(writerObj, frame_data);
    
    % 更新进度显示
    if args.ShowProgress && mod(frame, max(1, round(numFrames/100))) == 0
        progress = frame / numFrames;
        elapsed = toc;
        estimated_total = elapsed / progress;
        remaining = estimated_total - elapsed;
        
        progress_text = sprintf('完成: %.1f%% - 剩余时间: %.1f秒', progress*100, remaining);
        waitbar(progress, progress_bar, progress_text);
    end
end

% 关闭视频写入器
close(writerObj);

% 关闭进度条
if args.ShowProgress
    delete(progress_bar);
end

% 关闭图形
close(fig);

% 完成信息
if args.ShowProgress
    fprintf('热图动画已完成！\n');
    fprintf('总帧数: %d, 视频时长: %.1f秒\n', numFrames, numFrames/args.FrameRate);
    fprintf('输出文件: %s\n', outfile);
    fprintf('总耗时: %.1f秒\n', toc);
end

end

%% 带剖面的热图动画函数
function outfile = profileAnimation(data, times, varargin)
% PROFILEANIMATION 创建带剖面图的热图动画视频，适用于科研展示
%
% 用法:
%   outfile = profileAnimation(data, times)
%   outfile = profileAnimation(data, times, 'Name', Value, ...)
%
% 必需参数:
%   data  - 三维数组，维度为 [时间 x 行 x 列]
%   times - 时间点向量，长度必须与data的第一维一致
%
% 可选名称-值对参数:
%   'Title'         - 图表标题，默认：'Heatmap with Profiles'
%   'LabelX'        - X轴刻度标签，空单元格数组或数值向量，默认自动生成
%   'LabelY'        - Y轴刻度标签，空单元格数组或数值向量，默认自动生成
%   'Colormap'      - 色彩映射名称，默认：'turbo'
%   'ColorbarLabel' - 颜色条标签，默认：'Value'
%   'LimitsColor'   - 颜色范围 [min max]，默认：自动
%   'TimeFormat'    - 时间标签格式，默认：'Time: %.2f'
%   'TimeUnit'      - 时间单位，附加到时间标签，默认：''
%   'ProfileRow'    - 水平剖面行索引，默认：中间行
%   'ProfileCol'    - 垂直剖面列索引，默认：中间列
%   'ProfileColorX' - 水平剖面线颜色，默认：[0 0.447 0.741]
%   'ProfileColorY' - 垂直剖面线颜色，默认：[0.85 0.325 0.098]
%   'ProfileLineWidth' - 剖面线宽度，默认：2
%   'AspectRatio'   - 热图纵横比例，可选：'equal', 'auto'，默认：'equal'
%   'Interpolation' - 插值方法，可选：'none','bilinear'等，默认：'bilinear'
%   'Filename'      - 输出文件名，默认：'profile_animation.mp4'
%   'Directory'     - 输出目录，默认：'./animations'
%   'Resolution'    - 分辨率 [宽 高]，默认：[1920 1080]
%   'FrameRate'     - 帧率，默认：30
%   'Quality'       - 视频质量 (1-100)，默认：95
%   'FontName'      - 字体名称，默认：'Arial'
%   'FontSize'      - 基础字体大小，默认：12
%   'FontWeight'    - 字体粗细，默认：'normal'
%   'GridLines'     - 逻辑值，是否显示网格线，默认：false
%   'GridColor'     - 网格颜色，默认：[0.15 0.15 0.15]
%   'BackgroundColor' - 背景颜色，默认：[1 1 1]
%   'WatermarkText' - 水印文本，默认：''
%   'TimestampLocation' - 时间戳位置 [x y]，默认：[0.05 0.92]
%   'ReverseY'      - 逻辑值，是否反转Y轴，默认：false
%   'ShowProgress'  - 逻辑值，是否显示进度条，默认：true
%
% 返回值:
%   outfile - 生成的视频文件完整路径
%
% 示例:
%   % 创建带剖面的热图动画:
%   [X,Y] = meshgrid(-3:0.15:3);
%   frames = 60;
%   z = zeros(frames, size(X,1), size(X,2));
%   t = linspace(0, 4*pi, frames);
%   for i = 1:frames
%       z(i,:,:) = peaks(X,Y) * sin(t(i)/2) * cos(t(i)/4);
%   end
%   profileAnimation(z, t, 'Title', '热点追踪', ...
%                   'ColorbarLabel', '强度', ...
%                   'TimeUnit', 's', 'GridLines', true, ...
%                   'ProfileRow', 20, 'ProfileCol', 25);

% 输入参数解析
p = inputParser;
p.FunctionName = 'profileAnimation';
p.KeepUnmatched = false;
p.CaseSensitive = false;

addRequired(p, 'data', @(x) validateattributes(x, {'numeric'}, {'3d'}));
addRequired(p, 'times', @(x) validateattributes(x, {'numeric'}, {'vector'}));

% 内容参数
addParameter(p, 'Title', 'Heatmap with Profiles', @ischar);
addParameter(p, 'LabelX', {}, @(x) isempty(x) || iscell(x) || isnumeric(x));
addParameter(p, 'LabelY', {}, @(x) isempty(x) || iscell(x) || isnumeric(x));
addParameter(p, 'Colormap', 'turbo', @ischar);
addParameter(p, 'ColorbarLabel', 'Value', @ischar);
addParameter(p, 'LimitsColor', [], @(x) isempty(x) || (isnumeric(x) && numel(x)==2));
addParameter(p, 'TimeFormat', 'Time: %.2f', @ischar);
addParameter(p, 'TimeUnit', '', @ischar);
addParameter(p, 'ProfileRow', [], @(x) isempty(x) || (isnumeric(x) && isscalar(x) && x > 0));
addParameter(p, 'ProfileCol', [], @(x) isempty(x) || (isnumeric(x) && isscalar(x) && x > 0));
addParameter(p, 'ProfileColorX', [0 0.447 0.741], @(x) isnumeric(x) && numel(x)==3);
addParameter(p, 'ProfileColorY', [0.85 0.325 0.098], @(x) isnumeric(x) && numel(x)==3);
addParameter(p, 'ProfileLineWidth', 2, @(x) isnumeric(x) && isscalar(x) && x > 0);
addParameter(p, 'AspectRatio', 'equal', @(x) ismember(x, {'equal', 'auto'}));
addParameter(p, 'Interpolation', 'bilinear', @ischar);

% 输出参数
addParameter(p, 'Filename', 'profile_animation.mp4', @ischar);
addParameter(p, 'Directory', './animations', @ischar);
addParameter(p, 'Resolution', [1920 1080], @(x) isnumeric(x) && numel(x)==2);
addParameter(p, 'FrameRate', 30, @(x) isnumeric(x) && isscalar(x) && x>0);
addParameter(p, 'Quality', 95, @(x) isnumeric(x) && isscalar(x) && x>=1 && x<=100);

% 样式参数
addParameter(p, 'FontName', 'Arial', @ischar);
addParameter(p, 'FontSize', 12, @(x) isnumeric(x) && isscalar(x) && x>0);
addParameter(p, 'FontWeight', 'normal', @ischar);
addParameter(p, 'GridLines', false, @islogical);
addParameter(p, 'GridColor', [0.15 0.15 0.15], @(x) isnumeric(x) && numel(x)==3);
addParameter(p, 'BackgroundColor', [1 1 1], @(x) isnumeric(x) && numel(x)==3);
addParameter(p, 'WatermarkText', '', @ischar);
addParameter(p, 'TimestampLocation', [0.05 0.92], @(x) isnumeric(x) && numel(x)==2);
addParameter(p, 'ReverseY', false, @islogical);
addParameter(p, 'ShowProgress', true, @islogical);

parse(p, data, times, varargin{:});
args = p.Results;

% 检查时间维度
[numFrames, numRows, numCols] = size(data);
if length(times) ~= numFrames
    error('时间向量长度必须与数据第一维相同。');
end

% 预处理时间标签格式
if ~isempty(args.TimeUnit)
    timeFormat = [args.TimeFormat ' ' args.TimeUnit];
else
    timeFormat = args.TimeFormat;
end

% 创建输出目录
if ~exist(args.Directory, 'dir')
    mkdir(args.Directory);
end
outfile = fullfile(args.Directory, args.Filename);

% 确定颜色范围
if isempty(args.LimitsColor)
    colorMin = min(data(:));
    colorMax = max(data(:));
    % 稍微扩展范围以提高视觉效果
    colorRange = colorMax - colorMin;
    colorLimits = [colorMin - 0.02*colorRange, colorMax + 0.02*colorRange];
else
    colorLimits = args.LimitsColor;
end

% 设置剖面位置
if isempty(args.ProfileRow)
    profileRow = floor(numRows / 2);
else
    profileRow = max(1, min(args.ProfileRow, numRows));
end

if isempty(args.ProfileCol)
    profileCol = floor(numCols / 2);
else
    profileCol = max(1, min(args.ProfileCol, numCols));
end

% 创建图形和坐标轴布局
fig = figure('Position', [50 50 args.Resolution], ...
             'Color', args.BackgroundColor, ...
             'InvertHardcopy', 'off');

% 创建子图布局（2x2网格，不均等大小）
% 主热图
ax_heatmap = subplot(4, 4, [5 6 7 9 10 11 13 14 15]);
% 顶部剖面图（与主热图共享X轴）
ax_top = subplot(4, 4, [1 2 3]);
% 右侧剖面图（与主热图共享Y轴）
ax_right = subplot(4, 4, [8 12 16]);

% 设置默认轴标签
if isempty(args.LabelX)
    % 默认X轴标签
    labelX = cellstr(string(1:numCols));
else
    if isnumeric(args.LabelX)
        labelX = cellstr(string(args.LabelX));
    else
        labelX = args.LabelX;
    end
end

if isempty(args.LabelY)
    % 默认Y轴标签
    labelY = cellstr(string(1:numRows));
else
    if isnumeric(args.LabelY)
        labelY = cellstr(string(args.LabelY));
    else
        labelY = args.LabelY;
    end
end

% 应用标签到主热图轴
if numel(labelX) > 10
    % 如果标签过多，只显示部分以避免拥挤
    step = floor(numel(labelX) / 5);
    ticksX = 1:step:numCols;
    set(ax_heatmap, 'XTick', ticksX);
    set(ax_heatmap, 'XTickLabel', labelX(ticksX));
else
    set(ax_heatmap, 'XTick', 1:numCols);
    set(ax_heatmap, 'XTickLabel', labelX);
end

if numel(labelY) > 10
    % 如果标签过多，只显示部分以避免拥挤
    step = floor(numel(labelY) / 5);
    ticksY = 1:step:numRows;
    set(ax_heatmap, 'YTick', ticksY);
    set(ax_heatmap, 'YTickLabel', labelY(ticksY));
else
    set(ax_heatmap, 'YTick', 1:numRows);
    set(ax_heatmap, 'YTickLabel', labelY);
end

% 初始化热图
axes(ax_heatmap);
img_h = imagesc(1:numCols, 1:numRows, squeeze(data(1,:,:)));
if strcmp(args.AspectRatio, 'equal')
    axis(ax_heatmap, 'equal');
else
    axis(ax_heatmap, 'normal');
end
axis(ax_heatmap, 'tight');

% 是否反转Y轴
if args.ReverseY
    set(ax_heatmap, 'YDir', 'reverse');
end

% 设置颜色映射
colormap(ax_heatmap, args.Colormap);

% 设置颜色范围
caxis(ax_heatmap, colorLimits);

% 设置颜色条
colorbar_h = colorbar(ax_heatmap);
colorbar_h.Label.String = args.ColorbarLabel;
colorbar_h.Label.FontSize = args.FontSize + 1;
colorbar_h.Label.FontWeight = 'bold';

% 设置热图标签
xlabel(ax_heatmap, 'Column', 'FontSize', args.FontSize + 1, 'FontWeight', 'bold');
ylabel(ax_heatmap, 'Row', 'FontSize', args.FontSize + 1, 'FontWeight', 'bold');

% 设置热图网格
if args.GridLines
    grid(ax_heatmap, 'on');
    set(ax_heatmap, 'GridColor', args.GridColor);
    set(ax_heatmap, 'GridAlpha', 0.3);
else
    grid(ax_heatmap, 'off');
end

% 设置插值方法
set(img_h, 'Interpolation', args.Interpolation);

% 在热图上绘制剖面线
hold(ax_heatmap, 'on');
h_line = plot(ax_heatmap, [1, numCols], [profileRow, profileRow], ...
              'Color', args.ProfileColorX, 'LineWidth', args.ProfileLineWidth, 'LineStyle', '-');
v_line = plot(ax_heatmap, [profileCol, profileCol], [1, numRows], ...
              'Color', args.ProfileColorY, 'LineWidth', args.ProfileLineWidth, 'LineStyle', '-');
hold(ax_heatmap, 'off');

% 初始化顶部剖面图
axes(ax_top);
p_top = plot(1:numCols, squeeze(data(1, profileRow, :)), ...
             'Color', args.ProfileColorX, 'LineWidth', args.ProfileLineWidth);
xlim(ax_top, [1, numCols]);
ylim(ax_top, colorLimits);
title(ax_top, ['Row ' num2str(profileRow) ' Profile'], 'FontSize', args.FontSize);
grid(ax_top, 'on');
set(ax_top, 'XTick', []);  % 隐藏X轴刻度

% 初始化右侧剖面图
axes(ax_right);
p_right = plot(squeeze(data(1, :, profileCol)), 1:numRows, ...
               'Color', args.ProfileColorY, 'LineWidth', args.ProfileLineWidth);
xlim(ax_right, colorLimits);
ylim(ax_right, [1, numRows]);
title(ax_right, ['Column ' num2str(profileCol) ' Profile'], 'FontSize', args.FontSize);
grid(ax_right, 'on');
set(ax_right, 'YTick', []);  % 隐藏Y轴刻度

% 设置全图字体
set(findall(fig, '-property', 'FontName'), 'FontName', args.FontName);
set(findall(fig, '-property', 'FontSize'), 'FontSize', args.FontSize);

% 添加主标题
sgtitle(args.Title, 'FontSize', args.FontSize + 4, 'FontWeight', 'bold');

% 添加水印
if ~isempty(args.WatermarkText)
    annotation('textbox', [0.5, 0.01, 0, 0], 'String', args.WatermarkText, ...
               'FontSize', args.FontSize - 2, 'FontName', args.FontName, ...
               'EdgeColor', 'none', 'Color', [0.5 0.5 0.5], ...
               'HorizontalAlignment', 'center');
end

% 添加时间戳
axes(ax_heatmap);
if ~isempty(timeFormat)
    time_text = text(args.TimestampLocation(1), args.TimestampLocation(2), ...
                    sprintf(timeFormat, times(1)), ...
                    'Units', 'normalized', ...
                    'FontSize', args.FontSize + 2, ...
                    'FontWeight', 'bold', ...
                    'BackgroundColor', [1 1 1 0.7], ...
                    'Margin', 3);
end

% 添加剖面位置说明
annotation('textbox', [0.3, 0.01, 0.4, 0.03], ...
           'String', sprintf('剖面位置: 行 %d, 列 %d', profileRow, profileCol), ...
           'FontSize', args.FontSize, 'FontName', args.FontName, ...
           'EdgeColor', 'none', 'BackgroundColor', [0.95 0.95 0.95], ...
           'HorizontalAlignment', 'center');

% 设置视频写入器
writerObj = VideoWriter(outfile, 'MPEG-4');
writerObj.FrameRate = args.FrameRate;
writerObj.Quality = args.Quality;
open(writerObj);

% 根据条件初始化进度显示
if args.ShowProgress
    fprintf('生成带剖面的热图动画: %s\n', outfile);
    progress_text = sprintf('完成: %%%.1f', 0);
    progress_bar = waitbar(0, progress_text, 'Name', 'Profile Animation Progress');
end

% 渲染动画帧
tic;
for frame = 1:numFrames
    % 更新热图数据
    set(img_h, 'CData', squeeze(data(frame,:,:)));
    
    % 更新顶部剖面数据
    set(p_top, 'YData', squeeze(data(frame, profileRow, :)));
    
    % 更新右侧剖面数据
    set(p_right, 'XData', squeeze(data(frame, :, profileCol)));
    
    % 更新时间戳
    if ~isempty(timeFormat)
        set(time_text, 'String', sprintf(timeFormat, times(frame)));
    end
    
    % 刷新图形
    drawnow;
    
    % 捕获当前帧
    frame_data = getframe(fig);
    
    % 写入帧到视频
    writeVideo(writerObj, frame_data);
    
    % 更新进度显示
    if args.ShowProgress && mod(frame, max(1, round(numFrames/100))) == 0
        progress = frame / numFrames;
        elapsed = toc;
        estimated_total = elapsed / progress;
        remaining = estimated_total - elapsed;
        
        progress_text = sprintf('完成: %.1f%% - 剩余时间: %.1f秒', progress*100, remaining);
        waitbar(progress, progress_bar, progress_text);
    end
end

% 关闭视频写入器
close(writerObj);

% 关闭进度条
if args.ShowProgress
    delete(progress_bar);
end

% 关闭图形
close(fig);

% 完成信息
if args.ShowProgress
    fprintf('带剖面的热图动画已完成！\n');
    fprintf('总帧数: %d, 视频时长: %.1f秒\n', numFrames, numFrames/args.FrameRate);
    fprintf('输出文件: %s\n', outfile);
    fprintf('总耗时: %.1f秒\n', toc);
end

end