# -*- coding: utf-8 -*-
"""Иллюстрации для презентации VitaGen-AI в стиле исходной (фиолетово-синие медицинские абстракции)."""
import math
import random
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from PIL import Image, ImageFilter

OUT = r"C:\Users\User\Documents\Freelance\Business plan\Готовые документы\assets"
import os
os.makedirs(OUT, exist_ok=True)

random.seed(42)
np.random.seed(42)


def radial_gradient(size, cx, cy, r, color, alpha_peak=0.95, bg=(0.04, 0.05, 0.16)):
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


embryo_dish()
dna_helix()
icsi()
cell_division()
gamete_banner()
print("assets done:", os.listdir(OUT))
