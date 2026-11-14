"""Génère livrables/Document_de_synthese_DWFA.docx (indicateurs retenus par vue + maquette)."""
from pathlib import Path
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

LIV = Path(__file__).resolve().parents[1]
CAP = LIV / "captures"
BLUE, INK, MUTED = RGBColor(0x1C, 0x5C, 0xAB), RGBColor(0x0B, 0x22, 0x36), RGBColor(0x5F, 0x74, 0x88)

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
for side in ("left_margin", "right_margin"):
    setattr(sec, side, Cm(2))
sec.top_margin = sec.bottom_margin = Cm(1.8)

st = doc.styles["Normal"]
st.font.name, st.font.size, st.font.color.rgb = "Calibri", Pt(10.5), INK
st.paragraph_format.space_after = Pt(4)
for name, size in (("Title", 24), ("Heading 1", 15), ("Heading 2", 12)):
    s = doc.styles[name]
    s.font.name, s.font.size, s.font.color.rgb, s.font.bold = "Cambria", Pt(size), BLUE if name != "Title" else INK, True
doc.styles["Heading 1"].paragraph_format.space_before = Pt(14)
doc.styles["Heading 2"].paragraph_format.space_before = Pt(8)


def shade(cell, hex_):
    tc = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), hex_)
    tc.append(sh)


def table(headers, rows, widths):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for k, h in enumerate(headers):
        c = t.rows[0].cells[k]
        c.text = ""
        r = c.paragraphs[0].add_run(h); r.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF); r.font.size = Pt(9.5)
        shade(c, "1C5CAB")
    for row in rows:
        cells = t.add_row().cells
        for k, v in enumerate(row):
            cells[k].text = ""
            r = cells[k].paragraphs[0].add_run(str(v)); r.font.size = Pt(9.5)
            if k == 0: r.bold = True
    for row in t.rows:
        for k, w in enumerate(widths):
            row.cells[k].width = Cm(w)
    # ligne d'en-tête répétée (accessibilité / lecture multi-pages)
    trPr = t.rows[0]._tr.get_or_add_trPr(); h = OxmlElement("w:tblHeader"); h.set(qn("w:val"), "true"); trPr.append(h)
    doc.add_paragraph()
    return t


def para(text, bold_lead=None, size=None, color=None):
    p = doc.add_paragraph()
    if bold_lead:
        p.add_run(bold_lead).bold = True
    r = p.add_run(text)
    if size: r.font.size = Pt(size)
    if color: r.font.color.rgb = color
    return p


def bullets(items):
    for it in items:
        p = doc.add_paragraph(style="List Bullet")
        if isinstance(it, tuple):
            p.add_run(it[0]).bold = True; p.add_run(it[1])
        else:
            p.add_run(it)


def image(path, width_cm, caption):
    doc.add_picture(str(path), width=Cm(width_cm))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    # texte alternatif pour les lecteurs d'écran
    doc.inline_shapes[-1]._inline.docPr.set("descr", caption)
    c = para(caption, size=9, color=MUTED); c.alignment = WD_ALIGN_PARAGRAPH.CENTER


# ------------------------------------------------------------------ couverture
doc.add_paragraph("Drinking Water For All · Étude d'accès à l'eau potable").runs[0].font.color.rgb = MUTED
doc.add_heading("Document de synthèse : indicateurs et vues du tableau de bord", level=0)
para("À l'attention de Thibaut Renard, chef de mission. Auteur : Mathéo Gerard, consultant Data Analyst. Octobre 2026.", color=MUTED)
para("Le tableau de bord répond à deux questions : quels pays rencontrent des difficultés d'accès à l'eau potable, et dans lesquels "
     "concentrer les efforts de DWFA pour chacun de ses trois domaines d'expertise. Il comporte trois vues emboîtées (Monde, Continent, Pays) "
     "qui partagent les mêmes indicateurs et les mêmes filtres, dont un filtre d'exclusion des pays trop instables.")

# ------------------------------------------------------------------ 1. données
doc.add_heading("1. Données utilisées et préparation", level=1)
table(["Fichier", "Contenu", "Source", "Période", "Granularité"], [
    ["BasicAndSafelyManagedDrinkingWaterServices", "% de population avec accès basique et accès sûr", "OMS / UNICEF (JMP)", "2000-2017", "Total, urbain, rural"],
    ["Population", "Population (milliers d'habitants)", "FAO", "2000-2018", "Total, urbain, rural, H/F"],
    ["MortalityRateAttributedToWater", "Mortalité attribuée à l'eau, l'assainissement et l'hygiène insalubres (WASH), décès", "OMS", "2016", "Total, H/F"],
    ["PoliticalStability", "Indice de stabilité politique (-2,5 à +2,5)", "Banque mondiale via FAO", "2000-2018 (2001 absent)", "Total"],
    ["RegionCountry", "Région OMS de chaque pays (194 pays)", "OMS", "-", "-"],
], [4.2, 4.6, 2.8, 2.4, 2.8])
para("Étapes de préparation (script preparation/preparation_donnees.py) :", bold_lead=None)
bullets([
    ("Harmonisation des noms : ", "les noms FAO sont alignés sur ceux de l'OMS (North Macedonia, China mainland) ; un référentiel ajoute le code ISO3 et le nom français."),
    ("Cas du Soudan : ", "la FAO ne sépare Soudan et Soudan du Sud qu'à partir de 2012 ; avant, la population du « Soudan (ancien) » est répartie selon les parts de 2012."),
    ("Valeurs manquantes : ", "l'indice de stabilité 2001, absent de la source, est interpolé linéairement ; les autres trous restent vides (affichés « n.d. »), sans imputation."),
    ("Jointures : ", "jointures à gauche sur le couple pays-année à partir des 194 pays OMS, pour qu'aucun pays ne disparaisse quand une source est muette."),
    ("Champs calculés : ", "population × 1 000 (source en milliers), taux d'urbanisation, personnes sans accès basique, écart basique - sûr, score d'efficacité, moyennes pondérées par la population pour les agrégats."),
    ("Modèle de données : ", "schéma en étoile (dim_pays, fait_pays_annee, fait_mortalite_2016) pré-agrégé par pays et par année : 3 492 lignes au lieu de plus de 35 000, pour un affichage instantané."),
])

# ------------------------------------------------------------------ 2. indicateurs
doc.add_heading("2. Indicateurs retenus", level=1)
doc.add_heading("Indicateurs généraux (présents sur les trois vues)", level=2)
table(["Indicateur", "Définition / calcul", "Pourquoi"], [
    ["Accès basique (%)", "Part de la population disposant d'un point d'eau amélioré à moins de 30 min aller-retour", "Mesure principale du besoin d'accès"],
    ["Accès sûr (%)", "Eau au domicile, disponible et non contaminée (« safely managed »)", "Mesure la qualité du service"],
    ["Personnes sans accès basique", "Population × (100 - accès basique) / 100", "Traduit un taux en nombre de personnes concernées"],
    ["Mortalité WASH", "Décès pour 100 000 habitants attribués à l'eau insalubre (2016)", "Conséquence sanitaire du manque d'accès"],
    ["Population, taux d'urbanisation", "Population totale ; population urbaine / totale", "Taille du besoin ; type d'infrastructure à construire"],
    ["Stabilité politique", "Indice Banque mondiale, de -2,5 (très instable) à +2,5", "Faisabilité d'une intervention ; sert de filtre"],
    ["Évolution 2000-2017", "Séries annuelles de l'accès basique (total, urbain, rural) et sûr", "Distinguer les pays qui progressent de ceux qui stagnent"],
], [4, 7.5, 5.3])
para("Agrégation : au niveau mondial et continental, les taux sont des moyennes pondérées par la population (et non des moyennes simples, "
     "qui donneraient le même poids à Malte et à l'Inde). La stabilité est une moyenne simple des pays.")

doc.add_heading("Indicateurs des trois domaines d'expertise (nuages de points)", level=2)
table(["Domaine", "Axe X", "Axe Y", "Lecture : pays ciblés"], [
    ["1 · Création de services", "Taux d'urbanisation", "Accès basique (taille du point : personnes sans accès)", "En bas à gauche : accès faible et population rurale, besoin de créer des services"],
    ["2 · Modernisation", "Accès basique", "Accès sûr (diagonale = pas d'écart)", "En bas à droite : service basique présent mais de mauvaise qualité, à moderniser"],
    ["3 · Consulting", "Stabilité politique (2016)", "Score d'efficacité de la politique de l'eau", "En bas à droite : pays stables mais politique peu efficace, à conseiller"],
], [3.6, 3.2, 4.6, 5.4])
para("Score d'efficacité (0-100, 2016) = 50 % × accès basique normalisé + 50 % × (100 - mortalité WASH normalisée). "
     "La mortalité est normalisée sur une échelle logarithmique car elle va de 0,01 à 101 pour 100 000 habitants : "
     "sans logarithme, tous les pays à faible mortalité seraient écrasés au même niveau. Les deux composantes sont ramenées entre 0 et 100 (min-max).")

# ------------------------------------------------------------------ 3. vues
doc.add_heading("3. Les trois vues", level=1).paragraph_format.page_break_before = True
views = [
    ("Vue 1 · Monde", "Où sont les besoins dans le monde ?", "blueprint_vue_monde.png", [
        ["Carte choroplèthe de l'accès basique par pays", "Géographique", "Repérer d'un coup d'œil les zones en difficulté ; clic = fiche pays"],
        ["Barres : personnes sans accès basique par continent", "Barres", "Où se concentrent les besoins en nombre de personnes"],
        ["Évolution de l'accès 2000-2017 (basique T/U/R, sûr)", "Line plot (temporel)", "Tendance mondiale"],
        ["Échelle de service par continent (sûr / basique / sans)", "Percent stacked barplot", "Qualité de service par continent"],
        ["Accès urbain vs rural par continent", "Grouped barplot", "Écart ville-campagne"],
        ["Trois nuages de points des domaines", "Scatter plot", "Pays candidats de chaque domaine"]]),
    ("Vue 2 · Continent", "Quels pays du continent choisi sont les plus en retard ?", "blueprint_vue_continent.png", [
        ["Carte zoomée sur le continent", "Géographique", "Situer les pays du continent"],
        ["Évolution de l'accès du continent", "Line plot (temporel)", "Tendance du continent"],
        ["Les 8 pays avec le plus de personnes sans accès", "Barres", "Prioriser par nombre de personnes"],
        ["Échelle de service des 15 pays les moins équipés", "Percent stacked barplot", "Comparer la qualité de service"],
        ["Accès urbain / rural de ces 15 pays", "Grouped barplot", "Choisir entre infrastructures urbaines et rurales"],
        ["Trois nuages de points des domaines (pays du continent)", "Scatter plot", "Candidats par domaine"]]),
    ("Vue 3 · Pays", "Le pays choisi est-il une bonne cible, et pour quel domaine ?", "blueprint_vue_pays.png", [
        ["Évolution de l'accès basique (T/U/R) et sûr", "Line plot (temporel)", "Le pays progresse-t-il ?"],
        ["Carte du continent, pays encadré", "Géographique", "Contexte régional ; navigation vers les voisins"],
        ["Pays vs continent vs monde", "Grouped barplot", "Situer le pays"],
        ["Population urbaine et rurale 2000-2017", "Stacked barplot", "Dynamique démographique"],
        ["Stabilité politique 2000-2017 et seuil du filtre", "Line plot", "Risque d'intervention"],
        ["Trois nuages de points, pays mis en évidence", "Scatter plot", "Position du pays dans chaque domaine"]]),
]
for k, (title, question, img, rows) in enumerate(views):
    h = doc.add_heading(title, level=2)
    if k: h.paragraph_format.page_break_before = True
    para(question, bold_lead="Question : ")
    image(CAP / img, 15, f"Maquette basse fidélité (blueprint) de la {title.lower()}.")
    table(["Graphique", "Type", "Rôle"], rows, [7.6, 3.8, 5.4])

# ------------------------------------------------------------------ 4. filtres
doc.add_heading("4. Filtres", level=1)
table(["Filtre", "Type de variable", "Vues", "Effet"], [
    ["Année (curseur 2000-2017)", "Temporelle", "Toutes", "Recalcule cartes, indicateurs et graphiques pour l'année choisie"],
    ["Zone : total / urbain / rural", "Qualitative", "Toutes", "Bascule tous les taux d'accès sur la zone choisie"],
    ["Stabilité politique minimale (-3,5 à +1,5)", "Quantitative", "Toutes", "Exclut des agrégats et grise sur la carte les pays trop instables pour une intervention"],
    ["Continent (région OMS)", "Géographique", "Continent, Pays", "Choisit le continent agrégé"],
    ["Pays (liste ou clic sur la carte / un point)", "Géographique", "Pays", "Ouvre la fiche du pays"],
], [5, 2.8, 2.6, 6.4])

# ------------------------------------------------------------------ 5. accessibilité
doc.add_heading("5. Palette, accessibilité et adaptation à l'auditoire", level=1)
bullets([
    ("Palette « Bleu » imposée : ", "une seule teinte, du bleu clair au bleu profond ; plus c'est foncé, meilleur est l'accès. Lisible par les personnes daltoniennes car l'information est portée par la luminosité, pas par la teinte."),
    ("Jamais la couleur seule : ", "les séries se distinguent aussi par le style de trait (plein, tirets, pointillés) ; les pays exclus par le filtre sont hachurés ; chaque graphique a un titre, des axes nommés avec unités, et des valeurs affichées."),
    ("Contrastes : ", "textes et éléments graphiques au-dessus des ratios WCAG AA (4,5:1 pour le texte) ; thème sombre automatique."),
    ("Clavier et lecteurs d'écran : ", "onglets navigables aux flèches, filtres étiquetés, focus visible, lien d'évitement, descriptions textuelles des graphiques, et un tableau de données dépliable sous chaque vue."),
    ("Auditoire non spécialiste : ", "une phrase clé chiffrée en tête de chaque vue, des indicateurs en grands chiffres, des repères de lecture sur les nuages de points (« accès faible et rural : créer »), et les pays candidats annotés directement."),
])

# ------------------------------------------------------------------ 6. conformité
doc.add_heading("6. Conformité au compte rendu de la réunion de lancement", level=1)
table(["Exigence", "Réponse"], [
    ["3 vues : monde, continent, pays", "Onglets 1 Monde, 2 Continent, 3 Pays"],
    ["Line plot, scatter plot, grouped barplot, (percent) stacked barplot", "Les quatre types sont présents sur chaque vue"],
    ["Données temporelles", "Courbes 2000-2017 et curseur d'année"],
    ["Données géographiques (option A)", "Cartes choroplèthes cliquables"],
    ["4 filtres : quantitatif, qualitatif, temporel, géographique", "Stabilité, zone, année, continent/pays (5 filtres)"],
    ["Filtre d'exclusion des pays instables", "Curseur de stabilité minimale"],
    ["Nuages de points pour les indicateurs à 2 variables", "Les trois indicateurs de domaine sont des scatter plots"],
    ["Champ calculé / agrégation", "× 1 000, moyennes pondérées, personnes sans accès, score d'efficacité"],
    ["Jointure", "Pays × année entre les 5 fichiers"],
    ["Palette Bleu, accessibilité, modèle optimisé", "Voir sections 1 et 5"],
], [8, 8.8])

doc.save(LIV / "Document_de_synthese_DWFA.docx")
print("ok")
