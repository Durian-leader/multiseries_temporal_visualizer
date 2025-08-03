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
% 
% 使用降采样后的数据创建3D表面动画，并传入自动计算的Z轴限制和时间点信息
% 使用自定义图窗大小
create_3d_surf_video(grid_data, 'ZLimits', [zlim_min, zlim_max], 'ViewAngles', [-45, 45],'TimePoints', time_points, 'TimeUnit', 's', 'FigureSize', [1000, 800], 'Colormap','turbo', 'ShowVg', true);












