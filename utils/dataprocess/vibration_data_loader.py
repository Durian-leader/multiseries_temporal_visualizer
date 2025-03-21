import pandas as pd
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path
import matplotlib.pyplot as plt
import os
import glob
import sys
from loguru import logger

@dataclass
class VibrationDataLoader:
    """用于加载和处理振动数据文件的类"""
    metadata: Dict[str, str] = field(default_factory=dict)  # 存储元数据的字典
    data: Optional[pd.DataFrame] = None  # 存储振动数据的DataFrame
    file_path: Optional[str] = None  # 数据文件路径
    
    def __post_init__(self):
        """初始化后记录初始化信息"""
        logger.debug(f"VibrationDataLoader initialized")
        if self.file_path:
            logger.debug(f"File path set to: {self.file_path}")
    
    @classmethod
    def from_txt(cls, file_path: str) -> "VibrationDataLoader":
        """
        从文本文件读取数据并创建VibrationDataLoader对象
        
        参数:
            file_path: 包含振动数据的文本文件路径
            
        返回:
            包含加载数据和元数据的VibrationDataLoader实例
            
        异常:
            FileNotFoundError: 当指定文件不存在时抛出
            ValueError: 当文件格式无效或异常时抛出
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"找不到文件: {file_path}")
        
        logger.info(f"开始加载文件: {file_path}")
        logger.debug("初始化元数据和数据存储")
        
        metadata = {}  # 存储元数据
        data_lines = []  # 存储数据行
        column_names = []  # 存储列名
        
        try:
            # 读取文件内容并去除空行
            logger.debug("读取文件内容")
            with open(file_path_obj, 'r') as file:
                lines = [line.strip() for line in file if line.strip()]
                
            # 提取元数据(包含':'的行)
            logger.debug("解析元数据")
            metadata_end_idx = 0
            for idx, line in enumerate(lines):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
                    metadata_end_idx = idx
                else:
                    break
            
            # 提取列名(元数据后的第一行)
            header_idx = metadata_end_idx + 1
            if header_idx >= len(lines):
                logger.error("文件格式错误: 缺少列标题")
                raise ValueError("文件格式错误: 缺少列标题")
            
            column_names = lines[header_idx].split('\t')
            logger.debug(f"检测到列名: {column_names}")
            
            # 提取单位(列名后的一行)
            units_idx = header_idx + 1
            if units_idx >= len(lines):
                logger.error("文件格式错误: 缺少单位行")
                raise ValueError("文件格式错误: 缺少单位行")
                
            column_units = lines[units_idx].split('\t')
            
            # 将单位信息存储到元数据中
            logger.debug("解析单位信息")
            for i, unit in enumerate(column_units):
                if i < len(column_names):
                    unit_match = re.search(r'\[(.*?)\]', unit)
                    if unit_match:
                        unit_value = unit_match.group(1)
                        metadata[f"{column_names[i]} Unit"] = unit_value
            
            # 提取数据行(单位行之后的所有行)
            data_lines = lines[units_idx + 1:]
            
            # 解析数据行到列表中
            logger.debug("解析数据行")
            data_values = []
            for line in data_lines:
                # 检查行是否以数字或负号开头(数据行)
                if line and (line[0].isdigit() or line[0] == '-'):
                    data_values.append(line.split('\t'))
            
            # 创建DataFrame
            logger.debug("创建DataFrame")
            df = pd.DataFrame(data_values, columns=column_names)
            
            # 将数值列转换为适当的数据类型
            logger.debug("转换数据类型")
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 删除可能由解析错误导致的NaN行
            df = df.dropna(how='all')
            
            logger.info(f"成功加载文件: {file_path}")
            logger.debug(f"数据形状: {df.shape}")
            
            return cls(
                metadata=metadata,
                data=df,
                file_path=str(file_path_obj.resolve())
            )
            
        except Exception as e:
            # 记录异常信息，包含堆栈跟踪
            logger.exception(f"解析振动数据文件时出错: {str(e)}")
            raise ValueError(f"解析振动数据文件时出错: {e}")
    
    def get_column_units(self) -> Dict[str, str]:
        """
        从元数据中提取列的单位信息
        
        返回:
            将列名映射到其单位的字典
        """
        units = {}
        for key, value in self.metadata.items():
            if key.endswith(" Unit") and key[:-5] in self.data.columns:
                units[key[:-5]] = value
        return units
    
    def plot_time_series(self, columns: List[str] = None, figsize=(12, 8)):
        """
        将选定列的数据绘制为时间序列图
        
        参数:
            columns: 要绘制的列名列表。如果为None，则绘制所有数值列
            figsize: 图形尺寸，格式为(宽度, 高度)的元组
            
        返回:
            matplotlib的Figure和Axes对象
        """
        if self.data is None:
            logger.error("没有可用于绘图的数据")
            raise ValueError("没有可用于绘图的数据")
            
        if columns is None:
            # 仅选择数值类型的列
            columns = self.data.select_dtypes(include=['number']).columns.tolist()
        
        logger.debug(f"绘制时间序列图，选择的列: {columns}")
        
        fig, ax = plt.subplots(figsize=figsize)
        
        x_col = self.data.columns[0]  # 假设第一列为时间/x轴
        units = self.get_column_units()
        
        for col in columns:
            if col != x_col and col in self.data.columns:
                ax.plot(self.data[x_col], self.data[col], label=col)
        
        # 添加标签和图例
        x_label = f"{x_col}"
        if x_col in units:
            x_label += f" [{units[x_col]}]"
        ax.set_xlabel(x_label)
        
        ax.set_title(f"振动数据: {Path(self.file_path).name}")
        ax.grid(True)
        ax.legend()
        
        logger.debug("时间序列图绘制完成")
        return fig, ax
    
    def to_csv(self, output_path: str = None, include_metadata: bool = False) -> str:
        """
        将数据导出为CSV文件
        
        参数:
            output_path: 保存CSV文件的路径。如果为None，则使用原始文件名并改为.csv扩展名
            include_metadata: 是否在CSV文件开头包含元数据注释信息。
                            默认为False(不包含元数据注释)
            
        返回:
            保存的CSV文件路径
        """
        if self.data is None:
            logger.error("没有可用于导出的数据")
            raise ValueError("没有可用于导出的数据")
        
        if output_path is None:
            if self.file_path is None:
                logger.error("未指定输出路径且无原始文件路径可用")
                raise ValueError("未指定输出路径且无原始文件路径可用")
            # 使用原始文件名并改为.csv扩展名
            output_path = str(Path(self.file_path).with_suffix(".csv"))
        
        logger.info(f"开始导出数据到: {output_path}")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        try:
            if include_metadata:
                logger.debug("写入元数据")
                # 将元数据作为注释写入文件开头
                with open(output_path, 'w') as f:
                    for key, value in self.metadata.items():
                        f.write(f"# {key}: {value}\n")
                    f.write("\n")  # 元数据后的空行
                
                # 将数据追加到文件中
                logger.debug("追加数据到文件")
                self.data.to_csv(output_path, mode='a', index=False)
            else:
                # 仅写入数据，不包含元数据注释
                logger.debug("写入数据(不包含元数据)")
                self.data.to_csv(output_path, index=False)
            
            logger.info(f"数据已成功导出到: {output_path}")
            return output_path
            
        except Exception as e:
            # 记录异常并带堆栈信息
            logger.exception(f"导出CSV文件时出错: {str(e)}")
            raise
    
    @staticmethod
    def convert_txt_to_csv_batch(input_folder: str, output_folder: str, include_metadata: bool = False) -> List[str]:
        """
        将文件夹中的所有TXT格式振动数据文件批量转换为CSV格式。
        
        参数:
            input_folder: 包含TXT文件的输入文件夹路径
            output_folder: CSV文件的保存文件夹路径
            include_metadata: 是否在CSV文件中包含元数据注释信息。
                            默认为False(不包含元数据)
            
        返回:
            已保存的CSV文件路径列表
        """
        # 确保输出目录存在
        os.makedirs(output_folder, exist_ok=True)
        
        # 查找输入文件夹中的所有txt文件
        input_files = glob.glob(os.path.join(input_folder, "*.txt"))
        logger.info(f"在 {input_folder} 中找到 {len(input_files)} 个txt文件")
        
        output_files = []
        for input_file in input_files:
            try:
                logger.info(f"开始处理文件: {input_file}")
                # 加载数据
                loader = VibrationDataLoader.from_txt(input_file)
                
                # 创建输出路径
                filename = os.path.basename(input_file)
                output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + ".csv")
                
                # 导出为CSV
                loader.to_csv(output_path, include_metadata)
                output_files.append(output_path)
                
                logger.info(f"成功处理文件: {input_file} -> {output_path}")
            except Exception as e:
                logger.error(f"处理 {input_file} 时出错: {str(e)}")
                # 使用exception方法记录堆栈信息
                with logger.catch():
                    raise e
        
        logger.info(f"批处理完成，共处理 {len(output_files)} 个文件")
        return output_files


if __name__ == "__main__":
    # 配置日志系统
    # logger.remove()  # 移除默认处理器
    # # 添加控制台和文件处理器
    # logger.add(sys.stdout, level="DEBUG")  # 控制台输出调试信息
    # logger.add("vibration_data.log", rotation="10 MB", level="INFO")  # 文件只记录INFO及以上级别
    logger.configure(
        handlers=[
            {"sink": sys.stdout, "level": "INFO"},
            {"sink": "vibration_data_loader.log", "level": "DEBUG", "rotation": "10 MB"},
            ]
        )
    # 测试批量处理文件夹
    VibrationDataLoader.convert_txt_to_csv_batch("./input/data", "./output/data_csv")
