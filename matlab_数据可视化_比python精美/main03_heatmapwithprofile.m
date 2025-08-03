% 加载数据
data = load('my_processed_data.mat');
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
    % 如果需要，也可以尝试其他降采样方法
    % % 方法2: 如果希望使用平均值进行降采样，取消下面的注释并注释掉方法1
    % 
    % % 将帧数分成target_frames组，计算每组的平均值
    % group_size = floor(num_frames / target_frames);
    % downsampled_grid_data = zeros(target_frames, num_rows, num_cols);
    % downsampled_time_points = zeros(target_frames, 1);
    % for i = 1:target_frames
    %     start_idx = (i-1) * group_size + 1;
    %     end_idx = min(i * group_size, num_frames);
    %     % 计算每组的平均值
    %     downsampled_grid_data(i, :, :) = mean(original_grid_data(start_idx:end_idx, :, :), 1);
    %     downsampled_time_points(i) = mean(original_time_points(start_idx:end_idx));
    % end
    
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
fprintf('数据范围: 最小值 = %.4f, 最大值 = %.4f\n', min_val, max_val);
% 使用计算出的最大最小值作为Z轴限制
% 可以选择对范围稍微扩大一点，使图像更美观
padding = 0.05 * (max_val - min_val); % 增加5%的边距
zlim_min = min_val - padding;
zlim_max = max_val + padding;





%%
% 获取数据尺寸
data = grid_data;
[numFrames, height, width] = size(data);
timepoints = time_points;

% 检查输入
if length(timepoints) ~= numFrames
    error('timepoints向量长度必须与数据第一维大小相匹配');
end

% 创建视频对象
videoFileName = 'heatmap_with_profiles1.mp4';
videoObj = VideoWriter(videoFileName, 'MPEG-4');
videoObj.FrameRate = 10; % 可以根据需要调整帧率
videoObj.Quality = 100; % 可以根据需要调整质量 (0-100)
open(videoObj);

% 计算整个数据的最小值和最大值，用于固定颜色比例
minVal = min(data(:));
maxVal = max(data(:));

% 创建自定义行列标签
colLabels = 1:6;
rowLabels = 2:5;

% 选择要显示剖视图的行和列
% 如果没有指定，则选择中间行和中间列
profile_row = 3;    % 默认选择第3行进行剖视图展示
profile_col = 3;    % 默认选择第3列进行剖视图展示

% Vg电压波形参数设置
vg_config.window_length = 1;    % 显示的时间窗口长度(秒)
vg_config.top_voltage = 5;       % 顶部电压(V)
vg_config.bottom_voltage = -5;   % 底部电压(V)
vg_config.top_time = 0.1515151515;          % 顶部持续时间(秒)
vg_config.bottom_time = 0.1515151515;       % 底部持续时间(秒)
vg_config.period = vg_config.top_time + vg_config.bottom_time;  % 周期
vg_config.stop_time = 8.9454;       % 电压停止时间点(秒)，之后电压为0

% 生成Vg电压波形函数
generate_vg_waveform = @(t) (t <= vg_config.stop_time) .* ...
    (vg_config.bottom_voltage + ...
    (vg_config.top_voltage - vg_config.bottom_voltage) * ...
    (mod(t, vg_config.period) < vg_config.top_time));

% 创建一个图形窗口，设置较大的尺寸以匹配Python版本的布局
fig = figure('Position', [100, 100, 1400, 1000], 'Color', 'w');

% 创建子图布局 - 使用类似Python GridSpec的布局
% 使用相对位置创建具有特定宽高比的子图
% [left bottom width height]

% 主热图位置 - 左下
heatmap_pos = [0.1, 0.1, 0.6, 0.6];

% 顶部剖面图位置 - 与主热图对齐
top_profile_pos = [0.1, 0.75, 0.6, 0.15];

% 右侧剖面图位置 - 与主热图对齐，保持原始大小
right_profile_pos = [0.75, 0.1, 0.15, 0.6];

% Vg电压波形图位置 - 右上角，进一步缩小高度避免文字重叠
vg_waveform_pos = [0.75, 0.78, 0.15, 0.12];

% 对每个时间点绘制热图并保存到视频
for i = 1:numFrames
    % 清除图形，保持图形窗口
    clf;
    
    % 主热图
    ax_heatmap = axes('Position', heatmap_pos);
    
    % 提取当前时间点的数据矩阵
    currentFrame = squeeze(data(i, :, :));
    
    % 绘制热图，使用双线性插值使热图看起来更平滑
    h_img = imagesc(colLabels, rowLabels, currentFrame);
    set(h_img, 'Interpolation', 'bilinear'); % 添加插值使热图更平滑
    
    % 设置坐标轴方向，使左下角为原点
    axis xy;
    
    % 设置颜色比例一致
    caxis([minVal maxVal]);
    
    % 添加彩色条 - 水平放置在热图下方
    colorbar_h = colorbar('Location', 'southoutside', 'FontSize', 10);
    colorbar_h.Label.String = 'Swelling (m)';
    colormap('turbo');  % 自定义 colormap
    
    % 设置坐标轴标签
    xlabel('Column', 'FontSize', 12);
    ylabel('Row', 'FontSize', 12);
    
    % 设置刻度为整数
    ax_heatmap.XTick = colLabels;
    ax_heatmap.YTick = rowLabels;
    
    % 添加剖面参考线到热图
    hold on;
    h_line = plot(colLabels, ones(size(colLabels))*profile_row, 'b-', 'LineWidth', 1.5);
    v_line = plot(ones(size(rowLabels))*profile_col, rowLabels, 'r-', 'LineWidth', 1.5);
    hold off;
    
    % 顶部剖面图（固定行，所有列）
    ax_top = axes('Position', top_profile_pos);
    profile_row_data = currentFrame(profile_row-rowLabels(1)+1, :);
    plot(colLabels, profile_row_data, 'b-', 'LineWidth', 2, 'Marker', 'o', 'MarkerFaceColor', 'b', 'MarkerSize', 4);
    title(['Row ', num2str(profile_row), ' Profile'], 'FontSize', 12);
    ylim([minVal maxVal]);
    xlim([min(colLabels), max(colLabels)]);
    set(ax_top, 'XTickLabel', []);  % 隐藏X轴刻度标签
    grid on;
    
    % 右侧剖面图（所有行，固定列）
    ax_right = axes('Position', right_profile_pos);
    profile_col_data = currentFrame(:, profile_col-colLabels(1)+1);
    plot(profile_col_data, rowLabels, 'r-', 'LineWidth', 2, 'Marker', 'o', 'MarkerFaceColor', 'r', 'MarkerSize', 4);
    title(['Column ', num2str(profile_col), ' Profile'], 'FontSize', 12);
    xlim([minVal maxVal]);
    ylim([min(rowLabels), max(rowLabels)]);
    set(ax_right, 'YTickLabel', []);  % 隐藏Y轴刻度标签
    grid on;
    
    % Vg电压波形图 - 右上角
    ax_vg = axes('Position', vg_waveform_pos);
    
    % 当前时间
    current_time = timepoints(i);
    
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
    
    % 添加总标题
    sgtitle(['Heatmap with Signal Profiles - Time: ', num2str(timepoints(i)), ' sec'], 'FontSize', 16, 'FontWeight', 'bold');
    
    % % 添加时间戳文本框 - 类似Python版本的黑底白字
    % timestamp_str = ['Time: ', num2str(timepoints(i), '%.4f')];
    % text(ax_heatmap, 0.02, 0.95, timestamp_str, 'Units', 'normalized', ...
    %      'FontSize', 12, 'Color', 'white', 'FontWeight', 'bold', ...
    %      'BackgroundColor', [0 0 0 0.5], 'Margin', 5);
    
    % 添加交互说明
    annotation('textbox', [0.3, 0.01, 0.4, 0.03], 'String', 'Showing profiles for fixed middle row and column', ...
               'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle', ...
               'FontSize', 10, 'EdgeColor', 'none', 'BackgroundColor', [1 1 1 0.7]);
    
    % 调整图形整体外观
    set(fig, 'Color', 'white');
    
    % 捕获当前帧并写入视频对象
    frame = getframe(fig);
    writeVideo(videoObj, frame);
    
    % 显示进度信息
    if mod(i, 10) == 0 || i == 1 || i == numFrames
        disp(['处理帧 ', num2str(i), ' / ', num2str(numFrames)]);
    end
end

% 关闭视频对象
close(videoObj);

% 显示视频的一些基本信息
videoInfo = VideoReader(videoFileName);
disp(['视频已成功导出为: ', videoFileName]);
disp(['视频帧率: ', num2str(videoInfo.FrameRate), ' fps']);
disp(['视频时长: ', num2str(videoInfo.Duration), ' 秒']);
disp(['视频分辨率: ', num2str(videoInfo.Width), 'x', num2str(videoInfo.Height)]);