% 加载数据
data = load('data.mat');
% 获取原始grid_data和时间点
original_grid_data = data.grid_data;
original_time_points = data.time_points;
% 获取原始形状
[num_frames, num_rows, num_cols] = size(original_grid_data);
fprintf('原始数据: %d 帧, %d 行, %d 列\n', num_frames, num_rows, num_cols);
% 设置目标帧数
target_frames = 500; % 设置你想要的帧数
% 如果原始帧数大于目标帧数，则进行降采样
if num_frames > target_frames
    % 方法1: 简单的等距离抽样
    downsample_indices = round(linspace(1, num_frames, target_frames));
    downsampled_grid_data = original_grid_data(downsample_indices, :, :);
    downsampled_time_points = original_time_points(downsample_indices);
    % 显示降采样后的信息
    fprintf('降采样后: %d 帧, %d 行, %d 列\n', size(downsampled_grid_data, 1), num_rows, num_cols);
    
    % 使用降采样后的数据
    grid_data = downsampled_grid_data;
    time_points = downsampled_time_points;
else
    % 如果帧数已经小于或等于目标帧数，就不需要降采样
    fprintf('原始帧数 (%d) 已经小于或等于目标帧数 (%d)，不需要降采样\n', num_frames, target_frames);
    grid_data = original_grid_data;
    time_points = original_time_points;
end
% 计算整个数据集的最大值和最小值
min_val = min(grid_data(:));
max_val = max(grid_data(:));
fprintf('数据范围: 最小值 = %.6f, 最大值 = %.6f\n', min_val, max_val);
% 使用计算出的最大最小值作为Z轴限制
% 可以选择对范围稍微扩大一点，使图像更美观
padding = 0.05 * (max_val - min_val); % 增加5%的边距
zlim_min = min_val - padding;
zlim_max = max_val + padding;
% 生成带时间戳的文件名
timestamp = datestr(now, 'yyyymmdd_HHMMSS');
filename = sprintf('3d_surface_animation_%s.mp4', timestamp);
fprintf('输出文件名: %s\n', filename);

% 加载电流数据
current_file = 'Current/3.3Hz.csv';
fprintf('加载电流数据: %s\n', current_file);
current_data = readtable(current_file);
current_time_data = current_data.Time;
current_values = current_data.id;
fprintf('电流数据: %d 个时间点，时间范围 %.6f - %.6f 秒\n', length(current_time_data), min(current_time_data), max(current_time_data));

% 使用降采样后的数据创建3D表面动画，并传入自动计算的Z轴限制和时间点信息
% 使用自定义图窗大小，并传递电流数据
create_3d_surf_video(grid_data, 'FileName', filename,'ZLimits', [zlim_min, zlim_max], 'ViewAngles', [-45, 45],'TimePoints', time_points, 'TimeUnit', 's', 'FigureSize', [1000, 800], 'Colormap','turbo', 'ShowVg', true, 'ShowCurrent', true, 'CurrentTime', current_time_data, 'CurrentValues', current_values, 'UseGeneratedVg', false, 'CurrentFile', current_file, 'VgYTicks', [-0.3,0, 0.6]);












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
%   'VgConfig'      - Vg电压参数结构体，包含window_length, top_voltage, bottom_voltage, top_time, bottom_time, stop_time
%   'CurrentTime'   - 电流数据的时间轴数组
%   'CurrentValues' - 电流数据的值数组
%   'ShowCurrent'   - 是否显示电流波形，默认为 true
%   'UseGeneratedVg' - 是否使用生成的Vg波形，默认为 false（true时使用生成的Vg，false时使用CSV中的实测Vg）
%   'CurrentFile'   - CSV文件路径，用于读取实测Vg数据，默认为空
%   'VgYTicks'      - 自定义Vg电压Y轴刻度数组，默认为 [-0.3, 0.6]

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
defaultVgConfig.stop_time = 8.9454;
defaultCurrentTime = [];
defaultCurrentValues = [];
defaultShowCurrent = true;
defaultUseGeneratedVg = false;  % true: 使用生成的Vg波形, false: 使用CSV中的实测Vg
defaultCurrentFile = '';  % CSV文件路径
defaultVgYTicks = [-0.3, 0.6];  % 自定义Vg电压刻度

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
addParameter(p, 'CurrentTime', defaultCurrentTime);
addParameter(p, 'CurrentValues', defaultCurrentValues);
addParameter(p, 'ShowCurrent', defaultShowCurrent, @islogical);
addParameter(p, 'UseGeneratedVg', defaultUseGeneratedVg, @islogical);
addParameter(p, 'CurrentFile', defaultCurrentFile, @ischar);
addParameter(p, 'VgYTicks', defaultVgYTicks, @isnumeric);

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
fig = figure('Position', [100, 100, args.FigureSize(1), args.FigureSize(2)], 'Color', 'white', ...
            'PaperPosition', [0 0 args.FigureSize(1)/100 args.FigureSize(2)/100], ...
            'PaperSize', [args.FigureSize(1)/100 args.FigureSize(2)/100]);
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
    timeFormat = sprintf('Time: %%.6f %s', args.TimeUnit);
else
    timeFormat = 'Time: %.6f';
end

% 生成Vg电压波形函数（如果需要显示Vg）
if args.ShowVg
    vg_config = args.VgConfig;
    generate_vg_waveform = @(t) (t <= vg_config.stop_time) .* ...
        (vg_config.bottom_voltage + ...
        (vg_config.top_voltage - vg_config.bottom_voltage) * ...
        (mod(t, vg_config.period) < vg_config.top_time));
end

% 准备电流数据和Vg数据（如果需要显示电流）
if args.ShowCurrent && ~isempty(args.CurrentTime) && ~isempty(args.CurrentValues)
    original_current_time = args.CurrentTime;
    original_current_values = args.CurrentValues;
    
    % 检查是否需要扩展电流数据到实验结束时间
    max_experiment_time = max(timePoints);
    max_current_time = max(original_current_time);
    
    if max_current_time < max_experiment_time
        % 需要扩展：在末尾添加零值
        fprintf('电流数据时间范围不够，从 %.6f 秒扩展到 %.6f 秒\n', max_current_time, max_experiment_time);
        
        % 创建扩展的时间点（从电流数据结束时间到实验结束时间）
        time_step = median(diff(original_current_time)); % 使用原始采样间隔
        extended_time = (max_current_time + time_step):time_step:max_experiment_time;
        
        % 合并原始数据和扩展数据
        current_time_data = [original_current_time; extended_time'];
        current_values_data = [original_current_values; zeros(length(extended_time), 1)];
        
        fprintf('扩展后电流数据: 时间范围 %.6f - %.6f 秒，共 %d 个数据点（原始 %d + 扩展 %d）\n', ...
            min(current_time_data), max(current_time_data), length(current_time_data), ...
            length(original_current_time), length(extended_time));
    else
        % 不需要扩展
        current_time_data = original_current_time;
        current_values_data = original_current_values;
        fprintf('电流数据准备完成，时间范围: %.6f - %.6f 秒，共 %d 个数据点\n', min(current_time_data), max(current_time_data), length(current_time_data));
    end
    
    % 如果不使用生成的Vg波形，则从CSV数据中提取实测Vg
    if ~args.UseGeneratedVg
        % 从CSV文件中读取Vg数据（第三列是vg）
        try
            % 使用传入的CurrentFile参数
            if ~isempty(args.CurrentFile) && exist(args.CurrentFile, 'file')
                csv_data = readtable(args.CurrentFile);
                num_cols = size(csv_data, 2);  % 使用size替代width函数
                if num_cols >= 3 && ismember('vg', csv_data.Properties.VariableNames)
                    original_vg_values = csv_data.vg;
                    fprintf('已从CSV文件 %s 中提取实测Vg数据\n', args.CurrentFile);
                    
                    % 同样需要扩展Vg数据
                    if max_current_time < max_experiment_time
                        % Vg在电流数据结束后保持为0
                        vg_values_data = [original_vg_values; zeros(length(extended_time), 1)];
                    else
                        vg_values_data = original_vg_values;
                    end
                    
                    fprintf('Vg数据范围: %.6f - %.6f V\n', min(vg_values_data), max(vg_values_data));
                else
                    fprintf('警告: CSV文件中未找到vg列，将使用生成的Vg波形\n');
                    args.UseGeneratedVg = true;  % 回退到生成的Vg
                end
            else
                fprintf('警告: CSV文件路径无效 (%s)，将使用生成的Vg波形\n', args.CurrentFile);
                args.UseGeneratedVg = true;  % 回退到生成的Vg
            end
        catch ME
            fprintf('警告: 无法读取CSV中的Vg数据 (%s)，将使用生成的Vg波形\n', ME.message);
            args.UseGeneratedVg = true;  % 回退到生成的Vg
        end
    end
end


% 创建动画
fprintf('开始创建视频，共 %d 帧...\n', numFrames);

for frame = 1:numFrames
    % 清除图形
    clf;
    
    % 根据显示需求确定布局
    show_side_plots = args.ShowVg || (args.ShowCurrent && ~isempty(args.CurrentTime));
    
    if show_side_plots
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
    
    % 添加侧边子图
    if show_side_plots
        current_time = timePoints(frame);
        
        % 如果显示Vg波形，添加Vg子图（上方）
        if args.ShowVg
            % Vg电压波形图 - 右上方
            ax_vg = subplot('Position', [0.8, 0.6, 0.15, 0.25]);
            
            % 计算时间窗口 - 当前时间在窗口中心，但不能小于0
            window_start = max(0, current_time - vg_config.window_length / 2);
            window_end = current_time + vg_config.window_length / 2;
            
            if args.UseGeneratedVg
                % 使用生成的Vg波形
                current_voltage = generate_vg_waveform(current_time);
                
                % 只有当窗口开始时间小于当前时间时才绘制历史波形
                if window_start < current_time
                    % 生成时间向量和对应的电压值（过去部分）
                    past_time_vec = linspace(window_start, current_time, 200);
                    past_voltage_vec = arrayfun(generate_vg_waveform, past_time_vec);
                    
                    % 绘制过去的波形（蓝色实线）
                    plot(past_time_vec - current_time, past_voltage_vec, 'b-', 'LineWidth', 2);
                    hold on;
                end
                
                % 绘制当前时间点（红色圆点，在x轴中心位置）
                plot(0, current_voltage, 'ro', 'MarkerSize', 8, 'MarkerFaceColor', 'r');
            else
                % 使用CSV中的实测Vg数据
                if exist('vg_values_data', 'var') && exist('current_time_data', 'var')
                    % 找出窗口内的Vg数据点
                    vg_mask = (current_time_data <= current_time) & (current_time_data >= window_start);
                    
                    if any(vg_mask)
                        % 获取符合条件的Vg数据点
                        display_vg_time = current_time_data(vg_mask);
                        display_vg_values = vg_values_data(vg_mask);
                        
                        % 绘制历史Vg曲线（蓝色实线）
                        plot(display_vg_time - current_time, display_vg_values, 'b-', 'LineWidth', 2);
                        hold on;
                        
                        % 在最新的数据点上标记（红色圆点）
                        if ~isempty(display_vg_values)
                            latest_vg_time = display_vg_time(end);
                            latest_vg_value = display_vg_values(end);
                            plot(latest_vg_time - current_time, latest_vg_value, 'ro', 'MarkerSize', 8, 'MarkerFaceColor', 'r');
                        end
                    end
                else
                    % 回退到生成的Vg
                    current_voltage = generate_vg_waveform(current_time);
                    plot(0, current_voltage, 'ro', 'MarkerSize', 8, 'MarkerFaceColor', 'r');
                end
            end
            
            % 设置坐标轴
            xlim([-vg_config.window_length/2, vg_config.window_length/2]);
            
            % 根据Vg数据源设置y轴
            if args.UseGeneratedVg
                ylim([vg_config.bottom_voltage - 0.5, vg_config.top_voltage + 0.5]);
                % 设置y轴刻度为顶部和底部电压
                yticks([vg_config.bottom_voltage, vg_config.top_voltage]);
                yticklabels({[num2str(vg_config.bottom_voltage), 'V'], [num2str(vg_config.top_voltage), 'V']});
            else
                % 使用实测Vg数据时，使用自定义刻度
                if exist('vg_values_data', 'var') && ~isempty(vg_values_data)
                    % 根据自定义刻度设置y轴范围
                    tick_range = [min(args.VgYTicks), max(args.VgYTicks)];
                    tick_padding = (tick_range(2) - tick_range(1)) * 0.1;
                    ylim([tick_range(1) - tick_padding, tick_range(2) + tick_padding]);
                    
                    % 使用自定义刻度
                    yticks(args.VgYTicks);
                    % 为刻度添加单位标签
                    tick_labels = cell(size(args.VgYTicks));
                    for i = 1:length(args.VgYTicks)
                        tick_labels{i} = [num2str(args.VgYTicks(i)), 'V'];
                    end
                    yticklabels(tick_labels);
                else
                    % 回退到默认范围
                    ylim([vg_config.bottom_voltage - 0.5, vg_config.top_voltage + 0.5]);
                    yticks([vg_config.bottom_voltage, vg_config.top_voltage]);
                    yticklabels({[num2str(vg_config.bottom_voltage), 'V'], [num2str(vg_config.top_voltage), 'V']});
                end
            end
            
            % 添加网格和标签
            grid on;
            xlabel('Rel. Time (s)', 'FontSize', 10);
            ylabel('Vg (V)', 'FontSize', 10);
            title('Drive Voltage', 'FontSize', 11, 'FontWeight', 'bold');
            
            % 设置坐标轴样式
            ax_vg.FontSize = 9;
            ax_vg.Box = 'on';
            
            hold off;
        end
        
        % 如果显示电流波形，添加电流子图（下方）
        if args.ShowCurrent && ~isempty(args.CurrentTime)
            % 确定电流子图位置（如果有Vg图则在下方，否则在中间）
            if args.ShowVg
                ax_current = subplot('Position', [0.8, 0.25, 0.15, 0.25]);
            else
                ax_current = subplot('Position', [0.8, 0.45, 0.15, 0.3]);
            end
            
            % 计算时间窗口
            if args.ShowVg
                window_length = vg_config.window_length;
            else
                window_length = 1.0;
            end
            window_start = current_time - window_length / 2;
            window_end = current_time + window_length / 2;
            
            % 找出当前时间之前且在显示窗口内的原始电流数据点
            current_mask = (current_time_data <= current_time) & (current_time_data >= window_start);
            
            if any(current_mask)
                % 获取符合条件的原始数据点
                display_time = current_time_data(current_mask);
                display_current = current_values_data(current_mask);
                
                % 绘制历史电流曲线（绿色实线），使用原始数据点
                plot(display_time - current_time, display_current, 'g-', 'LineWidth', 2);
                hold on;
                
                % 在最新的数据点上标记（红色圆点）
                if ~isempty(display_current)
                    latest_time = display_time(end);
                    latest_current = display_current(end);
                    plot(latest_time - current_time, latest_current, 'ro', 'MarkerSize', 8, 'MarkerFaceColor', 'r');
                end
            end
            
            % 设置坐标轴
            xlim([-window_length/2, window_length/2]);
            
            % 动态调整y轴范围，使用原始电流数据
            if exist('current_values_data', 'var') && ~isempty(current_values_data)
                y_range = [min(current_values_data), max(current_values_data)];
                y_padding = (y_range(2) - y_range(1)) * 0.1;
                ylim([y_range(1) - y_padding, y_range(2) + y_padding]);
            end
            
            % 添加网格和标签
            grid on;
            xlabel('Rel. Time (s)', 'FontSize', 10);
            ylabel('Current (A)', 'FontSize', 10);
            title('Drain Current', 'FontSize', 11, 'FontWeight', 'bold');
            
            % 设置坐标轴样式
            ax_current.FontSize = 9;
            ax_current.Box = 'on';
            
            % 添加科学计数法格式
            ax_current.YAxis.Exponent = -6;  % 显示为微安培
            
            hold off;
        end
    end

    % 捕获当前帧，确保尺寸正确
    frameData = getframe(fig);
    
    % 检查并调整帧尺寸
    [height, width, ~] = size(frameData.cdata);
    if height ~= args.FigureSize(2) || width ~= args.FigureSize(1)
        % 调整帧尺寸到期望大小
        frameData.cdata = imresize(frameData.cdata, [args.FigureSize(2), args.FigureSize(1)]);
    end

    % 写入视频
    writeVideo(writerObj, frameData);

    % 显示进度
    if mod(frame, 10) == 0 || frame == 1 || frame == numFrames
        fprintf('处理帧 %d/%d (%.1f%%) - 时间: %.6f\n', frame, numFrames, frame/numFrames*100, timePoints(frame));
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

