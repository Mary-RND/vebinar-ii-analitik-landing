# -*- coding: utf-8 -*-
"""Графики для презентации VitaGen-AI (базовый сценарий, единая сине-фиолетовая гамма)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

OUT = r"C:\Users\User\Documents\Freelance\Business plan\Готовые документы\assets"
os.makedirs(OUT, exist_ok=True)

# палитра в тон презентации
DEEP = "#0A2F4F"
MID = "#145DA0"
BRIGHT = "#2E9ED8"
VIOLET = "#8B6FE8"
PINK = "#E86FB0"
GRID = "#D6EAF7"
TXT = "#1A2A3A"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.edgecolor": GRID,
    "axes.labelcolor": TXT,
    "text.color": TXT,
    "xtick.color": TXT,
    "ytick.color": TXT,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

YEARS = [2026, 2027, 2028, 2029, 2030]
REV = [7.1, 37.7, 113.7, 220.1, 391.1]
EXP = [46.5, 70.5, 106.5, 167.0, 245.0]
EBITDA = [-39.4, -32.8, 7.2, 53.1, 146.1]


def rub(x, _=None):
    return f"{x:,.0f}".replace(",", " ")


# ---------- 1. Выручка vs расходы + EBITDA ----------
fig, ax = plt.subplots(figsize=(8.4, 4.3), dpi=160)
x = range(len(YEARS))
w = 0.38
ax.bar([i - w / 2 for i in x], REV, w, label="Выручка", color=BRIGHT, edgecolor="white")
ax.bar([i + w / 2 for i in x], EXP, w, label="Расходы", color=MID, edgecolor="white")
ax.set_xticks(list(x))
ax.set_xticklabels(YEARS)
ax.set_ylabel("млн ₽")
ax.set_title("Выручка и операционные расходы, млн ₽", fontsize=13, fontweight="bold", color=DEEP, pad=10)
ax2 = ax.twinx()
ax2.plot(list(x), EBITDA, color=VIOLET, lw=2.6, marker="o", ms=7, label="EBITDA", zorder=5)
ax2.axhline(0, color=PINK, lw=1.2, ls="--", alpha=0.8)
ax2.set_ylabel("EBITDA, млн ₽", color=VIOLET)
ax2.tick_params(axis="y", colors=VIOLET)
ax2.grid(False)
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False, fontsize=10)
ax.set_ylim(0, 430)
ax2.set_ylim(-60, 190)
for i, v in enumerate(REV):
    ax.text(i - w / 2, v + 6, f"{v:.0f}", ha="center", fontsize=8.5, color=DEEP, fontweight="bold")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "chart_revenue.png"), bbox_inches="tight")
plt.close(fig)

# ---------- 2. EBITDA + остаток денег ----------
fig, ax = plt.subplots(figsize=(8.4, 4.3), dpi=160)
colors = [PINK if v < 0 else BRIGHT for v in EBITDA]
ax.bar(list(x), EBITDA, 0.55, color=colors, edgecolor="white")
ax.axhline(0, color=TXT, lw=1)
for i, v in enumerate(EBITDA):
    ax.text(i, v + (6 if v >= 0 else -12), f"{v:+.1f}", ha="center", fontsize=9,
            fontweight="bold", color=DEEP if v >= 0 else PINK)
ax.set_xticks(list(x))
ax.set_xticklabels(YEARS)
ax.set_ylabel("млн ₽")
ax.set_ylim(-55, 175)
ax.set_title("EBITDA по годам, млн ₽ (пик кассы покрыт раундами 1+2)", fontsize=13,
             fontweight="bold", color=DEEP, pad=10)
cash = [0.5, 20.8, 34.0, 91.1, 239.2]
ax2 = ax.twinx()
ax2.plot(list(x), cash, color=VIOLET, lw=2.6, marker="s", ms=6, label="Остаток денег")
ax2.set_ylabel("Остаток денег, млн ₽", color=VIOLET)
ax2.tick_params(axis="y", colors=VIOLET)
ax2.grid(False)
ax2.legend(loc="upper left", frameon=False, fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "chart_ebitda.png"), bbox_inches="tight")
plt.close(fig)

# ---------- 3. Клиники и APAC ----------
fig, ax = plt.subplots(figsize=(8.0, 4.0), dpi=160)
clinics = [3, 12, 32, 55, 85]
ax.plot(list(x), clinics, color=MID, lw=3, marker="o", ms=9, label="Клиники-абоненты в РФ")
for i, v in enumerate(clinics):
    ax.annotate(str(v), (i, v), textcoords="offset points", xytext=(0, 10),
                ha="center", fontsize=10, fontweight="bold", color=MID)
apac = [0, 0, 0, 8.0, 25.5]
ax2 = ax.twinx()
ax2.bar(list(x), apac, 0.4, color=VIOLET, alpha=0.85, label="APAC-выручка, млн ₽")
ax2.set_ylabel("APAC, млн ₽", color=VIOLET)
ax2.tick_params(axis="y", colors=VIOLET)
ax2.grid(False)
ax.set_xticks(list(x))
ax.set_xticklabels(YEARS)
ax.set_ylabel("Клиники, шт")
ax.set_ylim(0, 100)
ax.set_title("Клиентская база РФ и выручка APAC (Хайнань/АТР)", fontsize=13,
             fontweight="bold", color=DEEP, pad=10)
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False, fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "chart_clients.png"), bbox_inches="tight")
plt.close(fig)

# ---------- 4. TAM / SAM / SOM ----------
fig, ax = plt.subplots(figsize=(7.4, 4.0), dpi=160)
labels = ["TAM\nклинический рынок\nВРТ РФ", "SAM\nсофт и аналитика\nдля клиник", "SOM 2030\nVitaGen"]
vals = [27.5, 2.5, 0.391]  # млрд ₽ (27.5 = середина 25–30; 2.5 = середина 2–3)
colors = [DEEP, MID, BRIGHT]
bars = ax.barh(labels, vals, color=colors, edgecolor="white", height=0.55)
ax.set_xscale("log")
ax.set_xlabel("млрд ₽/год (логарифмическая шкала)")
ax.set_title("Рынок: TAM → SAM → SOM", fontsize=13, fontweight="bold", color=DEEP, pad=10)
ann = ["25–30 млрд ₽", "2–3 млрд ₽", "391 млн ₽"]
for b, a in zip(bars, ann):
    ax.text(b.get_width() * 1.15, b.get_y() + b.get_height() / 2, a,
            va="center", fontsize=11, fontweight="bold", color=DEEP)
ax.set_xlim(0.2, 120)
ax.invert_yaxis()
ax.grid(axis="y", visible=False)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "chart_market.png"), bbox_inches="tight")
plt.close(fig)

print("charts done")
