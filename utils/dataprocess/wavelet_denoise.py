import pywt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Union, List, Optional, Tuple
from pathlib import Path
import os
from loguru import logger

class WaveletDenoiser:
    def __init__(self, wavelet: str = 'db4', level: int = 3, keep_nodes: Optional[List[str]] = None):
        """
        使用小波包分解进行去噪。

        参数：
            wavelet: 小波名称，例如 'db4'
            level: 分解的层数
            keep_nodes: 需要保留的结点路径，例如 ['aaa', 'aad']
        """
        self.wavelet = wavelet
        self.level = level
        self.keep_nodes = keep_nodes

    def denoise_signal(self, signal: Union[np.ndarray, pd.Series]) -> np.ndarray:
        wp = pywt.WaveletPacket(data=signal, wavelet=self.wavelet, mode='symmetric', maxlevel=self.level)
        all_nodes = [node.path for node in wp.get_level(self.level, 'freq')]

        new_wp = pywt.WaveletPacket(data=None, wavelet=self.wavelet, mode='symmetric')
        for path in all_nodes:
            if self.keep_nodes is None or path in self.keep_nodes:
                new_wp[path] = wp[path].data
            else:
                new_wp[path] = np.zeros_like(wp[path].data)

        return new_wp.reconstruct(update=False)[:len(signal)]

    def denoise_dataframe(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
        df_denoised = df.copy()
        if columns is None:
            columns = df.select_dtypes(include=['number']).columns.tolist()
        for col in columns:
            if col in df.columns:
                df_denoised[col] = self.denoise_signal(df[col].values)
        return df_denoised

    def denoise_csv_batch(self, input_folder: str, output_folder: str, columns: Optional[List[str]] = None) -> List[str]:
        os.makedirs(output_folder, exist_ok=True)
        input_files = list(Path(input_folder).glob("*.csv"))
        output_paths = []

        for file in input_files:
            try:
                logger.info(f"处理文件: {file}")
                df = pd.read_csv(file)
                df_denoised = self.denoise_dataframe(df, columns=columns)

                output_path = Path(output_folder) / file.name
                df_denoised.to_csv(output_path, index=False)
                output_paths.append(str(output_path))

                logger.info(f"保存去噪数据到: {output_path}")
            except Exception as e:
                logger.error(f"处理 {file} 时出错: {e}")

        return output_paths

    def plot_denoise_comparison(self, df: pd.DataFrame, denoised_df: pd.DataFrame, column: str, time_column: Optional[str] = None, figsize=(14, 5)):
        x = df[time_column] if time_column and time_column in df.columns else df.index

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize, sharex=True)

        ax1.plot(x, df[column], label="原始", color='tab:blue')
        ax1.set_title(f"原始信号: {column}")
        ax1.set_xlabel(time_column if time_column else "Index")
        ax1.set_ylabel(column)
        ax1.grid(True)

        ax2.plot(x, denoised_df[column], label="去噪", color='tab:orange')
        ax2.set_title(f"去噪信号: {column}")
        ax2.set_xlabel(time_column if time_column else "Index")
        ax2.set_ylabel(column)
        ax2.grid(True)

        fig.suptitle(f"{column} 小波包去噪前后对比", fontsize=14)
        plt.tight_layout()
        plt.show()

    def plot_denoise_overlay(self, df: pd.DataFrame, denoised_df: pd.DataFrame, column: str, time_column: Optional[str] = None, figsize=(12, 5)):
        x = df[time_column] if time_column and time_column in df.columns else df.index
        plt.figure(figsize=figsize)
        plt.plot(x, df[column], label="原始", color='tab:blue', alpha=0.6)
        plt.plot(x, denoised_df[column], label="去噪", color='tab:orange', alpha=0.8)
        plt.title(f"{column} 小波包重叠对比图")
        plt.xlabel(time_column if time_column else "Index")
        plt.ylabel(column)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def auto_select_trend_nodes(self, signal: np.ndarray, threshold_ratio: float = 0.1, fs: float = 1.0, plot: str = "bar") -> List[str]:
        wp = pywt.WaveletPacket(data=signal, wavelet=self.wavelet, mode='symmetric', maxlevel=self.level)
        nodes = wp.get_level(self.level, order='freq')

        path_energy = [(node.path, np.sum(np.square(node.data))) for node in nodes]
        max_energy = max(e for _, e in path_energy)
        selected = [path for path, energy in path_energy if energy >= threshold_ratio * max_energy]

        if plot == "bar":
            plt.figure(figsize=(12, 4))
            for path, energy in path_energy:
                plt.bar(path, energy, alpha=0.6, color='tab:gray' if path not in selected else 'tab:orange')
            plt.title("小波包路径能量分布")
            plt.ylabel("能量")
            plt.grid(True)
            plt.tight_layout()
            plt.show()

        elif plot == "band":
            plt.figure(figsize=(12, 3))
            for i, (path, energy) in enumerate(path_energy):
                f_start = i / 2**self.level * fs
                f_end = (i + 1) / 2**self.level * fs
                plt.barh(0, f_end - f_start, left=f_start, height=0.5,
                         color='tab:orange' if path in selected else 'tab:gray',
                         edgecolor='black', alpha=0.7)
                plt.text((f_start + f_end) / 2, 0.1, path, ha='center', va='bottom', fontsize=8)
            plt.xlabel("频率 (Hz)")
            plt.title("小波包路径频率分布（橙色为保留）")
            plt.yticks([])
            plt.tight_layout()
            plt.show()

        self.keep_nodes = selected
        return selected

    def get_node_frequency_range(self, node_index: int, fs: float = 1.0) -> Tuple[float, float]:
        """
        获取第 node_index 个路径对应的频率范围（Hz）

        参数：
            node_index: 节点在第 level 层中的索引（0 到 2^level - 1）
            fs: 采样频率

        返回：
            (起始频率, 结束频率)
        """
        total_nodes = 2 ** self.level
        f_start = node_index / total_nodes * fs
        f_end = (node_index + 1) / total_nodes * fs
        return f_start, f_end
