# -*- coding: utf-8 -*-
"""Обложка: эмбрион пользователя на синем DEEP-фоне; плод справа, слева место под текст."""
import numpy as np
from PIL import Image, ImageFilter

SRC = r"C:\Users\User\Documents\Freelance\Business plan\17917044595435.jpg"
OUT = r"C:\Users\User\Documents\Freelance\Business plan\Готовые документы\assets\cover_user_embryo.png"

W, H = 1920, 1080

# --- 1. исходник → синий фон ---
im = Image.open(SRC).convert("RGB")
# лёгкий кроп, чтобы убрать пустые поля, плод в центре
w, h = im.size
pad_x, pad_y = int(w * 0.06), int(h * 0.04)
im = im.crop((pad_x, pad_y, w - pad_x, h - pad_y))
arr = np.asarray(im).astype(np.float32) / 255.0
lum = arr.max(axis=-1)

# DEEP-градиент для «чёрного»
ch, cw = lum.shape
yy, xx = np.mgrid[0:ch, 0:cw]
v = yy / max(ch - 1, 1)
top_c = np.array([0x0C / 255, 0x38 / 255, 0x5C / 255], dtype=np.float32)
bot_c = np.array([0x06 / 255, 0x1C / 255, 0x32 / 255], dtype=np.float32)
bg_src = top_c[None, None, :] * (1 - v[..., None]) + bot_c[None, None, :] * v[..., None]

t = np.clip((lum - 0.06) / (0.22 - 0.06), 0, 1)
t = t * t * (3 - 2 * t)
star = np.clip((lum - 0.15) / 0.35, 0, 1) * (1 - t)
t_out = np.clip(t + star * 0.55, 0, 1)
src_blue = bg_src * (1 - t_out[..., None]) + arr * t_out[..., None]
src_blue = np.clip(src_blue * 1.05, 0, 1)
src_img = Image.fromarray((src_blue * 255).astype(np.uint8))

# --- 2. холст 16:9: DEEP + плод справа ---
canvas = np.zeros((H, W, 3), dtype=np.float32)
yy, xx = np.mgrid[0:H, 0:W]
u, v = xx / W, yy / H
top_c = np.array([0x0C / 255, 0x38 / 255, 0x5C / 255], dtype=np.float32)
bot_c = np.array([0x06 / 255, 0x1C / 255, 0x32 / 255], dtype=np.float32)
canvas[:] = top_c[None, None, :] * (1 - v[..., None]) + bot_c[None, None, :] * v[..., None]
# мягкое свечение справа
d = np.sqrt(((u - 0.72) ** 2) + ((v - 0.42) ** 2)) / 0.40
glow = np.clip(1 - d, 0, 1) ** 2 * 0.40
canvas = canvas * (1 - glow[..., None]) + np.array([0.22, 0.45, 0.75], dtype=np.float32)[None, None, :] * glow[..., None]
# затемнение слева
shade = np.clip(1.0 - u / 0.50, 0, 1) ** 1.25 * 0.48
canvas = canvas * (1 - shade[..., None])

# плод: масштаб ~58% ширины кадра, правая часть, без шва у правого края
target_w = int(W * 0.58)
sw, sh = src_img.size
target_h = int(target_w * sh / sw)
if target_h > int(H * 0.95):
    target_h = int(H * 0.95)
    target_w = int(target_h * sw / sh)
src_r = src_img.resize((target_w, target_h), Image.LANCZOS)

# мягкая маска краёв (фейд слева/сверху/снизу; справа — без шва)
mask = np.ones((target_h, target_w), dtype=np.float32)
fade_l = int(target_w * 0.28)
fade_t = int(target_h * 0.12)
fade_b = int(target_h * 0.12)
for i in range(fade_l):
    mask[:, i] *= i / max(fade_l, 1)
for j in range(fade_t):
    mask[j, :] *= j / max(fade_t, 1)
for j in range(fade_b):
    mask[target_h - 1 - j, :] *= j / max(fade_b, 1)
# blur маски для гладкого шва
mask_img = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(28))
mask = np.asarray(mask_img).astype(np.float32) / 255.0

# позиция: правый край кадра, вертикально по центру фигуры
ox = W - target_w
oy = int((H - target_h) * 0.40)
# blend
region = canvas[oy:oy + target_h, ox:ox + target_w]
src_a = np.asarray(src_r).astype(np.float32) / 255.0
canvas[oy:oy + target_h, ox:ox + target_w] = region * (1 - mask[..., None]) + src_a * mask[..., None]

canvas = np.clip(canvas, 0, 1)
Image.fromarray((canvas * 255).astype(np.uint8)).save(OUT)
print("saved", OUT)
