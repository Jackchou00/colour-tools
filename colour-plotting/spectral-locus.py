def get_spectral_locus():
    """使用 colour-science 库获取 CIE 1931 2° 标准观察者的光谱轨迹"""
    cmfs = colour.MSDS_CMFS["CIE 1931 2 Degree Standard Observer"]
    wavelengths = cmfs.wavelengths
    cmf_data = cmfs.values

    x_bar = cmf_data[:, 0]
    y_bar = cmf_data[:, 1]
    z_bar = cmf_data[:, 2]

    total = x_bar + y_bar + z_bar
    valid = total > 1e-10
    x_locus = np.zeros_like(x_bar)
    y_locus = np.zeros_like(y_bar)
    x_locus[valid] = x_bar[valid] / total[valid]
    y_locus[valid] = y_bar[valid] / total[valid]

    denom = x_bar + 15 * y_bar + 3 * z_bar
    u_locus = np.zeros_like(x_bar)
    v_locus = np.zeros_like(y_bar)
    valid_uv = denom > 1e-10
    u_locus[valid_uv] = 4 * x_bar[valid_uv] / denom[valid_uv]
    v_locus[valid_uv] = 9 * y_bar[valid_uv] / denom[valid_uv]

    return x_locus, y_locus, u_locus, v_locus, wavelengths

