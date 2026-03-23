"""
几种使用 rawpy 读取 RAW 图像数据的方法。
"""

import numpy as np
import rawpy


def read_raw_image(path):
    """
    Get demosaiced RGB image data from a RAW file.

    Arguments:
        path (str): RAW file path

    Returns:
        np.ndarray: Normalized image data with shape (height, width, 3) and dtype float32
    """
    try:
        with rawpy.imread(path) as raw:
            crgb = raw.postprocess(
                gamma=(1, 1),
                output_bps=16,
                user_wb=[1, 1, 1, 1],
                output_color=rawpy.ColorSpace.raw,
                half_size=False,  # Use true to skip demosaicing (Combine RGBG directly, CAN'T BE USED FOR FUJI XTRANS)
                no_auto_bright=True,
            )
    except Exception as e:
        raise RuntimeError(f"Failed to read RAW file '{path}': {str(e)}") from e

    # Normalize data to [0, 1] range and convert to float32
    crgb = crgb.astype(np.float32) / 65535.0

    # Validate data range
    if not (0.0 <= crgb.min() <= crgb.max() <= 1.0):
        raise ValueError(
            f"Data range out of expected bounds: [{crgb.min()}, {crgb.max()}]"
        )

    return crgb


"""
If false color issues arise, consider adjusting the demosaicing algorithm.
"""

with rawpy.imread() as raw:
    crgb = raw.postprocess(
        gamma=(1, 1),
        output_bps=16,
        user_wb=[1, 1, 1, 1],
        output_color=rawpy.ColorSpace.raw,
        demosaic_algorithm=rawpy.DemosaicAlgorithm.DCB,
        dcb_iterations=2,
        four_color_rgb=True,
        dcb_enhance=True,
        median_filter_passes=1,
        no_auto_bright=True,
    )


"""
If want the Bayer pattern and metadata.

Can use bayer_image to check if overexposure occurs (values close to 16383 for 14-bit RAW, or 65,535 for 16-bit RAW)
"""

with rawpy.imread() as raw:
    bayer_image = raw.raw_image.copy()
    black_level_per_channel = raw.black_level_per_channel.copy()
