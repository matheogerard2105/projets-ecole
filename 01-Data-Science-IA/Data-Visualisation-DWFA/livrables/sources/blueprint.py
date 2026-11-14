"""Maquette basse fidélité (blueprint) des 3 vues du tableau de bord DWFA."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parents[1] / "captures"
INK, LINE, FILL, ACC = "#0b2236", "#7d93a8", "#eef4f9", "#1c5cab"

def box(ax, x, y, w, h, title, kind="", fill=FILL, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.6", fc=fill, ec=LINE, lw=1.2))
    ax.text(x + 1.2, y + h - 1.6, title, fontsize=9.5, color=INK, va="top", weight="bold" if bold or kind else "normal", wrap=True)
    if kind:
        ax.text(x + w / 2, y + h / 2 - 1, kind, fontsize=8.5, color=ACC, ha="center", va="center", style="italic")

def frame(title, sub):
    fig, ax = plt.subplots(figsize=(11, 7.6), dpi=170)
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    ax.text(0, 99, title, fontsize=15, weight="bold", color=INK, va="top")
    ax.text(0, 94.8, sub, fontsize=9.5, color=LINE, va="top")
    return fig, ax

def common(ax, filters):
    for k, t in enumerate(["1 Monde", "2 Continent", "3 Pays"]):
        box(ax, k * 12, 86, 11, 4.5, t, fill="#ffffff")
    box(ax, 0, 79, 100, 6, "Filtres :  " + "   ·   ".join(filters), fill="#ffffff")
    box(ax, 0, 72.5, 100, 5.5, "Phrase clé (chiffre principal de la vue, mis à jour avec les filtres)", fill="#ffffff")
    for k, t in enumerate(["Population", "Accès basique", "Accès sûr", "Sans accès", "Mortalité WASH", "Urbanisation", "Stabilité"]):
        box(ax, k * 14.4, 64, 13.4, 7.3, t, fill="#ffffff")

def domains(ax, y):
    for k, (t, s) in enumerate([("D1 Création", "scatter : urbanisation × accès basique\n(taille = pers. sans accès)"),
                                ("D2 Modernisation", "scatter : accès basique × accès sûr\n(diagonale = pas d'écart)"),
                                ("D3 Consulting", "scatter : stabilité × score d'efficacité\n(accès + faible mortalité)")]):
        box(ax, k * 33.7, y, 32.6, 14, t, s)

FILTERS = ["Année (temporel)", "Zone T/U/R (qualitatif)", "Stabilité min. (quantitatif)"]
views = [
    ("vue_monde", "Vue 1 · Monde", "Agrégation mondiale (moyennes pondérées par la population)", FILTERS, [
        (0, 37, 64, 26, "Carte du monde : accès basique par pays", "carte choroplèthe (géographique)"),
        (65, 37, 35, 26, "Personnes sans accès par continent", "barres horizontales"),
        (0, 18, 49.5, 18, "Évolution 2000-2017", "line plot (temporel)"),
        (50.5, 18, 49.5, 18, "Échelle de service par continent", "percent stacked barplot")]),
    ("vue_continent", "Vue 2 · Continent", "Indicateurs agrégés pour le continent choisi", FILTERS + ["Continent (géo.)"], [
        (0, 37, 56, 26, "Carte du continent", "carte choroplèthe zoomée"),
        (57, 50.5, 43, 12.5, "Évolution 2000-2017", "line plot"),
        (57, 37, 43, 12.5, "8 pays avec le plus de pers. sans accès", "barres"),
        (0, 18, 49.5, 18, "15 pays les moins équipés", "percent stacked barplot"),
        (50.5, 18, 49.5, 18, "Ville / campagne dans ces 15 pays", "grouped barplot")]),
    ("vue_pays", "Vue 3 · Pays", "Fiche du pays choisi, comparée à son continent et au monde", FILTERS + ["Continent", "Pays (géo.)"], [
        (0, 37, 56, 26, "Évolution de l'accès (basique T/U/R, sûr)", "line plot (temporel)"),
        (57, 37, 43, 26, "Situation dans le continent", "carte zoomée, pays encadré"),
        (0, 18, 33, 18, "Pays / continent / monde", "grouped barplot"),
        (34, 18, 33, 18, "Population urbaine / rurale", "stacked barplot"),
        (68, 18, 32, 18, "Stabilité politique 2000-2017", "line plot + seuil du filtre")]),
]
for name, title, sub, filt, blocks in views:
    fig, ax = frame(title, sub)
    common(ax, filt)
    for b in blocks: box(ax, *b)
    domains(ax, 2.5)
    fig.savefig(OUT / f"blueprint_{name}.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)
print("ok")
