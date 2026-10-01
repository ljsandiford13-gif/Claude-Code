import statistics as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from data2 import computed, STORE_A, STORE_B, CATEGORIES

OUT = "/tmp/claude-0/-home-user-Claude-Code/44dd45fb-e13e-5e85-ae62-01673943b147/scratchpad/build/charts2"
import os; os.makedirs(OUT, exist_ok=True)

BLUE, ORANGE, AQUA, RED = "#2a78d6", "#eb6834", "#1baf7a", "#e34948"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e6e5e1"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False})

rows = computed()
val = rows

def clean(ax, zero=True):
    ax.grid(axis="x" if ax.get_xlim()[0] < 0 else "y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)

# ---------- Chart 1: mean & median by category ----------
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)
cats = CATEGORIES + ["All"]
for ax, stat, ttl in ((axes[0], st.mean, "Mean"), (axes[1], st.median, "Median")):
    a_vals, b_vals = [], []
    for c in cats:
        v = val if c == "All" else [d for d in val if d["cat"] == c]
        a_vals.append(stat([d["ff_a"] for d in v]) * 100)
        b_vals.append(stat([d["ff_b"] for d in v]) * 100)
    x = range(len(cats)); w = 0.36
    ba = ax.bar([i - w/2 for i in x], a_vals, w, color=ORANGE, label=f"vs {STORE_A}")
    bb = ax.bar([i + w/2 for i in x], b_vals, w, color=AQUA, label=f"vs {STORE_B}")
    for bars in (ba, bb):
        for b in bars:
            h = b.get_height()
            ax.text(b.get_x() + b.get_width()/2, h - 1.2 if h < 0 else h + 1.2, f"{h:+.0f}%", ha="center",
                    va="top" if h < 0 else "bottom", fontsize=8, color=INK)
    ax.axhline(0, color=INK2, linewidth=0.8)
    ax.set_xticks(list(x)); ax.set_xticklabels(cats)
    ax.set_title(f"{ttl} % difference", fontsize=10, color=INK, loc="left")
    ax.grid(axis="y", color=GRID, linewidth=0.8); ax.set_axisbelow(True); ax.tick_params(length=0)
    ax.set_ylim(-50, 5)
axes[0].set_ylabel("Food First relative to supermarket (%)")
axes[0].legend(loc="lower left", frameon=False, fontsize=8)
fig.suptitle("Food First price relative to each supermarket, by category (negative = Food First cheaper)", fontsize=10, color=INK, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0, 1, 0.94))
fig.savefig(f"{OUT}/chart_category.png", dpi=200); plt.close(fig)

# ---------- Chart 2: matched basket ----------
sf = sum(d["ff"] for d in val); sa = sum(d["a"] for d in val); sb = sum(d["b"] for d in val)
fig, ax = plt.subplots(figsize=(5.0, 2.4))
names = ["Food First", STORE_A, STORE_B]; vals = [sf, sa, sb]; cols = [BLUE, ORANGE, AQUA]
bars = ax.barh(names[::-1], vals[::-1], color=cols[::-1], height=0.55)
for b, v in zip(bars, vals[::-1]):
    ax.text(v + 4, b.get_y() + b.get_height()/2, f"BBD {v:,.2f}", va="center", fontsize=9, color=INK)
ax.set_xlim(0, max(vals) * 1.25)
ax.set_xlabel("Sum of standardised prices, 36 included items (BBD)")
ax.grid(axis="x", color=GRID, linewidth=0.8); ax.set_axisbelow(True); ax.tick_params(length=0)
ax.set_title("Indicative matched-basket total", fontsize=10, color=INK, loc="left")
fig.tight_layout()
fig.savefig(f"{OUT}/chart_basket.png", dpi=200); plt.close(fig)

# ---------- Chart 3: cheapest store ----------
from collections import Counter
cnt = Counter(d["cheapest"] for d in val)
fig, ax = plt.subplots(figsize=(5.0, 2.2))
bars = ax.barh(names[::-1], [cnt[n] for n in names[::-1]], color=cols[::-1], height=0.55)
for b, n in zip(bars, names[::-1]):
    ax.text(cnt[n] + 0.4, b.get_y() + b.get_height()/2, f"{cnt[n]} of {len(val)} ({cnt[n]/len(val):.0%})", va="center", fontsize=9, color=INK)
ax.set_xlim(0, len(val)); ax.set_xlabel("Items where this store had the lowest standardised price")
ax.grid(axis="x", color=GRID, linewidth=0.8); ax.set_axisbelow(True); ax.tick_params(length=0)
ax.set_title("Cheapest store, item by item", fontsize=10, color=INK, loc="left")
fig.tight_layout()
fig.savefig(f"{OUT}/chart_cheapest.png", dpi=200); plt.close(fig)

# ---------- Chart 4: item-level, all included items, sorted ----------
srt = sorted(val, key=lambda d: d["ff_a"])
fig, ax = plt.subplots(figsize=(7.2, 9.0))
y = range(len(srt)); h = 0.38
ax.barh([i + h/2 for i in y], [d["ff_a"]*100 for d in srt], h, color=ORANGE, label=f"vs {STORE_A}")
ax.barh([i - h/2 for i in y], [d["ff_b"]*100 for d in srt], h, color=AQUA, label=f"vs {STORE_B}")
ax.set_yticks(list(y)); ax.set_yticklabels([f"{d['item']}  ({d['cat'][:3]})" for d in srt], fontsize=8)
ax.set_xlim(-95, 140)
ax.invert_yaxis()
ax.axvline(0, color=INK2, linewidth=0.8)
ax.set_xlabel("Food First price relative to supermarket (%)  |  negative = Food First cheaper")
ax.grid(axis="x", color=GRID, linewidth=0.8); ax.set_axisbelow(True); ax.tick_params(length=0)
ax.legend(loc="upper right", frameon=False, fontsize=8)
ax.set_title("Item-level price difference, 36 like-for-like items", fontsize=10, color=INK, loc="left")
for i, d in enumerate(srt):
    if d["ff_a"] > 0.6:
        v = d["ff_a"]*100
        ax.text(v + 2, i + h/2, f"{v:+.0f}%", va="center", ha="left", fontsize=7, color=INK)
    if d["ff_a"] < -0.6:
        v = d["ff_a"]*100
        ax.text(v - 2, i + h/2, f"{v:+.0f}%", va="center", ha="right", fontsize=7, color=INK)
fig.tight_layout()
fig.savefig(f"{OUT}/chart_items.png", dpi=200); plt.close(fig)
print("charts written")
