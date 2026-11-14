"""Préparation des données DWFA : nettoyage, jointures, champs calculés et modèle de données.

Entrées : les 5 fichiers de DAN-P8-donnees/ + preparation/referentiel_pays.csv
          (code ISO3, nom français et continent OMS traduit, pour la carte et l'affichage).
Sorties : modele/dim_pays.csv, modele/fait_pays_annee.csv, modele/fait_zone.csv,
          modele/fait_mortalite_2016.csv
          (schéma en étoile, directement chargeable dans Tableau ou Power BI)
          et dashboard/data.js (le même modèle, compacté pour le tableau de bord web).

Lancer depuis la racine du dépôt :  python preparation/preparation_donnees.py
"""
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "DAN-P8-donnees"
OUT = ROOT / "modele"
YEARS = list(range(2000, 2018))  # période commune à toutes les sources (eau : 2000-2017)

REGIONS_FR = {"Africa": "Afrique", "Americas": "Amériques", "South-East Asia": "Asie du Sud-Est",
              "Europe": "Europe", "Eastern Mediterranean": "Méditerranée orientale",
              "Western Pacific": "Pacifique occidental"}
# Noms FAO/Banque mondiale -> noms OMS (référence des fichiers eau et régions)
ALIAS = {"North Macedonia": "Republic of North Macedonia", "China, mainland": "China"}


def read(name):
    return pd.read_csv(SRC / name, encoding="utf-8-sig")


# ---------------------------------------------------------------- 1. chargement
ref = pd.read_csv(ROOT / "preparation" / "referentiel_pays.csv")
regions = read("RegionCountry.csv").rename(columns={"REGION (DISPLAY)": "region_oms", "COUNTRY (DISPLAY)": "country"})
water = read("BasicAndSafelyManagedDrinkingWaterServices.csv").rename(columns={
    "Country": "country", "Year": "year", "Granularity": "zone",
    "Population using at least basic drinking-water services (%)": "basic",
    "Population using safely managed drinking-water services (%)": "safe"})
pop = read("Population.csv").rename(columns={"Country": "country", "Year": "year", "Granularity": "zone", "Population": "pop_k"})
stab = read("PoliticalStability.csv").rename(columns={"Country": "country", "Year": "year", "Political_Stability": "stability"})
mort = read("MortalityRateAttributedToWater.csv").rename(columns={
    "Country": "country", "Year": "year", "Granularity": "sexe",
    "Mortality rate attributed to exposure to unsafe WASH services": "mortality", "WASH deaths": "deaths"})

# La ligne FAO "China" inclut Hong Kong, Macao et Taïwan : on garde "China, mainland", comme l'OMS
pop = pop[pop["country"] != "China"]
pop["country"] = pop["country"].replace(ALIAS)
stab["country"] = stab["country"].replace(ALIAS)

# ---------------------------------------------------------------- 2. nettoyage
# Champ calculé : la population FAO est en milliers d'habitants -> x 1 000
pop["pop"] = pop["pop_k"] * 1000
pop = pop[pop["zone"].isin(["Total", "Urban", "Rural"]) & pop["year"].isin(YEARS)]
pop = pop.pivot_table(index=["country", "year"], columns="zone", values="pop").rename(
    columns={"Total": "pop", "Urban": "pop_urb", "Rural": "pop_rur"}).reset_index()

# Pays scindés : la FAO garde l'ancien pays jusqu'à la séparation, l'OMS donne déjà les deux.
# Avant la séparation, on répartit l'ancien pays selon les parts de la première année séparée.
def scinder(pop, ancien, pays, annee):
    cols = ["pop", "pop_urb", "pop_rur"]
    former = pop[pop["country"] == ancien].set_index("year")
    ref_an = pop[pop["year"] == annee].set_index("country")
    tot = ref_an.loc[pays, cols].sum()
    split = [former[cols].mul(ref_an.loc[c, cols] / tot).assign(country=c).reset_index() for c in pays]
    return pd.concat([pop[pop["country"] != ancien]] + split, ignore_index=True)

pop = scinder(pop, "Sudan (former)", ["Sudan", "South Sudan"], 2012)               # séparation en 2011
pop = scinder(pop, "Serbia and Montenegro", ["Serbia", "Montenegro"], 2006)        # séparation en 2006

# Accès à l'eau : une colonne par zone (T = total, U = urbain, R = rural)
water = water.pivot_table(index=["country", "year"], columns="zone", values=["basic", "safe"])
water.columns = [f"{v}_{ {'Total': 'T', 'Urban': 'U', 'Rural': 'R'}[z]}" for v, z in water.columns]
water = water.reset_index()
# 7 taux valent 100,00001 % (arrondi de la source) : on borne les pourcentages à [0, 100]
pct = [c for c in water.columns if c.startswith(("basic_", "safe_"))]
water[pct] = water[pct].clip(0, 100)

# Stabilité politique : l'année 2001 manque dans la source -> interpolation linéaire par pays
stab = stab[stab["year"].isin(YEARS)][["country", "year", "stability"]]
grid = pd.MultiIndex.from_product([stab["country"].unique(), YEARS], names=["country", "year"])
stab = (stab.set_index(["country", "year"]).reindex(grid)
        .groupby(level="country")["stability"].transform(lambda s: s.interpolate(limit_area="inside"))
        .reset_index())

# ---------------------------------------------------------------- 3. jointures
dim = (ref.merge(regions, on="country", how="left")
          .assign(continent_check=lambda d: d["region_oms"].map(REGIONS_FR)))
assert (dim["continent"] == dim["continent_check"]).all(), "continent incohérent avec RegionCountry.csv"
dim = dim.drop(columns="continent_check")

base = pd.MultiIndex.from_product([dim["country"], YEARS], names=["country", "year"]).to_frame(index=False)
fact = (base.merge(pop, on=["country", "year"], how="left")       # jointures à gauche : on garde
            .merge(water, on=["country", "year"], how="left")     # les 194 pays de l'OMS même
            .merge(stab, on=["country", "year"], how="left"))     # quand une source est muette

# ---------------------------------------------------------------- 4. champs calculés
fact["urban_rate"] = fact["pop_urb"] / fact["pop"] * 100
fact["pop_without_basic"] = fact["pop"] * (100 - fact["basic_T"]) / 100
fact["gap_basic_safe"] = fact["basic_T"] - fact["safe_T"]

m = mort.pivot_table(index="country", columns="sexe", values="mortality").rename(
    columns={"Total": "mortality", "Male": "mortality_m", "Female": "mortality_f"})
m["deaths"] = mort[mort["sexe"] == "Total"].set_index("country")["deaths"]
m = m.reset_index()

# Score d'efficacité de la politique de l'eau (domaine 3), 2016 :
#   50 % accès basique normalisé (min-max) + 50 % faible mortalité normalisée (min-max sur log,
#   car la mortalité va de 0,01 à 101 pour 100 000 : sans log, tous les pays riches seraient à 100).
f16 = fact[fact["year"] == 2016][["country", "basic_T"]].merge(m, on="country")
f16 = f16.dropna(subset=["basic_T", "mortality"])
mm = lambda s: (s - s.min()) / (s.max() - s.min()) * 100
lm = np.log(f16["mortality"].clip(lower=0.01))
f16["efficiency_score"] = 0.5 * mm(f16["basic_T"]) + 0.5 * (100 - mm(lm))
m = m.merge(f16[["country", "efficiency_score"]], on="country", how="left").assign(year=2016)
# Population et stabilité 2016 à côté de la mortalité : moyenne pondérée des taux
# (SUM(deaths) / SUM(pop) * 100 000) et nuage du domaine 3 sans changer de table dans Tableau
m = m.merge(fact[fact["year"] == 2016][["country", "pop", "stability"]], on="country", how="left")

# Table longue par zone (une ligne par pays, année et zone) pour Tableau : la zone devient une
# dimension (couleur des courbes et des barres groupées) et les numérateurs / dénominateurs
# précalculés donnent des moyennes pondérées exactes à tout niveau : SUM(hab_basic) / SUM(pop_couv_basic)
zones = []
for z, zl in [("T", "Total"), ("U", "Urbain"), ("R", "Rural")]:
    zp = {"T": "pop", "U": "pop_urb", "R": "pop_rur"}[z]
    d = fact[["country", "year"]].assign(zone=zl, population=fact[zp], basic=fact[f"basic_{z}"], safe=fact[f"safe_{z}"])
    d["hab_basic"] = d["population"] * d["basic"] / 100
    d["pop_couv_basic"] = d["population"].where(d["basic"].notna())
    d["hab_safe"] = d["population"] * d["safe"] / 100
    d["pop_couv_safe"] = d["population"].where(d["safe"].notna())
    d["pop_sans_basic"] = d["population"] - d["hab_basic"]
    # Échelle de service (barres 100 % empilées), seulement quand les deux taux sont connus
    both = d["basic"].notna() & d["safe"].notna()
    d["part_sur"] = d["safe"].where(both)
    d["part_basique_seul"] = (d["basic"] - d["safe"]).where(both)
    d["part_sans_basique"] = (100 - d["basic"]).where(both)
    zones.append(d)
zone = pd.concat(zones, ignore_index=True)

# ---------------------------------------------------------------- 5. export du modèle
OUT.mkdir(exist_ok=True)
dim[["iso3", "country", "pays", "continent", "region_oms"]].to_csv(OUT / "dim_pays.csv", index=False)
fact.merge(dim[["country", "iso3"]], on="country").drop(columns="country").round(4).to_csv(OUT / "fait_pays_annee.csv", index=False)
m.merge(dim[["country", "iso3"]], on="country").drop(columns="country").round(4).to_csv(OUT / "fait_mortalite_2016.csv", index=False)
zone.merge(dim[["country", "iso3"]], on="country").drop(columns="country").round(4).to_csv(OUT / "fait_zone.csv", index=False)

# Version compacte pour le tableau de bord web : un objet par pays, des tableaux par année
def arr(s, nd):
    return [None if pd.isna(v) else round(float(v), nd) for v in s]

fact = fact.sort_values(["country", "year"])
mi = m.set_index("country")
countries = []
for _, d in dim.sort_values("pays", key=lambda s: s.str.normalize("NFKD")).iterrows():
    f = fact[fact["country"] == d["country"]]
    r = mi.loc[d["country"]] if d["country"] in mi.index else None
    g = lambda k, nd: None if r is None or pd.isna(r[k]) else round(float(r[k]), nd)
    countries.append({"n": d["pays"], "en": d["country"], "i": d["iso3"], "r": d["continent"],
        "p": arr(f["pop"], 0), "pu": arr(f["pop_urb"], 0), "pr": arr(f["pop_rur"], 0), "u": arr(f["urban_rate"], 2),
        **{k: arr(f[c], 2) for k, c in [("bT", "basic_T"), ("bU", "basic_U"), ("bR", "basic_R"),
                                           ("sT", "safe_T"), ("sU", "safe_U"), ("sR", "safe_R"), ("st", "stability")]},
        "m": g("mortality", 2), "mH": g("mortality_m", 2), "mF": g("mortality_f", 2), "dw": g("deaths", 0),
        "sc": g("efficiency_score", 1)})
data = {"years": YEARS, "regions": sorted(REGIONS_FR.values()), "c": countries}
(ROOT / "dashboard").mkdir(exist_ok=True)
(ROOT / "dashboard" / "data.js").write_text("const D = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")

print(f"{len(dim)} pays · {len(fact)} lignes pays-année · {len(zone)} lignes pays-année-zone · "
      f"{m['efficiency_score'].notna().sum()} scores d'efficacité")
print("Valeurs manquantes (%) :", (fact.isna().mean() * 100).round(1).to_dict())
