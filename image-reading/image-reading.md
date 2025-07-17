# 图像读取

用于从各种格式的文件中，正确的读取图像数据和附属信息。

## we-spectra.py: 蔚谱高光谱相机的图像读取

拍完之后，选择光谱立方保存，并记录下 RGB 图像的高度和宽度，以及通道数。

### 函数说明

#### `read_hyperspectral_cube(file_path, height, width, channels=61)`

从二进制文件中读取高光谱立方体数据。

**参数:**
- `file_path` (str): 文件路径
- `height` (int): 图像高度
- `width` (int): 图像宽度  
- `channels` (int): 光谱通道数，默认61

**返回:**
- `np.ndarray`: 形状为(height, width, channels)的numpy数组，数据类型为float32

**异常:**
- `FileNotFoundError`: 当指定路径的文件不存在时
- `ValueError`: 当文件大小与预期不符时
- `OSError`: 当文件无法读取或内存映射失败时

**使用示例:**
```python
from image_reading.we_spectra import read_hyperspectral_cube

# 读取光谱数据
height = 2464
width = 4500
channels = 61
spectral_cube = read_hyperspectral_cube("path/to/data.SC", height, width, channels)
print(spectral_cube.shape)  # 输出: (2464, 4500, 61)
```

#### `get_hyperspectral_info(file_path, height, width, channels=61)`

获取高光谱立方体文件的信息而不完全加载数据，适合大文件预检。

**参数:**
- `file_path` (str): 文件路径
- `height` (int): 图像高度
- `width` (int): 图像宽度
- `channels` (int): 光谱通道数，默认61

**返回:**
- `dict`: 包含文件信息的字典
  - `file_path`: 文件路径
  - `file_size_mb`: 文件大小（MB）
  - `expected_size_mb`: 预期大小（MB）
  - `dimensions`: 数据维度 (height, width, channels)
  - `is_valid`: 文件大小是否有效
  - `data_type`: 数据类型

**使用示例:**
```python
from image_reading.we_spectra import get_hyperspectral_info

info = get_hyperspectral_info("path/to/data.SC", 2464, 4500, 61)
print(f"文件大小: {info['file_size_mb']:.2f} MB")
print(f"数据维度: {info['dimensions']}")
print(f"是否有效: {info['is_valid']}")
```

### 内存优化

使用 `np.memmap` 进行内存映射读取，可以有效处理GB级别的大文件，避免一次性加载到内存中。

## raw-universal.py: 通用的 RAW 文件读取

一种通用的读取 raw 数据的办法，已经包含了黑电平扣除、归一化、解马赛克。

### 函数说明

#### `read_raw(path)`

从 RAW 文件中读取并处理图像数据。

**参数:**
- `path` (str): RAW 文件路径

**返回:**
- `np.ndarray`: 归一化后的图像数据，形状为 (height, width, 3)，数据类型为float32，数值范围[0,1]

**异常:**
- `FileNotFoundError`: 当指定路径的文件不存在时
- `RuntimeError`: 当无法读取RAW文件时（包括格式不支持或文件损坏）
- `ValueError`: 当数据范围超出预期时

**处理流程:**
1. 读取RAW文件
2. 应用后处理参数：
   - gamma=(1,1): 线性gamma
   - output_bps=16: 16位输出
   - user_wb=[1,1,1,1]: 禁用白平衡
   - output_color=rawpy.ColorSpace.raw: 原始色彩空间
   - no_auto_bright=True: 禁用自动亮度
3. 归一化到[0,1]范围
4. 转换为float32类型

**使用示例:**
```python
from image_reading.raw_universal import read_raw

# 读取RAW文件
raw_image = read_raw("path/to/image.NEF")
print(raw_image.shape)  # 输出: (height, width, 3)
print(f"数据范围: [{raw_image.min():.4f}, {raw_image.max():.4f}]")
```

### 等价命令

该函数等价于以下dcraw命令：
```bash
dcraw -v -4 -T -o 0 -W -H 0 -r 1 1 1 1 -g 1 1 image.NEF
```