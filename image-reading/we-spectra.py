import numpy as np
import os
from typing import Tuple, Union


def read_hyperspectral_cube(file_path: str, height: int, width: int, channels: int = 61) -> np.ndarray:
    """
    从二进制文件中读取高光谱立方体数据

    参数:
        file_path (str): 文件路径
        height (int): 图像高度
        width (int): 图像宽度
        channels (int): 光谱通道数，默认61

    返回:
        np.ndarray: 形状为(height, width, channels)的numpy数组，数据类型为float32
        
    异常:
        FileNotFoundError: 当指定路径的文件不存在时
        ValueError: 当文件大小与预期不符时
        OSError: 当文件无法读取或内存映射失败时
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    # 计算预期文件大小
    expected_size = height * width * channels * np.dtype(np.float32).itemsize
    actual_size = os.path.getsize(file_path)
    
    if actual_size != expected_size:
        raise ValueError(
            f"文件大小与预期不符: "
            f"期望 {expected_size} 字节 (H{height}×W{width}×C{channels}×4字节), "
            f"实际 {actual_size} 字节"
        )
    
    try:
        # 使用memmap读取数据以减少内存占用
        temp_shape = (width, height, channels)
        array = np.memmap(file_path, dtype=np.float32, mode="r", shape=temp_shape)
        
        # 转置为正确的形状 (height, width, channels)
        # 从 (width, height, channels) 转换为 (height, width, channels)
        corrected_array = array.transpose(1, 0, 2).copy()
        
        return corrected_array
        
    except Exception as e:
        raise OSError(f"无法读取高光谱数据文件 '{file_path}': {str(e)}") from e


def get_hyperspectral_info(file_path: str, height: int, width: int, channels: int = 61) -> dict:
    """
    获取高光谱立方体文件的信息而不完全加载数据
    
    参数:
        file_path (str): 文件路径
        height (int): 图像高度
        width (int): 图像宽度
        channels (int): 光谱通道数，默认61
        
    返回:
        dict: 包含文件信息的字典
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    file_size = os.path.getsize(file_path)
    expected_size = height * width * channels * np.dtype(np.float32).itemsize
    
    return {
        'file_path': file_path,
        'file_size_mb': file_size / (1024 * 1024),
        'expected_size_mb': expected_size / (1024 * 1024),
        'dimensions': (height, width, channels),
        'is_valid': file_size == expected_size,
        'data_type': 'float32'
    }


if __name__ == "__main__":
    # 设置图像的高度和宽度
    height = 2464
    width = 4500
    channels = 61
    
    # 测试函数
    path = r"400x700x5xRadiance.SC"
    
    try:
        # 获取文件信息
        info = get_hyperspectral_info(path, height, width, channels)
        print("文件信息:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        # 读取数据
        array = read_hyperspectral_cube(path, height, width, channels)
        print(f"\n数据形状: {array.shape}")
        print(f"数据类型: {array.dtype}")
        print(f"数据范围: [{array.min():.4f}, {array.max():.4f}]")
        
    except Exception as e:
        print(f"错误: {e}")
