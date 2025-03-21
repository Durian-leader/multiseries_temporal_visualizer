import numpy as np
import pywt
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Union, Optional, Any


class WaveletTransform:
    """
    实现离散小波变换(DWT)和小波包分解(WPD)的类，用于信号分解和重构。
    
    属性:
        wavelet (str): 小波函数名称
        max_level (int): 最大分解层数
        mode (str): 边界处理模式
    """
    
    def __init__(self, wavelet: str = 'db4', mode: str = 'symmetric'):
        """
        初始化WaveletTransform类
        
        参数:
            wavelet (str): 小波函数名称，默认为'db4'
            mode (str): 边界处理模式，默认为'symmetric'
        """
        self.wavelet = wavelet
        self.mode = mode
        self._validate_inputs()
        
    def _validate_inputs(self) -> None:
        """验证输入参数的有效性"""
        # 验证小波函数是否存在
        if self.wavelet not in pywt.wavelist():
            raise ValueError(f"小波函数 '{self.wavelet}' 不存在。可用的小波函数: {pywt.wavelist()}")
        
        # 验证边界处理模式是否有效
        valid_modes = ['zero', 'constant', 'symmetric', 'periodic', 'smooth', 'periodization', 'reflect', 'antisymmetric', 'antireflect']
        if self.mode not in valid_modes:
            raise ValueError(f"边界处理模式 '{self.mode}' 无效。有效的模式: {valid_modes}")

    def get_max_level(self, signal: np.ndarray) -> int:
        """
        计算给定信号的最大可能分解层数
        
        参数:
            signal (np.ndarray): 输入信号
            
        返回:
            int: 最大可能分解层数
        """
        return pywt.dwt_max_level(len(signal), pywt.Wavelet(self.wavelet).dec_len)
    
    def dwt_decompose(self, signal: np.ndarray, level: int) -> Dict[str, np.ndarray]:
        """
        使用DWT对信号进行多层分解，DWT全称为Discrete Wavelet Transform，即离散小波变换。
        
        参数:
            signal (np.ndarray): 输入信号
            level (int): 分解层数
            
        返回:
            Dict[str, np.ndarray]: 包含近似系数(cA)和细节系数(cD1, cD2, ...)的字典
        """
        # 验证分解层数是否有效
        max_level = self.get_max_level(signal)
        if level > max_level:
            raise ValueError(f"分解层数 {level} 超过了最大可能层数 {max_level}。")
        
        # 执行小波分解
        coeffs = pywt.wavedec(signal, self.wavelet, mode=self.mode, level=level)
        
        # 将结果整理成字典
        result = {'cA' + str(level): coeffs[0]}
        for i in range(1, level + 1):
            result['cD' + str(level - i + 1)] = coeffs[i]
        
        return result
    
    def dwt_reconstruct(self, coeffs: Dict[str, np.ndarray], original_length: Optional[int] = None) -> np.ndarray:
        """
        使用DWT系数重构信号
        
        参数:
            coeffs (Dict[str, np.ndarray]): 包含近似系数和细节系数的字典
            original_length (int, optional): 原始信号长度，用于精确重构
            
        返回:
            np.ndarray: 重构后的信号
        """
        # 确定分解层数
        level = 0
        for key in coeffs.keys():
            if key.startswith('cD'):
                level = max(level, int(key[2:]))
        
        # 将字典转换为列表形式
        coeff_list = [coeffs.get('cA' + str(level), None)]
        for i in range(level, 0, -1):
            coeff_list.append(coeffs.get('cD' + str(i), None))
        
        # 去除None值
        coeff_list = [c for c in coeff_list if c is not None]
        
        # 重构信号
        reconstructed = pywt.waverec(coeff_list, self.wavelet, mode=self.mode)
        
        # 如果提供了原始长度，裁剪重构信号
        if original_length is not None and len(reconstructed) > original_length:
            reconstructed = reconstructed[:original_length]
        
        return reconstructed
    
    def wpd_decompose(self, signal: np.ndarray, level: int) -> Dict[str, np.ndarray]:
        """
        使用WPD对信号进行分解，WPD全称为Wavelet Packet Decomposition，即小波包分解。
        
        参数:
            signal (np.ndarray): 输入信号
            level (int): 分解层数
            
        返回:
            Dict[str, np.ndarray]: 小波包系数字典，键为节点路径
        """
        # 验证分解层数是否有效
        max_level = self.get_max_level(signal)
        if level > max_level:
            raise ValueError(f"分解层数 {level} 超过了最大可能层数 {max_level}。")
        
        # 创建小波包树
        wp = pywt.WaveletPacket(data=signal, wavelet=self.wavelet, mode=self.mode)
        
        # 获取系数
        coeffs = {}
        for node in wp.get_level(level, 'natural'):
            path = node.path
            coeffs[path] = node.data
        
        return coeffs
    
    def wpd_reconstruct(self, coeffs: Dict[str, np.ndarray], original_length: Optional[int] = None) -> np.ndarray:
        """
        使用WPD系数重构信号
        
        参数:
            coeffs (Dict[str, np.ndarray]): 小波包系数，键为节点路径
            original_length (int, optional): 原始信号长度
            
        返回:
            np.ndarray: 重构后的信号
        """
        # 创建空的小波包对象
        wp = pywt.WaveletPacket(data=None, wavelet=self.wavelet, mode=self.mode)
        
        # 将系数添加到小波包中
        for path, coeff in coeffs.items():
            # 创建节点并设置数据
            wp[path] = coeff
        
        # 重构信号
        reconstructed = wp.reconstruct()
        
        # 如果提供了原始长度，裁剪重构信号
        if original_length is not None and len(reconstructed) > original_length:
            reconstructed = reconstructed[:original_length]
        
        return reconstructed
    
    def filter_coeffs(self, coeffs: Dict[str, np.ndarray], to_keep: List[str]) -> Dict[str, np.ndarray]:
        """
        过滤DWT系数，仅保留指定的系数
        
        参数:
            coeffs (Dict[str, np.ndarray]): DWT系数字典
            to_keep (List[str]): 要保留的系数名称列表
            
        返回:
            Dict[str, np.ndarray]: 过滤后的系数字典
        """
        filtered = {}
        for key in to_keep:
            if key in coeffs:
                filtered[key] = coeffs[key]
            else:
                # 对于没有在原始系数中找到的系数，用零数组代替
                for existing_key, value in coeffs.items():
                    if existing_key.startswith('c'):
                        filtered[key] = np.zeros_like(value)
                        break
        return filtered
    
    def plot_coeffs(self, coeffs: Dict[str, np.ndarray], figsize: Tuple[int, int] = (12, 8)) -> None:
        """
        绘制DWT系数
        
        参数:
            coeffs (Dict[str, np.ndarray]): DWT系数字典
            figsize (Tuple[int, int]): 图形大小
        """
        n_coeffs = len(coeffs)
        fig, axes = plt.subplots(n_coeffs, 1, figsize=figsize)
        
        if n_coeffs == 1:
            axes = [axes]
        
        for i, (name, coeff) in enumerate(sorted(coeffs.items())):
            axes[i].plot(coeff)
            axes[i].set_title(f"系数 {name}")
            axes[i].set_xlabel("采样点")
            axes[i].set_ylabel("振幅")
            axes[i].grid(True)
        
        plt.tight_layout()
        plt.show()
    
    def denoise_signal(self, signal: np.ndarray, level: int, threshold_method: str = 'soft', 
                      threshold_level: Union[float, str] = 'universal') -> np.ndarray:
        """
        使用小波阈值去噪
        
        参数:
            signal (np.ndarray): 输入信号
            level (int): 分解层数
            threshold_method (str): 阈值方法，'soft'或'hard'
            threshold_level (Union[float, str]): 阈值大小或方法
            
        返回:
            np.ndarray: 去噪后的信号
        """
        # 信号分解
        coeffs = self.dwt_decompose(signal, level)
        
        # 对细节系数应用阈值
        for key, coeff in coeffs.items():
            if key.startswith('cD'):  # 只对细节系数应用阈值
                if isinstance(threshold_level, str) and threshold_level == 'universal':
                    # 计算通用阈值
                    threshold = np.sqrt(2 * np.log(len(coeff))) * np.median(np.abs(coeff)) / 0.6745
                else:
                    threshold = float(threshold_level)
                
                # 应用阈值
                if threshold_method == 'soft':
                    coeffs[key] = pywt.threshold(coeff, threshold, 'soft')
                else:
                    coeffs[key] = pywt.threshold(coeff, threshold, 'hard')
        
        # 重构信号
        return self.dwt_reconstruct(coeffs, len(signal))
    
    def feature_extraction(self, signal: np.ndarray, level: int, feature_type: str = 'energy') -> Dict[str, float]:
        """
        从小波系数中提取特征
        
        参数:
            signal (np.ndarray): 输入信号
            level (int): 分解层数
            feature_type (str): 特征类型，可以是'energy'或'entropy'
            
        返回:
            Dict[str, float]: 特征字典
        """
        # 信号分解
        coeffs = self.dwt_decompose(signal, level)
        
        features = {}
        for key, coeff in coeffs.items():
            if feature_type == 'energy':
                # 计算能量
                features[key + '_energy'] = np.sum(coeff**2)
            elif feature_type == 'entropy':
                # 计算Shannon熵
                prob = coeff**2 / np.sum(coeff**2)
                prob = prob[prob > 0]  # 避免log(0)
                features[key + '_entropy'] = -np.sum(prob * np.log2(prob))
        
        return features


# 使用示例
if __name__ == "__main__":
    # 生成测试信号
    t = np.linspace(0, 1, 1000, endpoint=False)
    signal = np.sin(2 * np.pi * 5 * t) + 0.5 * np.sin(2 * np.pi * 50 * t)
    
    # 添加噪声
    np.random.seed(42)
    noisy_signal = signal + 0.2 * np.random.randn(len(signal))
    
    # 创建小波变换对象
    wt = WaveletTransform(wavelet='db4')
    
    # DWT分解
    level = 5
    dwt_coeffs = wt.dwt_decompose(noisy_signal, level)
    
    # 绘制DWT系数
    wt.plot_coeffs(dwt_coeffs)
    
    # 重构信号
    reconstructed = wt.dwt_reconstruct(dwt_coeffs, len(noisy_signal))
    
    # 去噪
    denoised = wt.denoise_signal(noisy_signal, level)
    
    # 绘制结果
    plt.figure(figsize=(12, 10))
    
    plt.subplot(3, 1, 1)
    plt.plot(t, signal)
    plt.title("原始信号")
    plt.grid(True)
    
    plt.subplot(3, 1, 2)
    plt.plot(t, noisy_signal)
    plt.title("带噪信号")
    plt.grid(True)
    
    plt.subplot(3, 1, 3)
    plt.plot(t, denoised)
    plt.title("去噪信号")
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    # WPD分解
    wpd_coeffs = wt.wpd_decompose(noisy_signal, 3)
    
    # 重构WPD信号
    wpd_reconstructed = wt.wpd_reconstruct(wpd_coeffs, len(noisy_signal))
    
    # 特征提取
    features = wt.feature_extraction(noisy_signal, level, 'energy')
    print("提取的能量特征:")
    for key, value in features.items():
        print(f"{key}: {value}")