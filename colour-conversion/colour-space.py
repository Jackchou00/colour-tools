import numpy as np


def srgb_to_linear(srgb: np.ndarray) -> np.ndarray:
    """将 sRGB 值转换为线性 RGB"""
    srgb_normalized = srgb / 255.0
    linear = np.where(
        srgb_normalized <= 0.04045,
        srgb_normalized / 12.92,
        ((srgb_normalized + 0.055) / 1.055) ** 2.4,
    )
    return linear


def linear_rgb_to_xyz(linear_rgb: np.ndarray) -> np.ndarray:
    """将线性 RGB 转换为 CIE XYZ (D65)"""
    matrix = np.array([
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ])
    original_shape = linear_rgb.shape
    pixels = linear_rgb.reshape(-1, 3)
    xyz = pixels @ matrix.T
    return xyz.reshape(original_shape)


def xyz_to_uv(xyz: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """将 XYZ 转换为 CIE 1976 u'v' 色度坐标"""
    xyz_flat = xyz.reshape(-1, 3)
    x_val = xyz_flat[:, 0]
    y_val = xyz_flat[:, 1]
    z_val = xyz_flat[:, 2]

    denom = x_val + 15 * y_val + 3 * z_val
    valid = denom > 1e-10
    u_prime = np.zeros_like(x_val)
    v_prime = np.zeros_like(y_val)
    u_prime[valid] = 4 * x_val[valid] / denom[valid]
    v_prime[valid] = 9 * y_val[valid] / denom[valid]

    return u_prime, v_prime


def xyz_to_lab(xyz: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """将 XYZ 转换为 CIELAB (L*a*b*)，使用 D65 白点"""
    xyz_flat = xyz.reshape(-1, 3)
    x_val = xyz_flat[:, 0]
    y_val = xyz_flat[:, 1]
    z_val = xyz_flat[:, 2]

    Xn, Yn, Zn = 0.95047, 1.0, 1.08883

    def f(t):
        delta = 6 / 29
        return np.where(
            t > delta**3,
            t ** (1/3),
            (1 / (3 * delta**2)) * t + (4 / 29)
        )

    fx = f(x_val / Xn)
    fy = f(y_val / Yn)
    fz = f(z_val / Zn)

    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)

    return L, a, b


def get_srgb_primaries() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """获取 sRGB 原色的色度坐标 (用于 u'v' 图)"""
    primaries_xy = np.array([
        [0.6400, 0.3300],
        [0.3000, 0.6000],
        [0.1500, 0.0600],
        [0.6400, 0.3300],
    ])
    x_p = primaries_xy[:, 0]
    y_p = primaries_xy[:, 1]
    denom = -2 * x_p + 12 * y_p + 3
    u_p = 4 * x_p / denom
    v_p = 9 * y_p / denom
    return x_p, y_p, u_p, v_p


def get_srgb_gamut_lab_boundary(n_samples: int = 50) -> tuple[np.ndarray, np.ndarray]:
    """生成 sRGB 色域在 CIELAB a*b* 平面上的最大饱和度边界"""
    key_points = np.array([
        [1, 0, 0],  # Red
        [1, 1, 0],  # Yellow
        [0, 1, 0],  # Green
        [0, 1, 1],  # Cyan
        [0, 0, 1],  # Blue
        [1, 0, 1],  # Magenta
        [1, 0, 0]   # Back to Red
    ])

    rgb_sequence = []
    for i in range(len(key_points) - 1):
        start = key_points[i]
        end = key_points[i + 1]
        t = np.linspace(0, 1, n_samples)
        segment = start[None, :] * (1 - t[:, None]) + end[None, :] * t[:, None]
        rgb_sequence.append(segment)

    rgb_boundary = np.vstack(rgb_sequence)

    matrix = np.array([
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ])
    xyz_boundary = rgb_boundary @ matrix.T

    Xn, Yn, Zn = 0.95047, 1.0, 1.08883

    def f(t):
        delta = 6 / 29
        result = np.zeros_like(t)
        mask = t > delta**3
        result[mask] = t[mask] ** (1/3)
        result[~mask] = (1 / (3 * delta**2)) * t[~mask] + (4 / 29)
        return result

    x_val = xyz_boundary[:, 0]
    y_val = xyz_boundary[:, 1]
    z_val = xyz_boundary[:, 2]

    fx = f(x_val / Xn)
    fy = f(y_val / Yn)
    fz = f(z_val / Zn)

    a_boundary = 500 * (fx - fy)
    b_boundary = 200 * (fy - fz)

    return a_boundary, b_boundary


def plot_chromaticity_diagram(
    u_chroma: np.ndarray,
    v_chroma: np.ndarray,
    a_lab: np.ndarray,
    b_lab: np.ndarray,
    original_rgb: np.ndarray,
    output_path: str,
) -> None:
    """绘制 CIE 1976 u'v' 和 CIELAB a*b* 图"""
    _, _, u_locus, v_locus, wavelengths = get_spectral_locus()
    _, _, srgb_u, srgb_v = get_srgb_primaries()
    srgb_a, srgb_b = get_srgb_gamut_lab_boundary(n_samples=50)

    colors = original_rgb.reshape(-1, 3) / 255.0
    u_valid = u_chroma
    v_valid = v_chroma
    colors_uv = colors
    a_valid = a_lab
    b_valid = b_lab
    colors_lab = colors

    max_points = 50000
    if len(u_valid) > max_points:
        indices = np.random.choice(len(u_valid), max_points, replace=False)
        u_valid = u_valid[indices]
        v_valid = v_valid[indices]
        colors_uv = colors_uv[indices]
        a_valid = a_valid[indices]
        b_valid = b_valid[indices]
        colors_lab = colors_lab[indices]

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    ax1 = axes[0]
    ax1.set_facecolor("white")
    ax1.plot(u_locus, v_locus, "k-", linewidth=1.5, label="Spectral Locus")
    ax1.plot([u_locus[0], u_locus[-1]], [v_locus[0], v_locus[-1]], "k-", linewidth=1.5)

    label_wavelengths = [460, 480, 500, 520, 540, 560, 580, 600, 620]
    for wl in label_wavelengths:
        idx = (wavelengths == wl).argmax() if wl in wavelengths else -1
        if idx >= 0:
            ax1.annotate(f"{wl}", (u_locus[idx], v_locus[idx]), fontsize=8, xytext=(5, 5), textcoords="offset points")

    ax1.plot(srgb_u, srgb_v, "b-", linewidth=2, label="sRGB Gamut")
    ax1.scatter(u_valid, v_valid, c=colors_uv, s=1, alpha=0.1, marker=".", rasterized=True)

    ax1.set_xlim(-0.05, 0.65)
    ax1.set_ylim(-0.05, 0.65)
    ax1.set_xlabel("u'", fontsize=12)
    ax1.set_ylabel("v'", fontsize=12)
    ax1.set_title("CIE 1976 u'v' Chromaticity Diagram", fontsize=14)
    ax1.set_aspect("equal")
    ax1.legend(loc="upper right")
    ax1.grid(True, alpha=0.3)

    ax2 = axes[1]
    ax2.set_facecolor("white")
    ax2.plot(srgb_a, srgb_b, "b-", linewidth=2, label="sRGB Gamut")
    ax2.axhline(0, color="gray", linestyle="--", alpha=0.5, linewidth=0.8)
    ax2.axvline(0, color="gray", linestyle="--", alpha=0.5, linewidth=0.8)
    ax2.scatter(a_valid, b_valid, c=colors_lab, s=1, alpha=0.1, marker=".", rasterized=True)

    ax2.set_xlim(-130, 130)
    ax2.set_ylim(-130, 130)
    ax2.set_xlabel("a*", fontsize=12)
    ax2.set_ylabel("b*", fontsize=12)
    ax2.set_title("CIELAB a*b* Plane", fontsize=14)
    ax2.set_aspect("equal")
    ax2.legend(loc="upper right")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", format="jpeg")
    plt.close()
    print(f"结果已保存到: {output_path}")
