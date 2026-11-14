"""Graphique de la diapositive 7 : personnes sans accès basique par continent, 2000 vs 2017 (depuis le modèle)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
d = pd.read_csv(ROOT / "modele/dim_pays.csv")
f = pd.read_csv(ROOT / "modele/fait_pays_annee.csv").merge(d, on="iso3")
t = f[f.year.isin([2000, 2017])].pivot_table(index="continent", columns="year", values="pop_without_basic", aggfunc="sum") / 1e6
t = t.sort_values(2017)

plt.rcParams.update({"font.family": "Arial", "font.size": 13, "text.color": "#0b2236", "axes.labelcolor": "#5f7488"})
fig, ax = plt.subplots(figsize=(7.9, 5.4), dpi=220)
y = range(len(t)); h = 0.38
ax.barh([i + h / 2 for i in y], t[2000], h, color="#9ec5f4", label="2000")
ax.barh([i - h / 2 for i in y], t[2017], h, color="#1c5cab", label="2017")
for i, (a, b) in enumerate(zip(t[2000], t[2017])):
    ax.text(a + 5, i + h / 2, f"{a:.0f}", va="center", fontsize=11, color="#5f7488")
    ax.text(b + 5, i - h / 2, f"{b:.0f}", va="center", fontsize=12, color="#0b2236", weight="bold")
ax.set_yticks(list(y), t.index)
ax.set_xlim(0, 430); ax.set_xlabel("millions de personnes sans accès basique")
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#d3e0eb"); ax.tick_params(left=False, colors="#0b2236")
ax.xaxis.grid(True, color="#d3e0eb", lw=0.8); ax.set_axisbelow(True)
ax.legend(loc="lower right", frameon=False, reverse=True)
fig.tight_layout()
fig.savefig(ROOT / "livrables/captures/graphique_continents.png", facecolor="white")
