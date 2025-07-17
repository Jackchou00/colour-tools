import rawpy
import numpy as np
from typing import Optional


def read_raw(path: str) -> np.ndarray:
    """
    从 RAW 文件中读取图像数据
    
    参数:
        path (str): RAW 文件路径
        
    返回:
        np.ndarray: 归一化后的图像数据，形状为 (height, width, 3)，数据类型为 float32
        
    异常:
        FileNotFoundError: 当指定路径的文件不存在时
        rawpy.LibRawError: 当文件格式不支持或损坏时
    """
    try:
        with rawpy.imread(path) as raw:
            crgb = raw.postprocess(
                gamma=(1, 1),
                output_bps=16,
                user_wb=[1, 1, 1, 1],
                output_color=rawpy.ColorSpace.raw,
                no_auto_bright=True,
            )
    except Exception as e:
        raise RuntimeError(f"无法读取RAW文件 '{path}': {str(e)}") from e
    
    # 将数据归一化到 [0, 1] 范围并转换为 float32
    crgb = crgb.astype(np.float32) / 65535.0
    
    # 验证数据范围
    if not (0.0 <= crgb.min() <= crgb.max() <= 1.0):
        raise ValueError(f"数据范围超出预期: [{crgb.min()}, {crgb.max()}]")
    
    return crgb