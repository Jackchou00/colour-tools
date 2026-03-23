"""
将XYZ绝对值写入avif
"""

import os
import colour
import cv2
import numpy as np
import tifffile
from imagecodecs import AVIF, avif_encode

# 启用 OpenCV 的 OpenEXR 支持
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"


# from xyz(abs) to avif(bt.2020, hdr, pq)
def xyz_to_avif_bt2020_pq(xyz, output_path):
    # XYZ to linear RGB (BT.2020)
    bt2020_linear = colour.XYZ_to_RGB(xyz, colourspace="ITU-R BT.2020")
    bt2020_linear = np.clip(bt2020_linear, 0, None)
    bt2020_pq = colour.eotf_inverse(bt2020_linear, function="ITU-R BT.2100 PQ")
    bt2020_pq_10bit = np.clip(bt2020_pq * 1023, 0, 1023).astype(np.uint16)
    avif_bytes = avif_encode(
        bt2020_pq_10bit,
        level=AVIF.QUALITY.BEST,
        speed=AVIF.SPEED.FASTEST,
        bitspersample=10,
        primaries=AVIF.COLOR_PRIMARIES.BT2020,
        transfer=AVIF.TRANSFER_CHARACTERISTICS.PQ,
        matrix=AVIF.MATRIX_COEFFICIENTS.BT2020_NCL,
        numthreads=8,
    )
    with open(output_path, "wb") as f:
        f.write(avif_bytes)


# from xyz(abs) to avif(bt.2020, hdr, hlg)
def xyz_to_avif_bt2020_hlg(xyz, output_path):
    # XYZ to linear RGB (BT.2020)
    bt2020_linear = colour.XYZ_to_RGB(xyz, colourspace="ITU-R BT.2020")
    bt2020_linear = np.clip(bt2020_linear, 0, None)
    bt2020_hlg = colour.eotf_inverse(bt2020_linear, function="ITU-R BT.2100 HLG")
    bt2020_hlg_10bit = np.clip(bt2020_hlg * 1023, 0, 1023).astype(np.uint16)
    avif_bytes = avif_encode(
        bt2020_hlg_10bit,
        level=AVIF.QUALITY.BEST,
        speed=AVIF.SPEED.FASTEST,
        bitspersample=10,
        primaries=AVIF.COLOR_PRIMARIES.BT2020,
        transfer=AVIF.TRANSFER_CHARACTERISTICS.HLG,
        matrix=AVIF.MATRIX_COEFFICIENTS.BT2020_NCL,
        numthreads=8,
    )
    with open(output_path, "wb") as f:
        f.write(avif_bytes)


# from xyz(abs) to avif(bt.2020, sdr, linear)
def xyz_to_avif_bt2020_linear(xyz, output_path):
    # XYZ to linear RGB (BT.2020)
    bt2020_linear = colour.XYZ_to_RGB(xyz, colourspace="ITU-R BT.2020")
    bt2020_linear = np.clip(bt2020_linear, 0, None) / 203.0
    bt2020_linear_10bit = np.clip(bt2020_linear * 1023, 0, 1023).astype(np.uint16)
    avif_bytes = avif_encode(
        bt2020_linear_10bit,
        level=AVIF.QUALITY.BEST,
        speed=AVIF.SPEED.FASTEST,
        bitspersample=10,
        primaries=AVIF.COLOR_PRIMARIES.BT2020,
        transfer=AVIF.TRANSFER_CHARACTERISTICS.LINEAR,
        matrix=AVIF.MATRIX_COEFFICIENTS.BT2020_NCL,
        numthreads=8,
    )
    with open(output_path, "wb") as f:
        f.write(avif_bytes)


# from xyz(abs) to TIFF (sRGB, linear, 32-bit float)
def xyz_to_tiff_srgb_linear(xyz, output_path):
    # 1. XYZ to linear RGB (sRGB)
    srgb_linear = colour.XYZ_to_RGB(xyz, colourspace="sRGB")
    srgb_linear = np.clip(srgb_linear, 0, None)

    # 2. 映射亮度：将 203 nits 映射为 1.0 (SDR 峰值白)
    # 超过 203 的部分将自然成为 > 1.0 的浮点数高光
    srgb_linear_float32 = (srgb_linear / 203.0).astype(np.float32)

    # 3. 写入 32-bit Float TIFF
    # tifffile 原生支持写入多维浮点数组
    tifffile.imwrite(
        output_path,
        srgb_linear_float32,
        photometric="rgb",
        metadata={"ColorSpace": "sRGB Linear"},  # 写入基础元数据备注
    )


# from xyz(abs) to OpenEXR (sRGB, linear, 32-bit float)
def xyz_to_exr_srgb_linear(xyz, output_path):
    # 1. XYZ to linear RGB (sRGB)
    srgb_linear = colour.XYZ_to_RGB(xyz, colourspace="sRGB")
    srgb_linear = np.clip(srgb_linear, 0, None)

    # 2. 映射亮度：203 nits -> 1.0
    srgb_linear_float32 = (srgb_linear / 203.0).astype(np.float32)

    # 3. OpenCV 默认使用 BGR 通道顺序，因此在写入前需要翻转通道 (RGB -> BGR)
    srgb_bgr_float32 = srgb_linear_float32[:, :, ::-1]

    # 4. 写入 OpenEXR
    cv2.imwrite(
        output_path,
        srgb_bgr_float32,
        [cv2.IMWRITE_EXR_TYPE, cv2.IMWRITE_EXR_TYPE_FLOAT],  # 强制使用 32-bit Float
    )
