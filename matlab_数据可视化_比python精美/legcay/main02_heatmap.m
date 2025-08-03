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
timepoints=time_points;
% 检查输入
if length(timepoints) ~= numFrames
    error('timepoints向量长度必须与数据第一维大小相匹配');
end
% 创建视频对象
videoFileName = 'heatmap_video111.mp4';
videoObj = VideoWriter(videoFileName, 'MPEG-4');
videoObj.FrameRate = 10; % 可以根据需要调整帧率
videoObj.Quality = 100; % 可以根据需要调整质量 (0-100)
open(videoObj);
% 计算整个数据的最小值和最大值，用于固定颜色比例
minVal = min(data(:));
maxVal = max(data(:));
% 创建一个图形窗口
fig = figure('Position', [100, 100, 800, 600], 'Color', 'w');
% 创建自定义行列标签
% 列标签范围: 1-6
colLabels = 1:6;
% 行标签范围: 2-5
rowLabels = 2:5;
% 对每个时间点绘制热图并保存到视频
for i = 1:numFrames
    % 提取当前时间点的数据矩阵
    currentFrame = squeeze(data(i, :, :));
    % 绘制热图，使用双线性插值使热图看起来更平滑
    h = imagesc(colLabels, rowLabels, currentFrame);
    set(h, 'Interpolation', 'bilinear'); % 添加插值使热图更平滑
    % 设置坐标轴方向，使左下角对应(0,0)
    axis xy;
    % 设置颜色比例一致
    caxis([minVal maxVal]);
    % 添加彩色条
    colorbar;
    colormap('turbo');  % 自定义 colormap
    % 设置标题，显示当前时间点
    title(['时间点: ', num2str(timepoints(i)), ' 秒']);
    % 设置坐标轴标签
    xlabel('Column');
    ylabel('Row');
    % 设置刻度为整数（确保最小刻度为1，不显示小数）
    ax = gca;
    ax.XTick = colLabels;
    ax.YTick = rowLabels;
    % 调整图形外观
    set(gca, 'FontSize', 12);
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
% 关闭图形窗口
close(fig);
disp(['视频已成功导出为: ', videoFileName]);
% 显示视频的一些基本信息
videoInfo = VideoReader(videoFileName);
disp(['视频帧率: ', num2str(videoInfo.FrameRate), ' fps']);
disp(['视频时长: ', num2str(videoInfo.Duration), ' 秒']);
disp(['视频分辨率: ', num2str(videoInfo.Width), 'x', num2str(videoInfo.Height)]);