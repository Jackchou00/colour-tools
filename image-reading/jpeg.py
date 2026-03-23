from imagecodecs import jpeg_decode


def read_with_imagecodecs(path):
    with open(path, "rb") as f:
        data = f.read()
    img = jpeg_decode(data)
    return img.astype(np.uint8)
