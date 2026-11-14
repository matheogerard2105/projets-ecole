"""Génère le classeur Tableau DWFA (tableau/DWFA.twbx) qui reproduit dashboard/index.html.

Entrées : modele/*.csv (schéma en étoile produit par preparation/preparation_donnees.py).
Sorties :
  tableau/donnees/pays_annee.csv   une ligne par pays et par année (KPI, cartes, nuages de points)
  tableau/donnees/indicateurs.csv  format long (courbes, échelles de service, ville/campagne, comparaisons)
  tableau/DWFA.twb                 classeur pointant vers tableau/donnees/
  tableau/DWFA.twbx                même classeur empaqueté avec ses données (à ouvrir dans Tableau)

Les filtres du tableau HTML deviennent des paramètres Tableau (Année, Zone, Stabilité minimale,
Continent, Pays) : un paramètre s'applique d'un coup à toutes les feuilles des trois tableaux de bord.
"""
import re
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tableau"
DATA = OUT / "donnees"

# --------------------------------------------------------------------------------------------
# 1. Données
# --------------------------------------------------------------------------------------------
fait = pd.read_csv(ROOT / "modele/fait_pays_annee.csv")
dim = pd.read_csv(ROOT / "modele/dim_pays.csv")
mort = pd.read_csv(ROOT / "modele/fait_mortalite_2016.csv")

df = fait.merge(dim[["iso3", "pays", "continent"]], on="iso3")
df = df.merge(mort[["iso3", "deaths", "mortality", "efficiency_score"]], on="iso3", how="left")
y16 = df[df.year == 2016].set_index("iso3")
df["pop_2016"] = df.iso3.map(y16["pop"])
df["stability_2016"] = df.iso3.map(y16["stability"])
df = df.rename(columns={"deaths": "deaths_2016", "mortality": "mortality_2016"})

# rangs précalculés par continent et par année (1 = le moins équipé / le plus de personnes sans accès)
for z in "TUR":
    df[f"rang_{z}"] = df.groupby(["continent", "year"])[f"basic_{z}"].rank(method="first")
df["rang_sans"] = df.groupby(["continent", "year"])["pop_without_basic"].rank(method="first", ascending=False)
# panel « accès sûr » : pays renseignés toutes les années (évite les sauts dus à la couverture)
df["panel_sur"] = df.groupby("iso3")["safe_T"].transform(lambda s: s.notna().all())

wide_cols = ["iso3", "pays", "continent", "year", "pop", "pop_urb", "pop_rur", "urban_rate", "basic_T", "basic_U", "basic_R",
             "safe_T", "safe_U", "safe_R", "stability", "pop_without_basic", "deaths_2016", "mortality_2016", "efficiency_score",
             "pop_2016", "stability_2016", "rang_T", "rang_U", "rang_R", "rang_sans"]
wide = df[wide_cols].sort_values(["iso3", "year"])

ZW = {"T": "pop", "U": "pop_urb", "R": "pop_rur"}
ZL = {"T": "total", "U": "urbain", "R": "rural"}
rows = []
for r in df.itertuples(index=False):
    base = dict(iso3=r.iso3, pays=r.pays, continent=r.continent, year=r.year, stability=r.stability,
                rang_T=r.rang_T, rang_U=r.rang_U, rang_R=r.rang_R, panel_sur=r.panel_sur)

    def add(niveau, indicateur, zone, libelle, valeur, poids, sur_renseigne=None):
        if valeur is None or (isinstance(valeur, float) and np.isnan(valeur)):
            return
        rows.append({**base, "niveau": niveau, "indicateur": indicateur, "zone": zone, "libelle": libelle,
                     "valeur": round(float(valeur), 4), "poids": poids, "sur_renseigne": sur_renseigne})

    for niveau in ("Monde", "Continent", "Pays"):
        for z in "TUR":
            w = getattr(r, ZW[z])
            add(niveau, "Accès basique", z, f"Accès basique · {ZL[z]}", getattr(r, f"basic_{z}"), w)
            add(niveau, "Accès sûr", z, f"Accès sûr · {ZL[z]}", getattr(r, f"safe_{z}"), w)
        add(niveau, "Urbanisation", "*", "Urbanisation", r.urban_rate, r.pop)
        add(niveau, "Stabilité", "*", "Stabilité politique", r.stability, 1)
    # population urbaine / rurale (vue Pays)
    add("Monde", "Population", "U", "Urbaine", r.pop_urb / 1e6, 1)
    add("Monde", "Population", "R", "Rurale", r.pop_rur / 1e6, 1)
    # échelle de service : sûr / basique non sûr / sans accès basique
    for z in "TUR":
        b, s, w = getattr(r, f"basic_{z}"), getattr(r, f"safe_{z}"), getattr(r, ZW[z])
        if np.isnan(b):
            continue
        ok = not np.isnan(s)
        add("Monde", "Échelle", z, "Accès sûr", s if ok else 0.0, w, ok)
        add("Monde", "Échelle", z, "Basique, non sûr", b - s if ok else b, w, ok)
        add("Monde", "Échelle", z, "Sans accès basique", 100 - b, w, ok)
long = pd.DataFrame(rows)

DATA.mkdir(parents=True, exist_ok=True)
wide.to_csv(DATA / "pays_annee.csv", index=False)
long.to_csv(DATA / "indicateurs.csv", index=False)

REGIONS = ["Afrique", "Amériques", "Asie du Sud-Est", "Europe", "Méditerranée orientale", "Pacifique occidental"]
PAYS = sorted(dim.pays, key=lambda s: s.lower())

# --------------------------------------------------------------------------------------------
# 2. Modèle du classeur : paramètres, sources, champs calculés
# --------------------------------------------------------------------------------------------
A = lambda s: quoteattr(s)  # attribut XML entre quotes
Q = lambda s: '"' + s.replace('"', '""') + '"'  # littéral chaîne Tableau

P_ANNEE, P_ZONE, P_STAB, P_CONT, P_PAYS = (f"[Parameters].[Parameter {k}]" for k in range(1, 6))
ZONE_CODE = f'CASE {P_ZONE} WHEN "Urbain" THEN "U" WHEN "Rural" THEN "R" ELSE "T" END'

PARAMS = [
    ("Parameter 1", "Année", "integer", "quantitative", "2017", ("range", 2000, 2017, 1)),
    ("Parameter 2", "Zone", "string", "nominal", Q("Total"), ("list", [Q(v) for v in ["Total", "Urbain", "Rural"]])),
    ("Parameter 3", "Stabilité politique minimale", "real", "quantitative", "-3.5", ("range", -3.5, 1.5, 0.1)),
    ("Parameter 4", "Continent (région OMS)", "string", "nominal", Q("Afrique"), ("list", [Q(v) for v in REGIONS])),
    ("Parameter 5", "Pays", "string", "nominal", Q("Madagascar"), ("list", [Q(v) for v in PAYS])),
]


class DS:
    def __init__(self, name, caption, filename, cols):
        self.name, self.caption, self.filename = name, caption, filename
        self.cols = {}  # nom interne -> dict(caption, datatype, role, type, formula, extra)
        for c, (dt, role, typ, cap, extra) in cols.items():
            self.cols[c] = dict(caption=cap, datatype=dt, role=role, type=typ, formula=None, extra=extra)

    def calc(self, name, caption, formula, datatype="real", role="measure", typ=None):
        typ = typ or ("quantitative" if role == "measure" and datatype in ("real", "integer") else "nominal")
        self.cols[name] = dict(caption=caption, datatype=datatype, role=role, type=typ, formula=formula, extra="")
        return name

    def deps(self, names):
        """Fermeture transitive des colonnes (et paramètres) utilisées par un ensemble de champs."""
        seen, params, todo = set(), set(), list(names)
        while todo:
            n = todo.pop()
            if n in seen or n not in self.cols:
                continue
            seen.add(n)
            f = self.cols[n]["formula"]
            if f:
                params.update(re.findall(r"\[Parameters\]\.\[(Parameter \d)\]", f))
                todo += [t for t in re.findall(r"(?<!\[Parameters\]\.)\[([^\]]+)\]", f) if t in self.cols]
        return seen, params

    def col_xml(self, n, indent="      "):
        c = self.cols[n]
        attrs = f"datatype='{c['datatype']}' name={A('[' + n + ']')} role='{c['role']}' type='{c['type']}'"
        if c["caption"]:
            attrs = f"caption={A(c['caption'])} " + attrs
        if c["extra"]:
            attrs += " " + c["extra"]
        if c["formula"]:
            return f"{indent}<column {attrs}>\n{indent}  <calculation class='tableau' formula={A(c['formula'])} />\n{indent}</column>\n"
        return f"{indent}<column {attrs} />\n"


def raw(dt, role, typ, cap=None, extra=""):
    return (dt, role, typ, cap, extra)


DIMS = {
    "iso3": raw("string", "dimension", "nominal", "Code pays", "semantic-role='[Country].[ISO3166_3]'"),
    "pays": raw("string", "dimension", "nominal", "Pays"),
    "continent": raw("string", "dimension", "nominal", "Continent"),
    "year": raw("integer", "dimension", "ordinal", "Année"),
}
M = lambda cap=None: raw("real", "measure", "quantitative", cap)

PA = DS("pays_annee", "Pays × année", "pays_annee.csv", {
    **DIMS, "pop": M("Population"), "pop_urb": M("Population urbaine"), "pop_rur": M("Population rurale"),
    "urban_rate": M("Taux d'urbanisation"), "basic_T": M("Accès basique total"), "basic_U": M("Accès basique urbain"),
    "basic_R": M("Accès basique rural"), "safe_T": M("Accès sûr total"), "safe_U": M("Accès sûr urbain"),
    "safe_R": M("Accès sûr rural"), "stability": M("Stabilité politique"), "pop_without_basic": M("Personnes sans accès basique"),
    "deaths_2016": M("Décès WASH 2016"), "mortality_2016": M("Mortalité WASH 2016"), "efficiency_score": M("Score d'efficacité"),
    "pop_2016": M("Population 2016"), "stability_2016": M("Stabilité politique 2016"), "rang_T": M(), "rang_U": M(),
    "rang_R": M(), "rang_sans": M()})
IN = DS("indicateurs", "Indicateurs (format long)", "indicateurs.csv", {
    **DIMS, "stability": M("Stabilité politique"), "rang_T": M(), "rang_U": M(), "rang_R": M(),
    "panel_sur": raw("boolean", "dimension", "nominal", "Panel accès sûr"),
    "niveau": raw("string", "dimension", "nominal", "Niveau"), "indicateur": raw("string", "dimension", "nominal", "Indicateur"),
    "zone": raw("string", "dimension", "nominal", "Zone"), "libelle": raw("string", "dimension", "nominal", "Série"),
    "valeur": M("Valeur"), "poids": M("Poids"), "sur_renseigne": raw("boolean", "dimension", "nominal", "Accès sûr renseigné")})

B = lambda ds, name, cap, f: ds.calc(name, cap, f, "boolean", "dimension", "nominal")
for ds in (PA, IN):
    B(ds, "f_retenu", "Retenu (stabilité)", f"ISNULL([stability]) OR [stability] >= {P_STAB}")
    B(ds, "f_annee", "Année choisie", f"[year] = {P_ANNEE}")
    B(ds, "f_continent", "Dans le continent choisi", f"[continent] = {P_CONT}")
    B(ds, "f_pays", "Pays choisi", f"[pays] = {P_PAYS}")
    ds.calc("cont_pays", "Continent du pays choisi", f"{{FIXED : MAX(IF [pays] = {P_PAYS} THEN [continent] END)}}", "string", "dimension")
    B(ds, "f_cont_pays", "Dans le continent du pays choisi", "[continent] = [cont_pays]")
    ds.calc("zone_code", "Code zone", ZONE_CODE, "string", "dimension")
    ds.calc("rang_zone", "Rang d'accès dans le continent", "CASE [zone_code] WHEN \"U\" THEN [rang_U] WHEN \"R\" THEN [rang_R] ELSE [rang_T] END")
    B(ds, "f_top15", "15 pays les moins équipés", "[rang_zone] <= 15")

# --- pays × année
PEOPLE = lambda x: (f"IF ISNULL({x}) THEN \"n.d.\" ELSEIF {x} >= 1e9 THEN REPLACE(STR(ROUND({x}/1e9, 2)), \".\", \",\") + \" Md\" "
                    f"ELSEIF {x} >= 1e6 THEN REPLACE(STR(ROUND({x}/1e6, 1)), \".\", \",\") + \" M\" "
                    f"ELSEIF {x} >= 1e3 THEN STR(INT(ROUND({x}/1e3, 0))) + \" k\" ELSE STR(INT(ROUND({x}, 0))) END")
PCT = lambda x, d=1: f"IF ISNULL({x}) THEN \"n.d.\" ELSE REPLACE(STR(ROUND({x}, {d})), \".\", \",\") + \" %\" END"
NUM = lambda x, d=1: f"IF ISNULL({x}) THEN \"n.d.\" ELSE REPLACE(STR(ROUND({x}, {d})), \".\", \",\") END"
WAVG = lambda v, w: f"SUM(IF NOT ISNULL({v}) AND NOT ISNULL({w}) THEN {v} * {w} END) / SUM(IF NOT ISNULL({v}) AND NOT ISNULL({w}) THEN {w} END)"

PA.calc("b_zone", "Accès basique (zone)", "CASE [zone_code] WHEN \"U\" THEN [basic_U] WHEN \"R\" THEN [basic_R] ELSE [basic_T] END")
PA.calc("s_zone", "Accès sûr (zone)", "CASE [zone_code] WHEN \"U\" THEN [safe_U] WHEN \"R\" THEN [safe_R] ELSE [safe_T] END")
PA.calc("w_zone", "Population de la zone", "CASE [zone_code] WHEN \"U\" THEN [pop_urb] WHEN \"R\" THEN [pop_rur] ELSE [pop] END")
PA.calc("m_basic", "% accès basique", WAVG("[b_zone]", "[w_zone]"))
PA.calc("m_safe", "% accès sûr", WAVG("[s_zone]", "[w_zone]"))
PA.calc("m_sans_M", "Personnes sans accès basique (millions)", "SUM([pop_without_basic]) / 1e6")
PA.calc("m_mort", "Mortalité WASH 2016 (pour 100 000)", "SUM([deaths_2016]) / SUM(IF NOT ISNULL([deaths_2016]) THEN [pop_2016] END) * 100000")
PA.calc("m_urb", "Taux d'urbanisation", "SUM([pop_urb]) / SUM([pop]) * 100")
PA.calc("m_safe_cov", "Couverture accès sûr", "SUM(IF NOT ISNULL([s_zone]) THEN [pop] END) / SUM([pop]) * 100")
PA.calc("classe", "Classe d'accès basique",
        "IF NOT [f_retenu] THEN \"exclu (stabilité)\" ELSEIF ISNULL([b_zone]) THEN \"n.d.\" ELSEIF [b_zone] < 50 THEN \"< 50 %\" "
        "ELSEIF [b_zone] < 70 THEN \"50-70 %\" ELSEIF [b_zone] < 85 THEN \"70-85 %\" ELSEIF [b_zone] < 95 THEN \"85-95 %\" "
        "ELSEIF [b_zone] < 99 THEN \"95-99 %\" ELSE \"≥ 99 %\" END", "string", "dimension")
PA.calc("lab_sel", "Libellé pays choisi", "IF [f_pays] THEN [pays] END", "string", "dimension")
B(PA, "f_2016", "Année 2016", "[year] = 2016")
B(PA, "f_top8", "8 pays avec le plus de personnes sans accès", "[rang_sans] <= 8")
B(PA, "f_has_b", "Accès basique renseigné", "NOT ISNULL([b_zone])")

KPI = {  # nom -> (titre, valeur, sous-titre)
    "pop": ("Population", PEOPLE("SUM([pop])"), "STR(COUNTD([iso3])) + \" pays retenus\""),
    "basic": ("Accès basique", PCT("[m_basic]"), "\"au moins un point d'eau amélioré\""),
    "safe": ("Accès sûr", PCT("[m_safe]"), "\"données pour \" + STR(INT(ROUND([m_safe_cov], 0))) + \" % de la population\""),
    "sans": ("Sans accès basique", PEOPLE("SUM([pop_without_basic])"), "\"personnes (total)\""),
    "mort": ("Mortalité WASH 2016", NUM("[m_mort]"), "\"pour 100 000 hab. · \" + " + PEOPLE("SUM([deaths_2016])").replace("\"n.d.\"", "\"0\"", 1) + " + \" décès\""),
    "urb": ("Taux d'urbanisation", PCT("[m_urb]"), "\"population vivant en ville\""),
    "stab": ("Stabilité politique", NUM("AVG([stability])", 2), "\"moyenne des pays, de -2,5 à +2,5\""),
    "score": ("Score d'efficacité 2016", NUM("AVG([efficiency_score])", 0), "\"sur 100 (domaine 3)\""),
}
for k, (t, v, s) in KPI.items():
    if s.startswith('"') and s.endswith('"') and s.count('"') == 2:  # texte fixe : on l'agrège, sinon Tableau en fait une dimension et la feuille reste vide
        s = f"IF COUNT([iso3]) > 0 THEN {s} END"
    PA.calc(f"kv_{k}", f"KPI {t}", v, "string")
    PA.calc(f"ks_{k}", f"KPI {t} (détail)", s, "string")

# --- format long
IN.calc("m_val", "Valeur pondérée", WAVG("[valeur]", "[poids]"))
IN.calc("m_sum", "Valeur (somme)", "SUM([valeur])")
B(IN, "f_monde", "Niveau Monde", "[niveau] = \"Monde\"")
B(IN, "f_courbe", "Séries de la courbe",
  "[niveau] = \"Monde\" AND (([indicateur] = \"Accès basique\") OR ([indicateur] = \"Accès sûr\" AND [zone] = \"T\"))")
B(IN, "f_panel", "Panel accès sûr (si série sûre)", "[indicateur] <> \"Accès sûr\" OR [panel_sur]")
B(IN, "f_vc", "Accès basique urbain / rural", "[niveau] = \"Monde\" AND [indicateur] = \"Accès basique\" AND [zone] <> \"T\"")
B(IN, "f_ech_monde", "Échelle (total, sûr renseigné)", "[indicateur] = \"Échelle\" AND [zone] = \"T\" AND [sur_renseigne]")
B(IN, "f_ech_zone", "Échelle (zone choisie)", "[indicateur] = \"Échelle\" AND [zone] = [zone_code]")
B(IN, "f_pop", "Population urbaine / rurale", "[indicateur] = \"Population\"")
B(IN, "f_comp", "Comparaison pays / continent / monde",
  "([indicateur] = \"Urbanisation\" OR (([indicateur] = \"Accès basique\" OR [indicateur] = \"Accès sûr\") AND [zone] = [zone_code])) AND "
  "(([niveau] = \"Pays\" AND [f_pays]) OR ([niveau] = \"Continent\" AND [f_cont_pays] AND [f_retenu]) OR ([niveau] = \"Monde\" AND [f_retenu]))")
B(IN, "f_stab", "Stabilité pays / continent",
  "[indicateur] = \"Stabilité\" AND (([niveau] = \"Pays\" AND [f_pays]) OR ([niveau] = \"Continent\" AND [f_cont_pays]))")
IN.calc("lib_niveau", "Pays / continent / monde",
        f"CASE [niveau] WHEN \"Pays\" THEN {P_PAYS} WHEN \"Continent\" THEN [cont_pays] ELSE \"Monde\" END", "string", "dimension")
IN.calc("lib_vc", "Milieu", "IF [zone] = \"U\" THEN \"Urbain\" ELSE \"Rural\" END", "string", "dimension")

# --- couleurs (palette « Bleu » du tableau HTML)
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#1c5cab", "#0d366b"]
COLORS = {
    (PA, "classe"): dict(zip(["< 50 %", "50-70 %", "70-85 %", "85-95 %", "95-99 %", "≥ 99 %", "n.d.", "exclu (stabilité)"],
                             SEQ + ["#c9d3dc", "#e9eef2"])),
    (PA, "f_pays"): {"true": "#0b2236", "false": "#9ec5f4"},
    (IN, "libelle"): {"Accès basique · total": "#1c5cab", "Accès basique · urbain": "#0d366b", "Accès basique · rural": "#6da7ec",
                      "Accès sûr · total": "#e08a2c", "Accès sûr": "#104281", "Basique, non sûr": "#5598e7",
                      "Sans accès basique": "#cde2fb", "Urbaine": "#0d366b", "Rurale": "#6da7ec"},
    (IN, "lib_vc"): {"Urbain": "#0d366b", "Rural": "#6da7ec"},
    (IN, "niveau"): {"Pays": "#0d366b", "Continent": "#5598e7", "Monde": "#b7d3f6"},
}
BLUE, INK, MUTED = "#1c5cab", "#0b2236", "#5f7488"
FONT = "Tableau Book"

# --------------------------------------------------------------------------------------------
# 3. Feuilles
# --------------------------------------------------------------------------------------------
DERIV = {"sum": "Sum", "avg": "Avg", "none": "None", "usr": "User", "attr": "Attribute"}


def inst(ds, spec):
    """'sum:pop' -> ('[sum:pop:qk]', column, derivation, type)."""
    d, c = spec.split(":", 1)
    col = ds.cols[c]
    if d == "none":
        t = col["type"]
    else:
        t = "quantitative" if col["datatype"] in ("real", "integer") or d in ("sum", "avg") else "nominal"
    suf = {"nominal": "nk", "ordinal": "ok", "quantitative": "qk"}[t]
    return f"[{d}:{c}:{suf}]", c, DERIV[d], t


class Sheet:
    def __init__(self, name, ds, title, rows=(), cols=(), mark="Bar", filters=(), color=None, size=None, label=None,
                 detail=(), tooltip=(), sort=None, mark_color=None, show_labels=False, label_text=None,
                 axis_titles=None, fmt=None, sizes=None, text_fmt=None):
        self.__dict__.update(locals())
        self.name = name

    def ref(self, spec):
        c = spec.split(":", 1)[1]
        if self.ds.cols[c].get("generated"):  # Latitude / Longitude (generated) : pas d'instance
            return f"[{self.ds.name}].[{c}]"
        return f"[{self.ds.name}].{inst(self.ds, spec)[0]}"

    def shelf(self, specs):
        if not specs:
            return ""
        parts = [self.ref(s) for s in specs]
        return parts[0] if len(parts) == 1 else "(" + " / ".join(parts) + ")"

    def xml(self):
        ds, specs = self.ds, set()
        enc_specs = [self.color, self.size, self.label] + list(self.detail) + list(self.tooltip)
        for s in list(self.rows) + list(self.cols) + [f"none:{f}" for f in self.filters] + enc_specs + ([self.sort[1]] if self.sort else []):
            if s:
                specs.add(s)
        if self.sort:
            specs.add(self.sort[0])
        used = {inst(ds, s)[1] for s in specs}
        cols, params = ds.deps(used)
        o = [f"    <worksheet name={A(self.name)}>\n      <layout-options>\n        <title>\n          <formatted-text>\n"
             f"            <run bold='true' fontcolor='{INK}' fontsize='11'>{escape(self.title)}</run>\n"
             "          </formatted-text>\n        </title>\n      </layout-options>\n      <table>\n        <view>\n          <datasources>\n"]
        o.append(f"            <datasource caption={A(ds.caption)} name={A(ds.name)} />\n          </datasources>\n")
        if any("generated" in r for r in self.rows):  # carte : fond de carte Tableau
            o.append("          <mapsources>\n            <mapsource name='Tableau' />\n          </mapsources>\n")
        if params:
            o.append("          <datasource-dependencies datasource='Parameters'>\n")
            for p in PARAMS:
                if p[0] in params:
                    o.append(param_xml(p, "            "))
            o.append("          </datasource-dependencies>\n")
        o.append(f"          <datasource-dependencies datasource={A(ds.name)}>\n")
        for c in sorted(cols):
            o.append(ds.col_xml(c, "            "))
        for s in sorted(specs):
            n, c, d, t = inst(ds, s)
            if ds.cols[c].get("generated"):
                continue
            o.append(f"            <column-instance column={A('[' + c + ']')} derivation='{d}' name={A(n)} pivot='key' type='{t}' />\n")
        o.append("          </datasource-dependencies>\n")
        for f in self.filters:
            r = inst(ds, f"none:{f}")[0]
            o.append(f"          <filter class='categorical' column={A(f'[{ds.name}].{r}')}>\n"
                     f"            <groupfilter function='member' level={A(r)} member='true' user:ui-domain='database' "
                     "user:ui-enumeration='inclusive' user:ui-marker='enumerate' />\n          </filter>\n")
        if self.sort:
            dim_, by, direction = self.sort
            o.append(f"          <sort class='computed' column={A(self.ref(dim_))} direction='{direction}' using={A(self.ref(by))} />\n")
        if self.filters:
            o.append("          <slices>\n" + "".join(f"            <column>{escape(self.ref('none:' + f))}</column>\n" for f in self.filters) + "          </slices>\n")
        o.append("          <aggregation value='true' />\n        </view>\n        <style>\n")
        if self.axis_titles:
            o.append("          <style-rule element='axis'>\n")
            for spec, scope, t in self.axis_titles:
                o.append(f"            <format attr='title' class='0' field={A(self.ref(spec))} scope='{scope}' value={A(t)} />\n")
            o.append("          </style-rule>\n")
        if self.fmt:
            o.append("          <style-rule element='cell'>\n")
            for spec, v in self.fmt:
                o.append(f"            <format attr='text-format' field={A(self.ref(spec))} value={A(v)} />\n")
            o.append("          </style-rule>\n")
        o.append("        </style>\n        <panes>\n          <pane>\n"
                 f"            <view>\n              <breakdown value='auto' />\n            </view>\n            <mark class='{self.mark}' />\n")
        enc = []
        if self.color:
            enc.append(f"<color column={A(self.ref(self.color))} />")
        if self.size:
            enc.append(f"<size column={A(self.ref(self.size))} />")
        if self.label:
            enc.append(f"<text column={A(self.ref(self.label))} />")
        enc += [f"<lod column={A(self.ref(s))} />" for s in self.detail]
        enc += [f"<tooltip column={A(self.ref(s))} />" for s in self.tooltip]
        if enc:
            o.append("            <encodings>\n" + "".join(f"              {e}\n" for e in enc) + "            </encodings>\n")
        if self.label_text:
            o.append("            <customized-label>\n              <formatted-text>\n")
            for txt, attrs in self.label_text:
                o.append(f"                <run {attrs}>{escape(txt)}</run>\n")
            o.append("              </formatted-text>\n            </customized-label>\n")
        o.append("            <style>\n              <style-rule element='mark'>\n")
        if self.mark_color:
            o.append(f"                <format attr='mark-color' value='{self.mark_color}' />\n")
        if self.show_labels or self.label_text:
            o.append("                <format attr='mark-labels-show' value='true' />\n                <format attr='mark-labels-cull' value='true' />\n")
        if self.sizes:
            o.append(f"                <format attr='size' value='{self.sizes}' />\n")
        o.append("              </style-rule>\n            </style>\n          </pane>\n        </panes>\n")
        o.append(f"        <rows>{escape(self.shelf(self.rows))}</rows>\n        <cols>{escape(self.shelf(self.cols))}</cols>\n")
        o.append("      </table>\n    </worksheet>\n")
        return "".join(o)


def param_xml(p, indent):
    name, cap, dt, typ, val, dom = p
    o = (f"{indent}<column caption={A(cap)} datatype='{dt}' name={A('[' + name + ']')} param-domain-type='{dom[0]}' "
         f"role='measure' type='{typ}' value={A(val)}>\n{indent}  <calculation class='tableau' formula={A(val)} />\n")
    if dom[0] == "range":
        o += f"{indent}  <range granularity='{dom[3]}' max='{dom[2]}' min='{dom[1]}' />\n"
    else:
        o += f"{indent}  <members>\n" + "".join(f"{indent}    <member value={A(m)} />\n" for m in dom[1]) + f"{indent}  </members>\n"
    return o + f"{indent}</column>\n"


SHEETS = []


def sheet(*a, **k):
    s = Sheet(*a, **k)
    SHEETS.append(s)
    return s.name


def kpi_sheets(view, filters, keys):
    names = []
    for k in keys:
        t = KPI[k][0]
        names.append(sheet(f"{view} · KPI {t}", PA, t, mark="Text", filters=filters, label=f"usr:kv_{k}",
                           tooltip=[f"usr:ks_{k}"], label_text=[
                               (t.upper() + "\n", f"fontcolor='{MUTED}' fontsize='9' bold='true'"),
                               (f"<[pays_annee].[usr:kv_{k}:nk]>\n", f"fontcolor='{INK}' fontsize='20' bold='true'"),
                               (f"<[pays_annee].[usr:ks_{k}:nk]>", f"fontcolor='{MUTED}' fontsize='8'")]))
    return names


def map_sheet(view, title, filters, color="none:classe"):
    return sheet(f"{view} · Carte", PA, title, rows=["none:Latitude (generated)"], cols=["none:Longitude (generated)"], mark="Multipolygon",
                 filters=filters, color=color, detail=["none:iso3", "none:pays"],
                 tooltip=["avg:b_zone", "avg:s_zone", "avg:stability", "sum:pop"])


def scatter_sheets(view, filters, highlight=False):
    col = "none:f_pays" if highlight else None
    lab = "none:lab_sel" if highlight else None
    common = dict(mark="Circle", detail=["none:iso3", "none:pays"], color=col, label=lab, mark_color=None if highlight else "#2a78d6")
    return [
        sheet(f"{view} · Domaine 1 création", PA, "DOMAINE 1 · CRÉATION — Accès basique et urbanisation (taille : personnes sans accès)",
              rows=["avg:basic_T"], cols=["avg:urban_rate"], filters=filters + ["f_annee"], size="sum:pop_without_basic",
              tooltip=["sum:pop_without_basic"], axis_titles=[("avg:basic_T", "rows", "Accès basique (%)"), ("avg:urban_rate", "cols", "Taux d'urbanisation (%)")], **common),
        sheet(f"{view} · Domaine 2 modernisation", PA, "DOMAINE 2 · MODERNISATION — Accès basique et accès sûr",
              rows=["avg:safe_T"], cols=["avg:basic_T"], filters=filters + ["f_annee"],
              axis_titles=[("avg:safe_T", "rows", "Accès sûr (%)"), ("avg:basic_T", "cols", "Accès basique (%)")], **common),
        sheet(f"{view} · Domaine 3 consulting", PA, "DOMAINE 3 · CONSULTING — Efficacité de la politique de l'eau et stabilité (2016)",
              rows=["avg:efficiency_score"], cols=["avg:stability_2016"], filters=filters + ["f_2016"], tooltip=["avg:mortality_2016"],
              axis_titles=[("avg:efficiency_score", "rows", "Score d'efficacité (0-100)"), ("avg:stability_2016", "cols", "Stabilité politique 2016")], **common),
    ]


V = {}
# ---- Vue 1 : Monde
V["Monde"] = dict(
    kpi=kpi_sheets("Monde", ["f_annee", "f_retenu"], ["pop", "basic", "safe", "sans", "mort", "urb", "stab"]),
    map=map_sheet("Monde", "Accès basique à l'eau potable (survoler pour le détail)", ["f_annee"]),
    sans=sheet("Monde · Sans accès par continent", PA, "Personnes sans accès basique, par continent (millions)", rows=["none:continent"],
               cols=["usr:m_sans_M"], filters=["f_annee", "f_retenu"], sort=("none:continent", "usr:m_sans_M", "DESC"),
               mark_color=BLUE, show_labels=True, label="usr:m_sans_M", fmt=[("usr:m_sans_M", "#,##0")],
               axis_titles=[("usr:m_sans_M", "cols", "millions de personnes")]),
    line=sheet("Monde · Évolution", IN, "Évolution de l'accès à l'eau, 2000-2017 (moyennes pondérées par la population)",
               rows=["usr:m_val"], cols=["none:year"], mark="Line", color="none:libelle", filters=["f_courbe", "f_panel", "f_retenu"],
               axis_titles=[("usr:m_val", "rows", "% de la population")]),
    ech=sheet("Monde · Échelle de service", IN, "Échelle de service par continent (% de la population, pays avec données « sûr »)",
              rows=["usr:m_val"], cols=["none:continent"], color="none:libelle", filters=["f_ech_monde", "f_annee", "f_retenu"],
              label="usr:m_val", fmt=[("usr:m_val", "#,##0")], axis_titles=[("usr:m_val", "rows", "% de la population")]),
    vc=sheet("Monde · Ville campagne", IN, "Écart ville / campagne par continent (accès basique, %)", rows=["usr:m_val"],
             cols=["none:continent", "none:lib_vc"], color="none:lib_vc", filters=["f_vc", "f_annee", "f_retenu"],
             label="usr:m_val", fmt=[("usr:m_val", "#,##0")], axis_titles=[("usr:m_val", "rows", "Accès basique (%)")]),
    dom=scatter_sheets("Monde", ["f_retenu"]),
)
# ---- Vue 2 : Continent
V["Continent"] = dict(
    kpi=kpi_sheets("Continent", ["f_annee", "f_retenu", "f_continent"], ["pop", "basic", "safe", "sans", "mort", "urb", "stab"]),
    map=map_sheet("Continent", "Accès basique dans le continent choisi", ["f_annee", "f_continent"]),
    line=sheet("Continent · Évolution", IN, "Évolution de l'accès à l'eau, 2000-2017", rows=["usr:m_val"], cols=["none:year"], mark="Line",
               color="none:libelle", filters=["f_courbe", "f_panel", "f_retenu", "f_continent"],
               axis_titles=[("usr:m_val", "rows", "% de la population")]),
    sans=sheet("Continent · Sans accès top 8", PA, "Où vivent les personnes sans accès basique (8 pays, millions)", rows=["none:pays"],
               cols=["usr:m_sans_M"], filters=["f_annee", "f_retenu", "f_continent", "f_top8"],
               sort=("none:pays", "usr:m_sans_M", "DESC"), mark_color=BLUE, show_labels=True, label="usr:m_sans_M",
               fmt=[("usr:m_sans_M", "#,##0.0")], axis_titles=[("usr:m_sans_M", "cols", "millions de personnes")]),
    ech=sheet("Continent · Échelle 15 pays", IN, "Échelle de service des 15 pays les moins équipés (%)", rows=["none:pays"],
              cols=["usr:m_val"], color="none:libelle", filters=["f_ech_zone", "f_annee", "f_retenu", "f_continent", "f_top15"],
              sort=("none:pays", "avg:rang_zone", "ASC"), label="usr:m_val", fmt=[("usr:m_val", "#,##0")],
              axis_titles=[("usr:m_val", "cols", "% de la population")]),
    vc=sheet("Continent · Ville campagne 15 pays", IN, "Ville et campagne dans ces 15 pays (accès basique, %)",
             rows=["none:pays", "none:lib_vc"], cols=["usr:m_val"], color="none:lib_vc",
             filters=["f_vc", "f_annee", "f_retenu", "f_continent", "f_top15"], sort=("none:pays", "avg:rang_zone", "ASC"),
             axis_titles=[("usr:m_val", "cols", "Accès basique (%)")]),
    dom=scatter_sheets("Continent", ["f_retenu", "f_continent"]),
)
# ---- Vue 3 : Pays
V["Pays"] = dict(
    kpi=kpi_sheets("Pays", ["f_annee", "f_pays"], ["pop", "basic", "safe", "sans", "mort", "urb", "stab", "score"]),
    line=sheet("Pays · Évolution", IN, "Évolution de l'accès à l'eau, 2000-2017", rows=["usr:m_val"], cols=["none:year"], mark="Line",
               color="none:libelle", filters=["f_courbe", "f_pays"], axis_titles=[("usr:m_val", "rows", "% de la population")]),
    map=map_sheet("Pays", "Situation dans le continent (pays choisi en foncé)", ["f_annee", "f_cont_pays"], color="none:f_pays"),
    comp=sheet("Pays · Comparaison", IN, "Le pays face à son continent et au monde (%)", rows=["usr:m_val"],
               cols=["none:indicateur", "none:niveau"], color="none:niveau", filters=["f_comp", "f_annee"],
               label="usr:m_val", fmt=[("usr:m_val", "#,##0")], axis_titles=[("usr:m_val", "rows", "%")]),
    pop=sheet("Pays · Population", IN, "Population urbaine et rurale (millions d'habitants)", rows=["usr:m_sum"], cols=["none:year"],
              color="none:libelle", filters=["f_pop", "f_pays"], axis_titles=[("usr:m_sum", "rows", "millions d'habitants")]),
    stab=sheet("Pays · Stabilité", IN, "Stabilité politique, 2000-2017 : pays et moyenne du continent", rows=["usr:m_val"], cols=["none:year"],
               mark="Line", color="none:niveau", filters=["f_stab"],
               axis_titles=[("usr:m_val", "rows", "indice (-2,5 à +2,5)")]),
    dom=scatter_sheets("Pays", ["f_cont_pays"], highlight=True),
)

# --------------------------------------------------------------------------------------------
# 4. Tableaux de bord (grille en pixels convertie en unités Tableau 0-100000)
# --------------------------------------------------------------------------------------------
W = 1400


class Dash:
    def __init__(self, name, height):
        self.name, self.H, self.zones, self.id = name, height, [], 10
        self.sheets = []

    def nid(self):
        self.id += 1
        return self.id

    def box(self, x, y, w, h):
        return (f"h='{round(h / self.H * 100000)}' w='{round(w / W * 100000)}' "
                f"x='{round(x / W * 100000)}' y='{round(y / self.H * 100000)}'")

    def sheet(self, name, x, y, w, h):
        self.sheets.append(name)
        self.zones.append(f"<zone {self.box(x, y, w, h)} id='{self.nid()}' name={A(name)} show-title='true' />")

    def kpis(self, names, y, h):
        w = W / len(names)
        for k, n in enumerate(names):
            self.sheets.append(n)
            self.zones.append(f"<zone {self.box(k * w, y, w, h)} id='{self.nid()}' name={A(n)} show-title='false' />")

    def param(self, p, mode, x, y, w, h):
        self.zones.append(f"<zone {self.box(x, y, w, h)} id='{self.nid()}' mode='{mode}' param={A(p)} type='paramctrl' />")

    def legend(self, sheet_name, field, x, y, w, h):
        self.zones.append(f"<zone {self.box(x, y, w, h)} id='{self.nid()}' leg-item-layout='horz' name={A(sheet_name)} "
                          f"pane-specification-id='0' param={A(field)} type='color' />")

    def text(self, runs, x, y, w, h):
        body = "".join(f"<run {a}>{escape(t)}</run>" for t, a in runs)
        self.zones.append(f"<zone {self.box(x, y, w, h)} id='{self.nid()}' type='text'><formatted-text>{body}</formatted-text></zone>")

    def xml(self):
        z = "\n".join("          " + s for s in self.zones)
        return (f"    <dashboard name={A(self.name)}>\n      <style />\n"
                f"      <size maxheight='{self.H}' maxwidth='{W}' minheight='{self.H}' minwidth='{W}' />\n      <zones>\n"
                f"        <zone h='100000' id='1' type='layout-basic' w='100000' x='0' y='0'>\n{z}\n        </zone>\n"
                f"      </zones>\n    </dashboard>\n")


def header(d, step, sous_titre, params):
    d.text([("DRINKING WATER FOR ALL · ÉTUDE D'ACCÈS À L'EAU POTABLE\n", f"fontcolor='{BLUE}' fontsize='9' bold='true'"),
            (f"{step}. Où concentrer les efforts de DWFA ? — Vue {d.name.split(' ', 1)[1]}\n", f"fontcolor='{INK}' fontsize='20' bold='true'"),
            (sous_titre, f"fontcolor='{MUTED}' fontsize='10'")], 0, 0, W, 90)
    w = W / len(params)
    for k, (p, mode) in enumerate(params):
        d.param(p, mode, k * w, 90, w, 60)


BASE_P = [(P_ANNEE, "slider"), (P_ZONE, "radiolist"), (P_STAB, "slider")]
DASHES = []

# Vue 1
d = Dash("1 Monde", 1880)
v = V["Monde"]
header(d, 1, "Pays exclus par le filtre de stabilité : grisés sur la carte et retirés des agrégats. Sources : OMS/UNICEF JMP, FAO, Banque mondiale, 2000-2017.", BASE_P)
d.kpis(v["kpi"], 150, 100)
d.sheet(v["map"], 0, 250, 930, 440); d.legend(v["map"], "[pays_annee].[none:classe:nk]", 0, 690, 930, 40)
d.sheet(v["sans"], 930, 250, 470, 480)
d.sheet(v["line"], 0, 730, 700, 340); d.sheet(v["ech"], 700, 730, 700, 340)
d.legend(v["line"], "[indicateurs].[none:libelle:nk]", 0, 1070, 700, 40); d.legend(v["ech"], "[indicateurs].[none:libelle:nk]", 700, 1070, 700, 40)
d.sheet(v["vc"], 0, 1110, W, 320)
for k, n in enumerate(v["dom"]):
    d.sheet(n, k * W / 3, 1430, W / 3, 450)
DASHES.append(d)

# Vue 2
d = Dash("2 Continent", 1960)
v = V["Continent"]
header(d, 2, "Choisir un continent ; les 15 pays les moins équipés sont classés selon la zone choisie.", BASE_P + [(P_CONT, "compact")])
d.kpis(v["kpi"], 150, 100)
d.sheet(v["map"], 0, 250, 800, 480); d.legend(v["map"], "[pays_annee].[none:classe:nk]", 0, 730, 800, 40)
d.sheet(v["line"], 800, 250, 600, 260); d.legend(v["line"], "[indicateurs].[none:libelle:nk]", 800, 510, 600, 40)
d.sheet(v["sans"], 800, 550, 600, 220)
d.sheet(v["ech"], 0, 770, 700, 520); d.sheet(v["vc"], 700, 770, 700, 520)
d.legend(v["ech"], "[indicateurs].[none:libelle:nk]", 0, 1290, 700, 40); d.legend(v["vc"], "[indicateurs].[none:lib_vc:nk]", 700, 1290, 700, 40)
for k, n in enumerate(v["dom"]):
    d.sheet(n, k * W / 3, 1330, W / 3, 630)
DASHES.append(d)

# Vue 3
d = Dash("3 Pays", 1900)
v = V["Pays"]
header(d, 3, "Choisir un pays : il est mis en évidence parmi les pays de son continent dans les trois domaines d'expertise.",
       BASE_P + [(P_PAYS, "compact")])
d.kpis(v["kpi"], 150, 100)
d.sheet(v["line"], 0, 250, 800, 400); d.legend(v["line"], "[indicateurs].[none:libelle:nk]", 0, 650, 800, 40)
d.sheet(v["map"], 800, 250, 600, 440)
d.sheet(v["comp"], 0, 690, 700, 360); d.sheet(v["pop"], 700, 690, 700, 360)
d.legend(v["comp"], "[indicateurs].[none:niveau:nk]", 0, 1050, 700, 40); d.legend(v["pop"], "[indicateurs].[none:libelle:nk]", 700, 1050, 700, 40)
d.sheet(v["stab"], 0, 1090, W, 360)
for k, n in enumerate(v["dom"]):
    d.sheet(n, k * W / 3, 1450, W / 3, 450)
DASHES.append(d)

# --------------------------------------------------------------------------------------------
# 5. Écriture du classeur
# --------------------------------------------------------------------------------------------
REMOTE = {"string": (129, "Count", "str"), "integer": (20, "Sum", "sint64"), "real": (5, "Sum", "double"), "boolean": (11, "Count", "bool")}


def metadata_xml(ds, raw_cols, parent, ind):
    """Liste des colonnes de la table : sans elle, Tableau ne rattache pas les champs des feuilles."""
    o = [f"{ind}<metadata-records>\n"]
    for k, c in enumerate(raw_cols):
        dt = ds.cols[c]["datatype"]
        code, agg, debug = REMOTE[dt]
        o.append(f"{ind}  <metadata-record class='column'>\n{ind}    <remote-name>{escape(c)}</remote-name>\n"
                 f"{ind}    <remote-type>{code}</remote-type>\n{ind}    <local-name>{escape('[' + c + ']')}</local-name>\n"
                 f"{ind}    <parent-name>{escape(parent)}</parent-name>\n{ind}    <remote-alias>{escape(c)}</remote-alias>\n"
                 f"{ind}    <ordinal>{k}</ordinal>\n{ind}    <local-type>{dt}</local-type>\n{ind}    <aggregation>{agg}</aggregation>\n"
                 + (f"{ind}    <scale>1</scale>\n{ind}    <width>1073741823</width>\n" if dt == "string" else "")
                 + f"{ind}    <contains-null>true</contains-null>\n"
                 + (f"{ind}    <collation flag='0' name='LROOT' />\n" if dt == "string" else "")
                 + f"{ind}    <attributes>\n{ind}      <attribute datatype='string' name='DebugRemoteType'>&quot;{debug}&quot;</attribute>\n"
                 f"{ind}    </attributes>\n{ind}  </metadata-record>\n")
    return "".join(o) + f"{ind}</metadata-records>\n"


def datasource_xml(ds, directory, extracts=None):
    o = [f"    <datasource caption={A(ds.caption)} inline='true' name={A(ds.name)} version='18.1'>\n"
         "      <connection class='federated'>\n        <named-connections>\n"
         f"          <named-connection caption={A(ds.filename)} name={A('textscan.' + ds.name)}>\n"
         f"            <connection class='textscan' directory={A(directory)} filename={A(ds.filename)} password='' server='' />\n"
         "          </named-connection>\n        </named-connections>\n"
         f"        <relation connection={A('textscan.' + ds.name)} name={A(ds.filename)} table={A('[' + ds.filename.replace('.', '#') + ']')} type='table'>\n"
         "          <columns character-set='UTF-8' header='yes' locale='en_US' separator=','>\n"]
    raw_cols = [c for c in ds.cols if ds.cols[c]["formula"] is None and not ds.cols[c].get("generated")]
    for k, c in enumerate(raw_cols):
        o.append(f"            <column datatype='{ds.cols[c]['datatype']}' name={A(c)} ordinal='{k}' />\n")
    o.append("          </columns>\n        </relation>\n")
    o.append(metadata_xml(ds, raw_cols, f"[{ds.filename.replace('.', '#')}]", "        "))
    o.append("      </connection>\n      <aliases enabled='yes' />\n")
    for c in ds.cols:
        if not ds.cols[c].get("generated"):
            o.append(ds.col_xml(c))
    if extracts:  # Tableau Public n'ouvre que des sources en extrait
        hyper = f"{extracts}/{ds.name}.hyper"
        o.append("      <extract count='-1' enabled='true' units='records'>\n"
                 f"        <connection authentication='auth-none' class='hyper' dbname={A(hyper)} default-settings='hyper' "
                 "schema='Extract' sslmode='' tablename='Extract' username='tableau_internal_user'>\n"
                 "          <relation name='Extract' table='[Extract].[Extract]' type='table' />\n"
                 + metadata_xml(ds, raw_cols, "[Extract]", "          ") +
                 "        </connection>\n      </extract>\n")
    o.append("      <style>\n        <style-rule element='mark'>\n")
    for (d_, field), m in COLORS.items():
        if d_ is ds:
            r = inst(ds, f"none:{field}")[0]
            o.append(f"          <encoding attr='color' field={A(r)} type='palette'>\n")
            for k_, col in m.items():
                key = k_ if ds.cols[field]["datatype"] == "boolean" else Q(k_)
                o.append(f"            <map to='{col}'>\n              <bucket>{escape(key)}</bucket>\n            </map>\n")
            o.append("          </encoding>\n")
    o.append("        </style-rule>\n      </style>\n    </datasource>\n")
    return "".join(o)


def workbook(directory, extracts=None):
    o = ["<?xml version='1.0' encoding='utf-8' ?>\n\n"
         "<!-- build data-dev.0.0000.0000                             -->\n"
         "<workbook locale='fr_FR' source-build='0.0.0 (0000.0.0.0)' source-platform='mac' version='18.1' "
         "xmlns:user='http://www.tableausoftware.com/xml/user'>\n  <preferences>\n"
         "    <preference name='ui.encoding.shelf.height' value='24' />\n    <preference name='ui.shelf.height' value='26' />\n"
         "  </preferences>\n  <datasources>\n    <datasource hasconnection='false' inline='true' name='Parameters' version='18.1'>\n"
         "      <aliases enabled='yes' />\n"]
    o += [param_xml(p, "      ") for p in PARAMS]
    o.append("    </datasource>\n")
    o += [datasource_xml(ds, directory, extracts) for ds in (PA, IN)]
    o.append("  </datasources>\n  <mapsources>\n    <mapsource name='Tableau' />\n  </mapsources>\n  <worksheets>\n")
    o += [s.xml() for s in SHEETS]
    o.append("  </worksheets>\n  <dashboards>\n")
    o += [d.xml() for d in DASHES]
    o.append("  </dashboards>\n  <windows source-height='30'>\n")
    for d in DASHES:
        o.append(f"    <window class='dashboard' maximized='true' name={A(d.name)}>\n      <viewpoints>\n"
                 + "".join(f"        <viewpoint name={A(n)} />\n" for n in d.sheets)
                 + f"      </viewpoints>\n      <active id='-1' />\n    </window>\n")
    for s in SHEETS:
        o.append(f"    <window class='worksheet' name={A(s.name)}>\n"
                 "      <cards>\n        <edge name='left'>\n          <strip size='160'>\n            <card type='pages' />\n"
                 "            <card type='filters' />\n            <card type='marks' />\n          </strip>\n        </edge>\n"
                 "        <edge name='top'>\n          <strip size='2147483647'>\n            <card type='columns' />\n          </strip>\n"
                 "          <strip size='2147483647'>\n            <card type='rows' />\n          </strip>\n"
                 "          <strip size='2147483647'>\n            <card type='title' />\n          </strip>\n        </edge>\n      </cards>\n"
                 "    </window>\n")
    o.append("  </windows>\n</workbook>\n")
    return "".join(o)


# Latitude / Longitude générées par Tableau à partir du rôle géographique de iso3
for ds in (PA,):
    for c in ("Latitude (generated)", "Longitude (generated)"):
        ds.cols[c] = dict(caption=None, datatype="real", role="measure", type="quantitative", formula=None, extra="", generated=True)

HYPER_TYPES = {"string": "TEXT", "integer": "BIG_INT", "real": "DOUBLE", "boolean": "BOOL"}


def build_hyper(ds, frame, path):
    """Écrit l'extrait Tableau (schéma Extract, table Extract) d'une source à partir du DataFrame."""
    from tableauhyperapi import (Connection, CreateMode, HyperProcess, Inserter, SqlType, TableDefinition,
                                 TableName, Telemetry)
    raw = [c for c in ds.cols if ds.cols[c]["formula"] is None and not ds.cols[c].get("generated")]
    table = TableDefinition(TableName("Extract", "Extract"),
                            [TableDefinition.Column(c, getattr(SqlType, HYPER_TYPES[ds.cols[c]["datatype"]].lower())()) for c in raw])
    # conversion valeur par valeur : pandas remettrait des NaN à la place des None (Tableau ne les voit pas comme vides)
    cast = {"string": str, "integer": int, "real": float, "boolean": bool}

    def clean(v, dt):
        return None if v is None or (isinstance(v, float) and np.isnan(v)) or v is pd.NA else cast[dt](v)

    types = [ds.cols[c]["datatype"] for c in raw]
    rows = [[clean(v, dt) for v, dt in zip(r, types)] for r in frame[raw].itertuples(index=False, name=None)]
    with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hp:
        with Connection(hp.endpoint, str(path), CreateMode.CREATE_AND_REPLACE) as cx:
            cx.catalog.create_schema("Extract")
            cx.catalog.create_table(table)
            with Inserter(cx, table) as ins:
                ins.add_rows(rows)
                ins.execute()


if __name__ == "__main__":
    (OUT / "DWFA.twb").write_text(workbook(str(DATA)), encoding="utf-8")
    # extraits .hyper (nécessite : pip install tableauhyperapi) ; sans eux, Tableau Public refuse d'ouvrir le classeur
    build_hyper(PA, wide, DATA / "pays_annee.hyper")
    build_hyper(IN, long, DATA / "indicateurs.hyper")
    with zipfile.ZipFile(OUT / "DWFA.twbx", "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("DWFA.twb", workbook("Data/donnees", extracts="Data/Extracts"))
        for f in ("pays_annee.csv", "indicateurs.csv"):
            z.write(DATA / f, f"Data/donnees/{f}")
        for f in ("pays_annee.hyper", "indicateurs.hyper"):
            z.write(DATA / f, f"Data/Extracts/{f}")
    print(f"{len(wide)} lignes pays-année · {len(long)} lignes indicateurs · {len(SHEETS)} feuilles · {len(DASHES)} tableaux de bord")
