# -*- coding: utf-8 -*-
"""Иллюстрации для презентации VitaGen-AI в стиле исходной (полигонный плод, сине-розовое свечение)."""
import math
import random
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from PIL import Image, ImageFilter
from scipy.spatial import Delaunay

OUT = r"C:\Users\User\Documents\Freelance\Business plan\Готовые документы\assets"
import os
os.makedirs(OUT, exist_ok=True)

random.seed(42)
np.random.seed(42)

DEEP_RGB = (0x0A / 255, 0x2F / 255, 0x4F / 255)


def radial_gradient(size, cx, cy, r, color, alpha_peak=0.95, bg=DEEP_RGB):
    """Мягкое радиальное свечение на тёмном фоне."""
    w, h = size
    y, x = np.mgrid[0:h, 0:w]
    d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / max(r, 1)
    a = np.clip(1 - d, 0, 1) ** 2 * alpha_peak
    img = np.zeros((h, w, 3))
    for i in range(3):
        img[..., i] = bg[i] * (1 - a) + color[i] * a
    return img


def add_noise(img, amount=0.03):
    n = np.random.normal(0, amount, img.shape)
    return np.clip(img + n, 0, 1)


def save_img(arr, name):
    Image.fromarray((arr * 255).astype(np.uint8)).save(os.path.join(OUT, name))


# ---------- 1. Обложка: градиент + полигонный плод ----------
def _ellipse_field(xx, yy, cx, cy, rx, ry, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)
    x = (xx - cx) * c + (yy - cy) * s
    y = -(xx - cx) * s + (yy - cy) * c
    return (x / max(rx, 1)) ** 2 + (y / max(ry, 1)) ** 2


def _fetus_mask(w, h, fx, fy, fw):
    """Силуэт плода (поза эмбриона) через metaball-поле: плавное слияние эллипсоидов."""
    yy, xx = np.mgrid[0:h, 0:w]
    fig_w = fw * w
    fig_h = fig_w * 1.22
    ox, oy = fx * w - fig_w * 0.5, fy * h - fig_h * 0.5

    def P(u, v):
        return ox + u * fig_w, oy + v * fig_h

    # (u, v, rx, ry, rot, strength) — анатомия: череп → шея → грудь → таз → ноги к груди → руки к лицу
    parts = [
        # череп
        (0.55, 0.16, 0.26, 0.20, -0.20, 1.20),
        (0.66, 0.22, 0.18, 0.16, 0.10, 1.00),
        # лицо / подбородок
        (0.44, 0.27, 0.14, 0.12, -0.45, 1.00),
        # шея + плечевой пояс (заполняем «дырку»)
        (0.58, 0.36, 0.14, 0.12, 0.40, 1.05),
        (0.50, 0.40, 0.12, 0.10, 0.10, 0.95),
        # грудная клетка (спина — дуга)
        (0.62, 0.46, 0.17, 0.17, 0.20, 1.10),
        (0.58, 0.56, 0.15, 0.14, -0.05, 1.05),
        # живот
        (0.48, 0.60, 0.15, 0.14, -0.20, 1.05),
        # таз
        (0.50, 0.72, 0.14, 0.12, 0.00, 1.05),
        # ближнее бедро → колено к груди
        (0.38, 0.62, 0.17, 0.11, -0.90, 1.05),
        (0.28, 0.50, 0.16, 0.09, -1.20, 1.00),
        # ближняя голень / стопа
        (0.20, 0.40, 0.12, 0.07, -1.10, 0.90),
        (0.14, 0.34, 0.08, 0.055, -0.85, 0.80),
        # дальнее бедро (чуть смещено)
        (0.44, 0.70, 0.15, 0.10, -0.75, 0.95),
        (0.32, 0.62, 0.14, 0.08, -1.05, 0.90),
        (0.22, 0.54, 0.10, 0.06, -1.00, 0.75),
        # плечо и рука к лицу (плотнее, без разрывов)
        (0.52, 0.42, 0.12, 0.09, -0.30, 1.00),
        (0.44, 0.38, 0.13, 0.08, -0.70, 1.00),
        (0.38, 0.34, 0.10, 0.07, -0.40, 0.95),
        # кисть у щеки
        (0.36, 0.30, 0.07, 0.055, -0.20, 0.90),
        # мостик: грудь ↔ живот ↔ бедро
        (0.52, 0.52, 0.13, 0.12, 0.00, 1.00),
        (0.46, 0.66, 0.12, 0.10, -0.30, 0.95),
    ]
    # metaball field: сумма (1 - d^2)^2 внутри радиуса
    field = np.zeros((h, w))
    for u, v, rx, ry, rot, s in parts:
        cx, cy = P(u, v)
        # нормализованное расстояние в повёрнутом эллипсе
        c, sn = math.cos(rot), math.sin(rot)
        dx, dy = xx - cx, yy - cy
        lx = (dx * c + dy * sn) / max(rx * fig_w, 1)
        ly = (-dx * sn + dy * c) / max(ry * fig_h, 1)
        d2 = lx * lx + ly * ly
        field += s * np.clip(1.0 - d2, 0, 1) ** 2
    # порог + сглаживание
    thr = 0.50
    mask = np.clip((field - thr) * 4.0, 0, 1)
    # gaussian blur для гладкого силуэта
    try:
        from scipy.ndimage import gaussian_filter
        mask = gaussian_filter(mask, sigma=max(2, fig_w * 0.010))
        mask = np.clip((mask - 0.22) * 3.5, 0, 1)
    except Exception:
        pass
    return mask, (ox, oy, fig_w, fig_h)


def _sample_inside(mask, n, rng, pad=8):
    h, w = mask.shape
    pts = []
    tries = 0
    while len(pts) < n and tries < n * 80:
        tries += 1
        x = rng.randint(pad, w - pad)
        y = rng.randint(pad, h - pad)
        # соседняя маска > порога
        if mask[y, x] > 0.45:
            # не слишком близко к уже выбранным
            ok = True
            for px, py in pts[-40:]:
                if (px - x) ** 2 + (py - y) ** 2 < 28 ** 2:
                    ok = False
                    break
            if ok:
                pts.append((float(x), float(y)))
    return np.array(pts) if pts else np.zeros((0, 2))


def cover_slide(w=1920, h=1080, name="cover_slide.png"):
    """Полноэкранный фон обложки: градиент DEEP + полигонный плод справа (как слайд 4 исходника)."""
    # --- градиентный фон ---
    y, x = np.mgrid[0:h, 0:w]
    u, v = x / w, y / h
    # диагональ DEEP → чуть темнее снизу-слева, глубже справа
    top = np.array([0x0C / 255, 0x38 / 255, 0x5C / 255])
    bot = np.array([0x06 / 255, 0x1C / 255, 0x32 / 255])
    img = np.zeros((h, w, 3))
    t = np.clip(0.35 * u + 0.65 * v, 0, 1)[..., None]
    img[:] = top * (1 - t) + bot * t
    # мягкое бирюзовое свечение справа-сверху (как в исходнике)
    for cx, cy, r, col, a in [
        (0.82, 0.28, 0.38, (0.55, 0.85, 1.0), 0.45),
        (0.90, 0.55, 0.32, (0.25, 0.45, 0.85), 0.35),
        (0.12, 0.15, 0.25, (0.35, 0.2, 0.7), 0.25),
    ]:
        d = np.sqrt(((x - cx * w) / (r * w)) ** 2 + ((y - cy * h) / (r * w)) ** 2)
        aa = np.clip(1 - d, 0, 1) ** 2 * a
        for i in range(3):
            img[..., i] = np.clip(img[..., i] * (1 - aa) + col[i] * aa, 0, 1)

    # --- плод (справа) ---
    mask, (ox, oy, fig_w, fig_h) = _fetus_mask(w, h, fx=0.66, fy=0.46, fw=0.40)
    # тело: тёмное с фиолетовым подтоном (полупрозрачное, как в референсе)
    body_a = mask * 0.38
    body_col = np.stack([
        0.50 * mask ** 0.95,
        0.14 * mask ** 1.15,
        0.70 * mask ** 0.75,
    ], axis=-1)
    # тонкий контур: розовый сзади (спина/затылок), бирюза спереди (лицо/колени)
    gy, gx = np.gradient(mask)
    edge = np.sqrt(gx ** 2 + gy ** 2)
    edge = edge / (edge.max() + 1e-6)
    # узкий ridge по границе
    ridge = np.exp(-((mask - 0.5) ** 2) / (2 * 0.12 ** 2)) * np.clip(edge * 8, 0, 1)
    nx = gx / (edge + 1e-6)
    front = np.clip(-nx, 0, 1) * ridge
    back = np.clip(nx, 0, 1) * ridge
    cyan = np.stack([0.15 * front, 0.80 * front, 1.0 * front], axis=-1)
    pink = np.stack([1.0 * back, 0.20 * back, 0.50 * back], axis=-1)
    for i in range(3):
        img[..., i] = np.clip(img[..., i] * (1 - body_a) + body_col[..., i] * body_a, 0, 1)
        img[..., i] = np.clip(img[..., i] + cyan[..., i] * 0.75, 0, 1)
        img[..., i] = np.clip(img[..., i] + pink[..., i] * 0.95, 0, 1)

    # полигонная сетка + узлы-искры (как на слайде 4)
    rng = random.Random(17)
    pts = _sample_inside(mask, 110, rng)
    if len(pts) >= 4:
        tri = Delaunay(pts)
        for simplex in tri.simplices:
            p0, p1, p2 = pts[simplex]
            for a, b in ((p0, p1), (p1, p2), (p2, p0)):
                # длина ребра — короткие ярче
                L = math.hypot(b[0] - a[0], b[1] - a[1])
                if L > 90:
                    continue
                op = 0.35 if L < 45 else 0.2
                # ближе к краю тела — розовое, внутри — бирюзовое
                mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
                mi = int(np.clip(my, 0, h - 1)), int(np.clip(mx, 0, w - 1))
                mval = mask[mi[0], mi[1]]
                col = (1.0, 0.35, 0.55) if mval < 0.75 else (0.35, 0.85, 1.0)
                # рисуем ребро точками (numpy-safe)
                steps = int(max(2, L / 3))
                for s in range(steps + 1):
                    t = s / steps
                    px = a[0] + (b[0] - a[0]) * t
                    py = a[1] + (b[1] - a[1]) * t
                    ix, iy = int(px), int(py)
                    if 1 <= ix < w - 1 and 1 <= iy < h - 1:
                        r = 1.5
                        y0, y1 = max(0, iy - 2), min(h, iy + 3)
                        x0, x1 = max(0, ix - 2), min(w, ix + 3)
                        yy2, xx2 = np.mgrid[y0:y1, x0:x1]
                        dd = np.sqrt((xx2 - px) ** 2 + (yy2 - py) ** 2)
                        al = np.clip(1 - dd / r, 0, 1) * op
                        for ci in range(3):
                            img[y0:y1, x0:x1, ci] = np.clip(
                                img[y0:y1, x0:x1, ci] * (1 - al) + col[ci] * al, 0, 1)
        # узлы-искры
        for i in range(len(pts)):
            px, py = pts[i]
            pink = rng.random() < 0.45
            col = (1.0, 0.4, 0.65) if pink else (0.5, 0.9, 1.0)
            sr = rng.uniform(2.0, 5.5) if pink else rng.uniform(1.5, 3.5)
            y0, y1 = max(0, int(py - sr * 2)), min(h, int(py + sr * 2) + 1)
            x0, x1 = max(0, int(px - sr * 2)), min(w, int(px + sr * 2) + 1)
            if y1 <= y0 or x1 <= x0:
                continue
            yy2, xx2 = np.mgrid[y0:y1, x0:x1]
            dd = np.sqrt((xx2 - px) ** 2 + (yy2 - py) ** 2)
            core = np.exp(-((dd / (sr * 0.55)) ** 2))
            glow = np.exp(-((dd / (sr * 2.2)) ** 2)) * 0.45
            al = np.clip(core + glow, 0, 1)
            for ci in range(3):
                img[y0:y1, x0:x1, ci] = np.clip(
                    img[y0:y1, x0:x1, ci] * (1 - al) + col[ci] * al, 0, 1)

    # рассыпанные вокруг искры
    for _ in range(50):
        px = rng.uniform(ox, ox + fig_w)
        py = rng.uniform(oy, oy + fig_h)
        if not (0 <= px < w and 0 <= py < h):
            continue
        col = (1.0, 0.35, 0.55) if rng.random() < 0.5 else (0.4, 0.85, 1.0)
        sr = rng.uniform(0.8, 2.2)
        y0, y1 = max(0, int(py - 3)), min(h, int(py + 4))
        x0, x1 = max(0, int(px - 3)), min(w, int(px + 4))
        if y1 <= y0 or x1 <= x0:
            continue
        yy2, xx2 = np.mgrid[y0:y1, x0:x1]
        dd = np.sqrt((xx2 - px) ** 2 + (yy2 - py) ** 2)
        al = np.clip(1 - dd / sr, 0, 1) * 0.7
        for ci in range(3):
            img[y0:y1, x0:x1, ci] = np.clip(
                img[y0:y1, x0:x1, ci] * (1 - al) + col[ci] * al, 0, 1)

    # лёгкий шум только в градиенте (мелкий) — края картинки ≈ плоские для бесшовности у текста
    # не шумим: фон должен ложиться ровно под текст
    save_img(np.clip(img, 0, 1), name)


def cover_embryo_tile(w=1000, h=1200, name="cover_embryo.png"):
    """Компактная плитка плода на чистом DEEP (если нужна отдельная иллюстрация)."""
    img = np.tile(np.array(DEEP_RGB).reshape(1, 1, 3), (h, w, 1))
    mask, _ = _fetus_mask(w, h, fx=0.5, fy=0.5, fw=0.70)
    body_a = mask * 0.42
    body_col = np.stack([0.52 * mask ** 0.95, 0.16 * mask ** 1.15, 0.75 * mask ** 0.75], -1)
    gy, gx = np.gradient(mask)
    edge = np.sqrt(gx ** 2 + gy ** 2)
    edge = edge / (edge.max() + 1e-6)
    ridge = np.exp(-((mask - 0.5) ** 2) / (2 * 0.12 ** 2)) * np.clip(edge * 8, 0, 1)
    nx = gx / (edge + 1e-6)
    front = np.clip(-nx, 0, 1) * ridge
    back = np.clip(nx, 0, 1) * ridge
    cyan = np.stack([0.15 * front, 0.80 * front, 1.0 * front], -1)
    pink = np.stack([1.0 * back, 0.20 * back, 0.50 * back], -1)
    for i in range(3):
        img[..., i] = np.clip(img[..., i] * (1 - body_a) + body_col[..., i] * body_a, 0, 1)
        img[..., i] = np.clip(img[..., i] + cyan[..., i] * 0.7, 0, 1)
        img[..., i] = np.clip(img[..., i] + pink[..., i] * 0.9, 0, 1)
    rng = random.Random(3)
    pts = _sample_inside(mask, 90, rng)
    if len(pts) >= 4:
        tri = Delaunay(pts)
        for simplex in tri.simplices:
            p0, p1, p2 = pts[simplex]
            for a, b in ((p0, p1), (p1, p2), (p2, p0)):
                L = math.hypot(b[0] - a[0], b[1] - a[1])
                if L > 70:
                    continue
                steps = max(2, int(L / 3))
                for s in range(steps + 1):
                    t = s / steps
                    px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                    ix, iy = int(px), int(py)
                    if 1 <= ix < w - 1 and 1 <= iy < h - 1:
                        mi = mask[iy, ix]
                        col = (1.0, 0.4, 0.6) if mi < 0.75 else (0.4, 0.9, 1.0)
                        y0, y1 = max(0, iy - 2), min(h, iy + 3)
                        x0, x1 = max(0, ix - 2), min(w, ix + 3)
                        yy2, xx2 = np.mgrid[y0:y1, x0:x1]
                        dd = np.sqrt((xx2 - px) ** 2 + (yy2 - py) ** 2)
                        al = np.clip(1 - dd / 1.6, 0, 1) * 0.3
                        for ci in range(3):
                            img[y0:y1, x0:x1, ci] = np.clip(
                                img[y0:y1, x0:x1, ci] * (1 - al) + col[ci] * al, 0, 1)
        for i in range(len(pts)):
            px, py = pts[i]
            pink = rng.random() < 0.4
            col = (1.0, 0.45, 0.7) if pink else (0.55, 0.95, 1.0)
            sr = rng.uniform(1.8, 4.5)
            y0, y1 = max(0, int(py - 5)), min(h, int(py + 6))
            x0, x1 = max(0, int(px - 5)), min(w, int(px + 6))
            if y1 <= y0 or x1 <= x0:
                continue
            yy2, xx2 = np.mgrid[y0:y1, x0:x1]
            dd = np.sqrt((xx2 - px) ** 2 + (yy2 - py) ** 2)
            al = np.clip(np.exp(-((dd / (sr * 0.6)) ** 2)) + 0.4 * np.exp(-((dd / (sr * 2)) ** 2)), 0, 1)
            for ci in range(3):
                img[y0:y1, x0:x1, ci] = np.clip(
                    img[y0:y1, x0:x1, ci] * (1 - al) + col[ci] * al, 0, 1)
    save_img(np.clip(img, 0, 1), name)


# ---------- 1. Эмбрион в петри (как обложка исходной) ----------
def embryo_dish(w=1600, h=1000, name="cover_embryo.png"):
    DEEP_RGB = (0x0A / 255, 0x2F / 255, 0x4F / 255)  # фон в цвет обложки
    img = radial_gradient((w, h), cx=int(w * 0.62), cy=int(h * 0.5),
                          r=int(h * 0.45), color=(0.55, 0.45, 0.95), alpha_peak=0.85,
                          bg=DEEP_RGB)
    # тело эмбриона
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy, R = w * 0.62, h * 0.5, h * 0.22
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    body = np.clip(1 - d / R, 0, 1) ** 0.7
    core = np.exp(-((d / (R * 0.55)) ** 2))
    for i, col in enumerate((0.78, 0.7, 1.0)):
        img[..., i] = np.clip(img[..., i] * (1 - body) + col * body * (0.5 + 0.5 * core), 0, 1)
    # зона пеллюцида — светлый ореол
    halo = np.exp(-(((d - R * 0.85) / (R * 0.18)) ** 2))
    for i, col in enumerate((0.85, 0.9, 1.0)):
        img[..., i] = np.clip(img[..., i] + col * halo * 0.35, 0, 1)
    # бластомеры
    rng = random.Random(7)
    for k in range(8):
        ang = 2 * math.pi * k / 8 + 0.2
        bx, by = cx + math.cos(ang) * R * 0.42, cy + math.sin(ang) * R * 0.42
        bd = np.sqrt((xx - bx) ** 2 + (yy - by) ** 2)
        blob = np.clip(1 - bd / (R * 0.34), 0, 1) ** 1.3
        tint = 0.75 + rng.random() * 0.2
        for i, col in enumerate((0.9 * tint, 0.82 * tint, 1.0)):
            img[..., i] = np.clip(img[..., i] * (1 - blob * 0.55) + col * blob * 0.55, 0, 1)
        edge = np.exp(-(((bd - R * 0.34) / (R * 0.05)) ** 2))
        for i, col in enumerate((1.0, 0.95, 1.0)):
            img[..., i] = np.clip(img[..., i] + col * edge * 0.25, 0, 1)
    # зона пикассо / иглы (ICSI)
    for i in range(60):
        t = i / 60
        px = w * 0.12 + t * w * 0.32
        py = h * 0.12 + t * h * 0.28 + math.sin(t * 8) * 6
        yy2 = np.clip(1 - np.sqrt((xx - px) ** 2 + (yy - py) ** 2) / 8, 0, 1)
        for c in range(3):
            img[..., c] = np.clip(img[..., c] + (0.75 + 0.2 * c) * yy2 * 0.35, 0, 1)
    # пиково-синий блик (внутри кадра, без среза краем)
    gl = np.exp(-(((xx - w * 0.78) ** 2 + (yy - h * 0.2) ** 2) / (2 * (h * 0.09) ** 2)))
    for i, col in enumerate((1.0, 0.3, 0.6)):
        img[..., i] = np.clip(img[..., i] + col * gl * 0.35, 0, 1)
    save_img(img, name)  # без шума — бесшовный фон на слайде


# ---------- 2. ДНК-спираль ----------
def dna_helix(w=1200, h=1200, name="dna.png"):
    DEEP_RGB = (0x0A / 255, 0x2F / 255, 0x4F / 255)
    img = radial_gradient((w, h), cx=w // 2, cy=h // 2, r=int(h * 0.45),
                          color=(0.35, 0.25, 0.85), alpha_peak=0.6, bg=DEEP_RGB)
    fig = plt.figure(figsize=(w / 100, h / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.imshow(img, extent=[0, 1, 0, 1])
    ts = np.linspace(0, 6 * np.pi, 500)
    x1 = 0.5 + 0.28 * np.sin(ts)
    x2 = 0.5 - 0.28 * np.sin(ts)
    y = ts / (6 * np.pi)
    depth = np.cos(ts)
    # перекладины
    for i in range(0, len(ts), 8):
        op = 0.3 + 0.5 * (depth[i] + 1) / 2
        ax.plot([x1[i], x2[i]], [y[i], y[i]], color=(0.6, 0.85, 1.0), lw=1.2, alpha=op)
    ax.plot(x1, y, color=(0.85, 0.6, 1.0), lw=5, solid_capstyle="round", alpha=0.95)
    ax.plot(x2, y, color=(0.4, 0.7, 1.0), lw=5, solid_capstyle="round", alpha=0.95)
    for i in range(0, len(ts), 12):
        s = 30 + 40 * (depth[i] + 1) / 2
        ax.scatter([x1[i]], [y[i]], s=s, color=(1, 0.85, 1.0), zorder=5, alpha=0.9)
        ax.scatter([x2[i]], [y[i]], s=s, color=(0.7, 0.95, 1.0), zorder=5, alpha=0.9)
    fig.savefig(os.path.join(OUT, name), transparent=True)
    plt.close(fig)


# ---------- 3. ICSI-микроинъекция ----------
def icsi(w=1400, h=900, name="icsi.png"):
    img = radial_gradient((w, h), cx=int(w * 0.42), cy=int(h * 0.55),
                          r=int(h * 0.45), color=(0.5, 0.4, 0.9), alpha_peak=0.8)
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy, R = w * 0.42, h * 0.55, h * 0.28
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    body = np.clip(1 - d / R, 0, 1) ** 0.6
    for i, col in enumerate((0.9, 0.85, 1.0)):
        img[..., i] = np.clip(img[..., i] * (1 - body) + col * body * 0.7, 0, 1)
    halo = np.exp(-(((d - R) / (R * 0.12)) ** 2))
    for i, col in enumerate((1.0, 0.7, 0.9)):
        img[..., i] = np.clip(img[..., i] + col * halo * 0.4, 0, 1)
    # яйцеклетка — ядро
    core = np.exp(-((d / (R * 0.4)) ** 2))
    for i, col in enumerate((0.95, 0.75, 1.0)):
        img[..., i] = np.clip(img[..., i] + col * core * 0.3, 0, 1)
    # игла ICSI
    ax_pts = []
    for t in np.linspace(0, 1, 200):
        px = w * 0.92 - t * (w * 0.5)
        py = h * 0.2 + t * (h * 0.33) + math.sin(t * 3) * 4
        ax_pts.append((px, py))
    for (px, py) in ax_pts:
        dd = np.sqrt((xx - px) ** 2 + (yy - py) ** 2)
        needle = np.clip(1 - dd / 7, 0, 1)
        for i, col in enumerate((1.0, 0.45, 0.7)):
            img[..., i] = np.clip(img[..., i] + col * needle * 0.5, 0, 1)
    # пиксельный блик
    gl = np.exp(-(((xx - w * 0.2) ** 2 + (yy - h * 0.25) ** 2) / (2 * (h * 0.1) ** 2)))
    for i, col in enumerate((0.4, 0.7, 1.0)):
        img[..., i] = np.clip(img[..., i] + col * gl * 0.35, 0, 1)
    save_img(add_noise(img), name)


# ---------- 4. Абстрактный «взрыв» бластомеров / рост ----------
def cell_division(w=1200, h=900, name="division.png"):
    img = radial_gradient((w, h), cx=w // 2, cy=h // 2, r=int(h * 0.6),
                          color=(0.3, 0.2, 0.75), alpha_peak=0.7)
    yy, xx = np.mgrid[0:h, 0:w]
    centers = [(0.35, 0.5, 0.16), (0.62, 0.5, 0.16), (0.48, 0.72, 0.12), (0.48, 0.28, 0.12)]
    for (fx, fy, fr) in centers:
        cx, cy, R = w * fx, h * fy, h * fr
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        body = np.clip(1 - d / R, 0, 1) ** 0.8
        for i, col in enumerate((0.85, 0.7, 1.0)):
            img[..., i] = np.clip(img[..., i] * (1 - body * 0.9) + col * body * 0.9, 0, 1)
        edge = np.exp(-(((d - R) / (R * 0.1)) ** 2))
        for i, col in enumerate((0.5, 0.85, 1.0)):
            img[..., i] = np.clip(img[..., i] + col * edge * 0.5, 0, 1)
    save_img(add_noise(img), name)


# ---------- 5. Фон-полоса для KPI / донорство ----------
def gamete_banner(w=1600, h=500, name="banner.png"):
    img = radial_gradient((w, h), cx=int(w * 0.3), cy=h // 2, r=int(h * 0.8),
                          color=(0.4, 0.3, 0.9), alpha_peak=0.75)
    yy, xx = np.mgrid[0:h, 0:w]
    # поток частиц
    rng = random.Random(11)
    for _ in range(40):
        px, py = rng.uniform(0, w), rng.uniform(0, h)
        R = rng.uniform(6, 22)
        d = np.sqrt((xx - px) ** 2 + (yy - py) ** 2)
        body = np.clip(1 - d / R, 0, 1) ** 0.7
        col = rng.choice([(0.7, 0.5, 1.0), (0.4, 0.8, 1.0), (1.0, 0.5, 0.8)])
        for i in range(3):
            img[..., i] = np.clip(img[..., i] * (1 - body * 0.6) + col[i] * body * 0.6, 0, 1)
    save_img(add_noise(img), name)


cover_slide()
cover_embryo_tile()
dna_helix()
icsi()
cell_division()
gamete_banner()
print("assets done:", os.listdir(OUT))
