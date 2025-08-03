function create_3d_surf_video(data3D, varargin)
% CREATE_3D_SURF_VIDEO 根据三维矩阵数据创建3D表面动画视频
%
% 用法:
%   create_3d_surf_video(data3D)
%   create_3d_surf_video(data3D, 'ParameterName', ParameterValue, ...)
%
% 输入:
%   data3D - 三维矩阵，第一维是时间，第二维和第三维是行和列
%
% 可选参数:
%   'FileName'      - 输出视频文件名，默认为 'surface_animation.mp4'
%   'FrameRate'     - 帧率，默认为 30
%   'Quality'       - 视频质量 (1-100)，默认为 95
%   'Colormap'      - 颜色图，默认为 'jet'
%   'XRange'        - X轴范围，默认自动生成
%   'YRange'        - Y轴范围，默认自动生成
%   'ZLimits'       - Z轴限制，默认自动调整
%   'CLimits'       - 颜色条范围 [最小值, 最大值]，默认自动调整
%   'ViewAngles'    - 视角设置 [方位角, 仰角]，默认为 [30, 30]
%   'TimePoints'    - 时间点数组，默认为帧索引 1:numFrames
%   'TimeUnit'      - 时间单位字符串，默认为空
%   'FigureSize'    - 图窗大小 [宽, 高]，默认为 [1280, 720]
%   'ShowVg'        - 是否显示Vg电压波形，默认为 true
%   'VgConfig'      - Vg电压参数结构体，包含window_length, top_voltage, bottom_voltage, top_time, bottom_time

% 解析输入参数
p = inputParser;
defaultFileName = 'surface_animation.mp4';
defaultFrameRate = 30;
defaultQuality = 95;
defaultColormap = 'jet';
defaultXRange = [];
defaultYRange = [];
defaultZLimits = [];
defaultCLimits = []; 
defaultViewAngles = [30, 30];
defaultTimePoints = []; 
defaultTimeUnit = '';   
defaultFigureSize = [1280, 720]; % 新增：图窗大小参数
defaultShowVg = true;
defaultVgConfig.window_length = 1;
defaultVgConfig.top_voltage = 5;
defaultVgConfig.bottom_voltage = -5;
defaultVgConfig.top_time = 0.1515151515;
defaultVgConfig.bottom_time = 0.1515151515;
defaultVgConfig.period = defaultVgConfig.top_time + defaultVgConfig.bottom_time;

addRequired(p, 'data3D');
addParameter(p, 'FileName', defaultFileName, @ischar);
addParameter(p, 'FrameRate', defaultFrameRate, @isnumeric);
addParameter(p, 'Quality', defaultQuality, @isnumeric);
addParameter(p, 'Colormap', defaultColormap, @ischar);
addParameter(p, 'XRange', defaultXRange);
addParameter(p, 'YRange', defaultYRange);
addParameter(p, 'ZLimits', defaultZLimits);
addParameter(p, 'CLimits', defaultCLimits);
addParameter(p, 'ViewAngles', defaultViewAngles, @isnumeric);
addParameter(p, 'TimePoints', defaultTimePoints);
addParameter(p, 'TimeUnit', defaultTimeUnit, @ischar);
addParameter(p, 'FigureSize', defaultFigureSize, @isnumeric); % 新增：图窗大小参数
addParameter(p, 'ShowVg', defaultShowVg, @islogical);
addParameter(p, 'VgConfig', defaultVgConfig, @isstruct);

parse(p, data3D, varargin{:});
args = p.Results;

% 验证输入数据
if ndims(data3D) ~= 3
    error('输入数据必须是三维矩阵');
end

% 获取数据维度
[numFrames, numRows, numCols] = size(data3D);

% 设置时间点（如果未指定）
if isempty(args.TimePoints)
    timePoints = 1:numFrames;
else
    timePoints = args.TimePoints;
    % 确保时间点数组长度与帧数一致
    if length(timePoints) ~= numFrames
        error('TimePoints数组长度必须与帧数相同');
    end
end

% 默认将X轴设置为1-6，Y轴设置为2-5
if isempty(args.XRange)
    X = 1:numCols;
    if numCols == 6
        X = 1:6; % 列刻度为1-6
    end
else
    X = args.XRange;
end

if isempty(args.YRange)
    Y = 1:numRows;
    if numRows == 4
        Y = 2:5; % 行刻度为2-5
    end
else
    Y = args.YRange;
end

[X, Y] = meshgrid(X, Y);

% 创建图形窗口，使用自定义大小
fig = figure('Position', [100, 100, args.FigureSize(1), args.FigureSize(2)], 'Color', 'white');
% 设置视频写入器
writerObj = VideoWriter(args.FileName, 'MPEG-4');
writerObj.FrameRate = args.FrameRate;
writerObj.Quality = args.Quality;
open(writerObj);

% 确定Z轴限制（如果未指定）
if isempty(args.ZLimits)
    minZ = min(data3D(:));
    maxZ = max(data3D(:));
    zRange = maxZ - minZ;
    zLimits = [minZ - 0.1*zRange, maxZ + 0.1*zRange];
else
    zLimits = args.ZLimits;
end

% 确定颜色条范围（如果未指定）
if isempty(args.CLimits)
    minC = min(data3D(:));
    maxC = max(data3D(:));
    cLimits = [minC, maxC];
else
    cLimits = args.CLimits;
end

% 构建时间字符串格式
if ~isempty(args.TimeUnit)
    timeFormat = sprintf('Time: %%.2f %s', args.TimeUnit);
else
    timeFormat = 'Time: %.2f';
end

% 生成Vg电压波形函数（如果需要显示Vg）
if args.ShowVg
    vg_config = args.VgConfig;
    generate_vg_waveform = @(t) vg_config.bottom_voltage + ...
        (vg_config.top_voltage - vg_config.bottom_voltage) * ...
        (mod(t, vg_config.period) < vg_config.top_time);
end

% 创建动画
fprintf('开始创建视频，共 %d 帧...\n', numFrames);

for frame = 1:numFrames
    % 清除图形
    clf;
    
    % 如果显示Vg波形，创建子图布局
    if args.ShowVg
        % 主3D图 - 占据大部分空间
        ax_main = subplot('Position', [0.1, 0.15, 0.65, 0.75]);
        
        % 获取当前帧的数据
        Z = squeeze(data3D(frame, :, :));
        
        % 创建表面图
        surf(X, Y, Z);
    else
        % 获取当前帧的数据
        Z = squeeze(data3D(frame, :, :));
        
        % 创建表面图（全屏）
        surf(X, Y, Z);
    end

    % 原始 RdYlBu（红→白→蓝）
    cmap_raw = [
        165,0,38
        215,48,39
        244,109,67
        253,174,97
        254,224,144
        255,255,191
        224,243,248
        171,217,233
        116,173,209
        69,117,180
        49,54,149
    ] / 255;
    
    % 反转：蓝→白→红（即 RdYlBu_r）
    cmap = flipud(cmap_raw);
    
    % 插值成 256 色平滑渐变
    n = 256;
    x = linspace(0, 1, size(cmap, 1));
    xi = linspace(0, 1, n);
    map = interp1(x, cmap, xi, 'linear');

    % 设置视觉效果
    shading interp;
    colormap(args.Colormap);
    % colormap(map)
    lighting gouraud;

    % 设置颜色范围（固定颜色条范围）
    caxis(cLimits);

    % 添加光源
    % light('Position', [1, 1, 1], 'Style', 'infinite');

    % 设置固定视角
    view(args.ViewAngles);

    % 设置轴属性
    axis tight;
    if ~isempty(zLimits)
        zlim(zLimits);
    end

    % 确保X和Y轴刻度显示为整数
    xticks(1:max(X(:)));
    yticks(min(Y(:)):max(Y(:)));

    % 添加标题（显示时间而不是帧号）
    title(sprintf(timeFormat, timePoints(frame)), 'FontSize', 14);

    % 添加标签
    xlabel('Column', 'FontSize', 12);
    ylabel('Row', 'FontSize', 12);
    zlabel('Swelling (m)', 'FontSize', 12);

    % 添加颜色条
    colorbar;
    
    % 如果显示Vg波形，添加Vg子图
    if args.ShowVg
        % Vg电压波形图 - 右侧
        ax_vg = subplot('Position', [0.8, 0.6, 0.15, 0.3]);
        
        % 当前时间
        current_time = timePoints(frame);
        
        % 计算时间窗口 - 当前时间在窗口中心
        window_start = current_time - vg_config.window_length / 2;
        window_end = current_time + vg_config.window_length / 2;
        
        % 生成时间向量和对应的电压值（过去部分）
        past_time_vec = linspace(window_start, current_time, 200);
        past_voltage_vec = arrayfun(generate_vg_waveform, past_time_vec);
        
        % 绘制过去的波形（蓝色实线）
        plot(past_time_vec - current_time, past_voltage_vec, 'b-', 'LineWidth', 2);
        hold on;
        
        % 绘制当前时间点（红色圆点，在x轴中心位置）
        current_voltage = generate_vg_waveform(current_time);
        plot(0, current_voltage, 'ro', 'MarkerSize', 8, 'MarkerFaceColor', 'r');
        
        % 设置坐标轴
        xlim([-vg_config.window_length/2, vg_config.window_length/2]);
        ylim([vg_config.bottom_voltage - 0.5, vg_config.top_voltage + 0.5]);
        
        % 设置y轴刻度为顶部和底部电压
        yticks([vg_config.bottom_voltage, vg_config.top_voltage]);
        yticklabels({[num2str(vg_config.bottom_voltage), 'V'], [num2str(vg_config.top_voltage), 'V']});
        
        % 添加网格和标签
        grid on;
        xlabel('Rel. Time (s)', 'FontSize', 10);
        ylabel('Vg (V)', 'FontSize', 10);
        title('Drive Voltage Vg', 'FontSize', 12, 'FontWeight', 'bold');
        
        % 设置坐标轴样式
        ax_vg.FontSize = 9;
        ax_vg.Box = 'on';
        
        hold off;
    end

    % 捕获当前帧
    frameData = getframe(fig);

    % 写入视频
    writeVideo(writerObj, frameData);

    % 显示进度
    if mod(frame, 10) == 0 || frame == 1 || frame == numFrames
        fprintf('处理帧 %d/%d (%.1f%%) - 时间: %.2f\n', frame, numFrames, frame/numFrames*100, timePoints(frame));
    end
end

% 关闭视频写入器
close(writerObj);

% 关闭图形窗口
close(fig);

% 显示完成消息
fprintf('\n视频创建完成！已保存为 "%s"\n', args.FileName);

% 示例用法
if nargout == 0 && nargin == 0
    % 生成示例数据
    fprintf('未提供数据，生成示例视频...\n');
    [x, y] = meshgrid(1:6, 2:5); % 使用指定范围
    frames = 100;
    exampleData = zeros(frames, 4, 6); % 4行6列

    % 创建示例时间点（例如0到10秒）
    exampleTime = linspace(0, 10, frames);

    for t = 1:frames
        time = t/frames * 4*pi;
        for i = 1:4
            for j = 1:6
                exampleData(t, i, j) = sin(sqrt((x(i,j)-3)^2 + (y(i,j)-3)^2) + time) * exp(-0.1 * ((x(i,j)-3)^2 + (y(i,j)-3)^2));
            end
        end
    end

    % 使用示例数据调用自身，并传递时间点和自定义图窗大小
    create_3d_surf_video(exampleData, 'FileName', 'example_animation.mp4', ...
                         'TimePoints', exampleTime, 'TimeUnit', 's', ...
                         'FigureSize', [1920, 1080]);
end
end

% 示例脚本（如何使用此函数）
%{
% 方法1：生成示例数据并创建视频
[x, y] = meshgrid(1:6, 2:5);
frames = 100;
data = zeros(frames, 4, 6); % 4行6列对应2-5行和1-6列

% 创建时间点数组（例如0到5秒，100个点）
time_points = linspace(0, 5, frames);

for t = 1:frames
    time = t/frames * 4*pi;
    for i = 1:4
        for j = 1:6
            data(t, i, j) = sin(sqrt((x(i,j)-3)^2 + (y(i,j)-3)^2) + time) * exp(-0.1 * ((x(i,j)-3)^2 + (y(i,j)-3)^2));
        end
    end
end

% 设置固定的颜色条范围，传递时间点，并自定义图窗大小
create_3d_surf_video(data, 'FileName', 'my_animation.mp4', 'Colormap', 'hot', ...
                    'CLimits', [-1, 1], 'TimePoints', time_points, 'TimeUnit', 's', ...
                    'FigureSize', [1920, 1080]);

% 方法2：加载已有数据（例如从MAT文件）
% load('my_3d_data.mat'); % 加载包含'data3D'变量和'time_points'变量的MAT文件
% create_3d_surf_video(data3D, 'ZLimits', [-1, 1], 'ViewAngles', [45, 30], ...
%                     'CLimits', [0, 100], 'TimePoints', time_points, 'TimeUnit', 'ms', ...
%                     'FigureSize', [1600, 900]);
%}

