// Génère livrables/Presentation_DWFA.pptx
// node livrables/sources/presentation.js   (pptxgenjs requis ; APPLY_THEME = chemin vers apply_theme.js, optionnel)
const path = require("path");
const pptxgen = require("pptxgenjs");

const LIV = path.resolve(__dirname, "..");
const CAP = path.join(LIV, "captures");
const OUT = path.join(LIV, "Presentation_DWFA.pptx");

const THEME = {
  name: "DWFA Bleu", headFontFace: "Cambria", bodyFontFace: "Calibri",
  colors: { dk1: "0B2236", lt1: "FFFFFF", dk2: "1C5CAB", lt2: "EEF4F9",
    accent1: "1C5CAB", accent2: "5598E7", accent3: "0D366B", accent4: "9EC5F4", accent5: "3987E5", accent6: "5F7488",
    hlink: "1C5CAB", folHlink: "0D366B" },
};
const HEX = THEME.colors;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13,33 x 7,5 in
pres.title = "DWFA - Où concentrer nos efforts ? Étude d'accès à l'eau potable";
pres.author = "Mathéo Gerard";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;

const W = 13.333, M = 0.6;

// ------------------------------------------------------------------ layouts
pres.defineSlideMaster({
  title: "TITRE", background: { color: C.text1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 2.2, w: 11.5, h: 1.6, fontSize: 44, bold: true, color: C.background1, fontFace: "Cambria", valign: "bottom", align: "left" }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: M, y: 4.0, w: 11.5, h: 1.4, fontSize: 18, color: C.accent4, valign: "top", align: "left" }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENU", background: { color: C.background1 }, margin: [0.5, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.35, w: W - 2 * M, h: 0.95, fontSize: 30, bold: true, color: C.text1, fontFace: "Cambria", valign: "middle", align: "left" }, text: "" } },
    { text: { text: "DWFA · Étude d'accès à l'eau potable", options: { x: M, y: 7.0, w: 6, h: 0.3, fontSize: 10, color: C.accent6, margin: 0 } } },
  ],
  slideNumber: { x: W - M - 0.5, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: HEX.accent6, align: "right" },
});

let n = 0;
const sections = {};
function slide(master, section) {
  if (!sections[section]) { pres.addSection({ title: section }); sections[section] = true; }
  n++;
  return pres.addSlide({ masterName: master, sectionTitle: section });
}
const T = (s, text, o) => s.addText(text, Object.assign({ isTextBox: true, fontSize: 15, color: C.text1, valign: "top", margin: 0 }, o));
function card(s, x, y, w, h, fill = C.background2) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { type: "none" } });
}
function num(s, x, y, k, fill = C.accent1) { // pastille numérotée (motif de la présentation)
  s.addShape(pres.shapes.OVAL, { x, y, w: 0.5, h: 0.5, fill: { color: fill }, line: { type: "none" } });
  T(s, String(k), { x, y, w: 0.5, h: 0.5, fontSize: 16, bold: true, color: C.background1, align: "center", valign: "middle" });
}
function img(s, file, x, y, w, h, alt) { s.addImage({ path: path.join(CAP, file), x, y, w, h, altText: alt }); }

// ================================================================== 1. titre
let s = slide("TITRE", "Introduction");
s.addText("Où concentrer les efforts de DWFA ?", { placeholder: "title" });
s.addText("Étude d'accès à l'eau potable : tableau de bord et recommandations\nMathéo Gerard, consultant Data Analyst · octobre 2026", { placeholder: "body" });
s.addNotes("Bonjour. Je vais vous présenter le tableau de bord construit pour DWFA, qui sert à choisir dans quel pays et dans quel domaine d'expertise investir les nouveaux financements. Plan : contexte, données et préparation, choix de l'outil, les trois vues, puis une démonstration en direct et mes recommandations.");

// ================================================================== 2. contexte
s = slide("CONTENU", "Contexte");
s.addText("Un financement à placer : quel pays, quel domaine ?", { placeholder: "title" });
T(s, "DWFA a demandé un financement à un bailleur de fonds. S'il est accordé, il sera investi dans un seul de ses trois domaines d'expertise, dans un pays encore à choisir.",
  { x: M, y: 1.45, w: 12, h: 0.8, fontSize: 16, color: C.text1 });
const doms = [["1", "Création", "Créer des services d'accès à l'eau potable là où il n'y en a pas."],
  ["2", "Modernisation", "Moderniser des services existants dont la qualité est insuffisante."],
  ["3", "Consulting", "Conseiller administrations et gouvernements sur leurs politiques de l'eau."]];
doms.forEach(([k, t, d], i) => {
  const x = M + i * 4.1;
  card(s, x, 2.55, 3.85, 2.3);
  num(s, x + 0.3, 2.8, k);
  T(s, t, { x: x + 0.95, y: 2.83, w: 2.7, h: 0.45, fontSize: 20, bold: true, color: C.accent1, valign: "middle" });
  T(s, d, { x: x + 0.3, y: 3.5, w: 3.3, h: 1.2, fontSize: 15 });
});
T(s, "Le besoin exprimé par le chef de mission", { x: M, y: 5.15, w: 12, h: 0.4, fontSize: 16, bold: true, color: C.accent3 });
T(s, [
  { text: "Identifier les pays qui rencontrent des difficultés d'accès à l'eau potable.", options: { bullet: true, breakLine: true } },
  { text: "Identifier ceux où concentrer nos efforts, pour chacun des trois domaines.", options: { bullet: true, breakLine: true } },
  { text: "Trois vues (monde, continent, pays), un filtre pour exclure les pays trop instables, la palette Bleu.", options: { bullet: true } },
], { x: M, y: 5.55, w: 12, h: 1.3, fontSize: 15, paraSpaceAfter: 4 });
s.addNotes("DWFA, Drinking Water For All, veut donner accès à l'eau potable à tous. Elle a trois domaines d'expertise. Le bailleur financera un seul domaine dans un seul pays : le tableau de bord doit donc aider à comparer les pays sous l'angle de chaque domaine, tout en écartant les pays où l'instabilité politique rend une intervention trop risquée.");

// ================================================================== 3. données
s = slide("CONTENU", "Données");
s.addText("Cinq fichiers, trois organismes, 194 pays de 2000 à 2017", { placeholder: "title" });
const hdr = (t) => ({ text: t, options: { bold: true, color: HEX.lt1, fill: { color: HEX.accent1 } } });
const rows = [
  [hdr("Fichier"), hdr("Contenu"), hdr("Source"), hdr("Années"), hdr("Granularité")],
  ["Accès à l'eau potable", "% de la population avec accès basique et accès sûr", "OMS / UNICEF", "2000-2017", "Total, urbain, rural"],
  ["Population", "Habitants (en milliers)", "FAO", "2000-2018", "Total, urbain, rural, H/F"],
  ["Mortalité WASH", "Décès dus à l'eau, l'assainissement et l'hygiène insalubres", "OMS", "2016", "Total, H/F"],
  ["Stabilité politique", "Indice de -2,5 (instable) à +2,5 (stable)", "Banque mondiale", "2000-2018, sauf 2001", "Total"],
  ["Région / pays", "Continent (région OMS) de chaque pays", "OMS", "-", "-"],
];
s.addTable(rows, { x: M, y: 1.5, w: 12.1, colW: [2.4, 4.1, 1.9, 1.9, 1.8], fontSize: 14, color: HEX.dk1, fontFace: "Calibri",
  border: { type: "solid", pt: 0.75, color: "D3E0EB" }, rowH: 0.55, valign: "middle", margin: [0.05, 0.1, 0.05, 0.1] });
card(s, M, 5.3, 12.1, 1.35);
T(s, [
  { text: "Deux définitions à retenir. ", options: { bold: true, color: HEX.accent3 } },
  { text: "Accès basique : un point d'eau amélioré à moins de 30 minutes aller-retour. Accès sûr (« safely managed ») : de l'eau au domicile, disponible quand nécessaire et non contaminée. Les données « sûr » ne couvrent qu'environ la moitié des pays." },
], { x: M + 0.3, y: 5.45, w: 11.5, h: 1.1, fontSize: 15 });
s.addNotes("Les données ont été collectées par un data engineer : OMS pour l'eau et la mortalité, FAO pour la population, Banque mondiale pour la stabilité. Point de vigilance : l'accès sûr n'est renseigné que pour environ la moitié des pays-années, et la mortalité n'existe que pour 2016.");

// ================================================================== 4. prétraitement
s = slide("CONTENU", "Données");
s.addText("Prétraitement : du brut à un modèle prêt à afficher", { placeholder: "title" });
const steps = [
  ["Harmoniser", "Noms de pays FAO alignés sur l'OMS ; code ISO3 et nom français ajoutés"],
  ["Nettoyer", "Soudan scindé avant 2012 ; stabilité 2001 interpolée ; manques laissés vides"],
  ["Joindre", "Jointures à gauche pays × année sur les 194 pays OMS"],
  ["Calculer", "Population × 1 000, urbanisation, personnes sans accès, score d'efficacité"],
  ["Modéliser", "Schéma en étoile pré-agrégé : 3 492 lignes au lieu de 35 000"],
];
const sw = 2.3, gap = 0.15;
steps.forEach(([t, d], i) => {
  const x = M + i * (sw + gap);
  card(s, x, 1.6, sw, 3.3, i === 4 ? C.accent1 : C.background2);
  num(s, x + 0.25, 1.85, i + 1, i === 4 ? C.accent3 : C.accent1);
  T(s, t, { x: x + 0.25, y: 2.5, w: sw - 0.4, h: 0.45, fontSize: 19, bold: true, color: i === 4 ? C.background1 : C.accent1 });
  T(s, d, { x: x + 0.25, y: 3.05, w: sw - 0.4, h: 1.75, fontSize: 14, color: i === 4 ? C.background1 : C.text1 });
});
T(s, "Modèle de données", { x: M, y: 5.15, w: 4, h: 0.4, fontSize: 16, bold: true, color: C.accent3 });
const tables = [["dim_pays", "194 pays · ISO3, nom, continent"], ["fait_pays_annee", "3 492 lignes · population, accès, stabilité"], ["fait_mortalite_2016", "183 pays · mortalité, décès, score"]];
tables.forEach(([t, d], i) => {
  const x = M + i * 4.1;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 5.6, w: 3.7, h: 0.95, rectRadius: 0.08, fill: { color: C.background1 }, line: { color: C.accent2, width: 1.25 } });
  T(s, [{ text: t, options: { bold: true, breakLine: true, color: HEX.accent3 } }, { text: d, options: { fontSize: 13 } }], { x: x + 0.2, y: 5.7, w: 3.4, h: 0.8, fontSize: 15 });
  if (i < 2) s.addShape(pres.shapes.LINE, { x: x + 3.7, y: 6.07, w: 0.4, h: 0, line: { color: C.accent2, width: 1.5 } });
});
s.addNotes("Le prétraitement est entièrement scripté en Python (preparation/preparation_donnees.py), donc reproductible. Points notables : la FAO ne sépare le Soudan et le Soudan du Sud qu'à partir de 2012, j'ai donc réparti l'ancien Soudan selon les parts de 2012 ; l'année 2001 manque pour la stabilité, je l'ai interpolée. Je n'ai pas imputé les autres valeurs manquantes : elles s'affichent 'n.d.'. Le modèle est pré-agrégé par pays et par année, ce qui rend l'affichage instantané. Les mêmes fichiers CSV se chargent tels quels dans Tableau ou Power BI.");

// ================================================================== 5. outil
s = slide("CONTENU", "Outil");
s.addText("Outil retenu : un tableau de bord web en Plotly", { placeholder: "title" });
const crit = [
  [hdr("Critère"), hdr("Tableau Public"), hdr("Power BI"), hdr("Plotly (retenu)")],
  ["Coût et licence", "Gratuit, données publiques", "Licence pour partager", "Gratuit, open source"],
  ["Partage", "Lien Tableau Public", "Compte Microsoft requis", "Simple lien web, sans compte"],
  ["Accessibilité", "Limitée et peu réglable", "Correcte", "Totale : clavier, contrastes, tableau de données"],
  ["Palette Bleu, mise en page", "Contrainte par l'outil", "Contrainte par l'outil", "Entièrement maîtrisées"],
  ["Reproductibilité", "Manipulations à la souris", "Power Query", "Script Python versionné dans Git"],
  ["Prise en main", "Rapide", "Rapide", "Plus longue (code)"],
];
s.addTable(crit, { x: M, y: 1.5, w: 12.1, colW: [2.8, 3.0, 3.0, 3.3], fontSize: 14, color: HEX.dk1, fontFace: "Calibri",
  border: { type: "solid", pt: 0.75, color: "D3E0EB" }, rowH: 0.52, valign: "middle", margin: [0.05, 0.1, 0.05, 0.1] });
card(s, M, 5.4, 12.1, 1.2);
T(s, [
  { text: "Pourquoi ce choix. ", options: { bold: true, color: HEX.accent3 } },
  { text: "Plotly est la bibliothèque vue en cours. Elle couvre les 4 types de graphiques imposés, la carte et les filtres. Elle donne la maîtrise de l'accessibilité, et le tableau de bord s'ouvre partout avec un simple lien. Le modèle reste compatible Tableau / Power BI." },
], { x: M + 0.3, y: 5.55, w: 11.5, h: 1.0, fontSize: 15 });
s.addNotes("Le mail laissait le choix entre Tableau et Power BI ; j'ai retenu une solution web en Plotly, la bibliothèque utilisée en cours, pour trois raisons : l'accessibilité (navigation clavier, tableau de données sous chaque vue, contraste), le partage par simple lien sans compte, et la reproductibilité du traitement. La contrepartie est un temps de développement plus long. Si DWFA préfère Tableau, le modèle de données CSV s'y charge directement.");

// ================================================================== 6. indicateurs
s = slide("CONTENU", "Indicateurs");
s.addText("Un indicateur et un nuage de points par domaine d'expertise", { placeholder: "title" });
const ind = [
  ["1", "Création", "Taux d'urbanisation", "Accès basique", "Taille du point : personnes sans accès. En bas à gauche : accès faible et population rurale."],
  ["2", "Modernisation", "Accès basique", "Accès sûr", "Sous la diagonale : service présent mais de mauvaise qualité."],
  ["3", "Consulting", "Stabilité politique", "Score d'efficacité", "Score = 50 % accès basique + 50 % faible mortalité (log), normalisés. À droite et en bas : stable mais peu efficace."],
];
ind.forEach(([k, t, xa, ya, d], i) => {
  const x = M + i * 4.1;
  img(s, `zoom_d${k}.png`, x + 0.55, 1.45, 2.75, 3.12, `Nuage de points du domaine ${k}, ${t}, vue Monde`);
  num(s, x, 1.5, k);
  T(s, t, { x, y: 4.7, w: 3.85, h: 0.4, fontSize: 18, bold: true, color: C.accent1 });
  T(s, [{ text: "X : ", options: { bold: true } }, { text: xa, options: { breakLine: true } }, { text: "Y : ", options: { bold: true } }, { text: ya }],
    { x, y: 5.1, w: 3.85, h: 0.6, fontSize: 14 });
  T(s, d, { x, y: 5.7, w: 3.85, h: 1.1, fontSize: 13, color: C.accent6 });
});
s.addNotes("Les indicateurs généraux sont l'accès basique et sûr, le nombre de personnes sans accès, la mortalité WASH, la population et l'urbanisation, la stabilité politique et leur évolution. Pour chaque domaine, la réunion de lancement demandait un graphique croisant deux variables : ce sont donc trois nuages de points. Pour le consulting, j'ai construit un score d'efficacité de la politique de l'eau qui combine bon accès et faible mortalité ; la mortalité passe par un logarithme car elle varie de 0,01 à 101 pour 100 000 habitants.");

// ================================================================== 7. chiffre clé (graphique natif)
s = slide("CONTENU", "Résultats");
s.addText("776 millions de personnes sans eau de base, dont la moitié en Afrique", { placeholder: "title" });
// image générée par sources/graphique_continents.py (Keynote n'affiche pas les graphiques natifs de pptxgenjs)
img(s, "graphique_continents.png", M, 1.45, 7.9, 5.4, "Personnes sans accès basique par continent en 2000 et 2017, en millions : Afrique 339 puis 387, Asie du Sud-Est 317 puis 148, Pacifique occidental 296 puis 126, Méditerranée orientale 92 puis 76, Amériques 51 puis 23, Europe 26 puis 16");
const stats = [["776 M", "personnes sans accès basique en 2017 (1 121 M en 2000)"], ["+ 48 M", "en Afrique depuis 2000 : le seul continent où le nombre augmente"], ["870 000", "décès liés à l'eau insalubre en 2016"]];
stats.forEach(([v, l], i) => {
  const y = 1.55 + i * 1.75;
  card(s, 8.85, y, 3.85, 1.55);
  T(s, v, { x: 9.1, y: y + 0.15, w: 3.4, h: 0.7, fontSize: 34, bold: true, color: C.accent1, fontFace: "Cambria" });
  T(s, l, { x: 9.1, y: y + 0.85, w: 3.4, h: 0.65, fontSize: 13 });
});
s.addNotes("Premier message, lu dans la vue Monde : l'accès basique est passé de 80 à 90 % de la population mondiale entre 2000 et 2017, et le nombre de personnes sans accès a baissé d'un tiers. Mais l'Afrique est le seul continent où ce nombre augmente, parce que la population y croît plus vite que l'accès. C'est là que se concentre la moitié du besoin.");

// ================================================================== 8-10. vues
const views = [
  ["slide_vue_monde.png", "Vue 1 · Monde : où sont les besoins ?", 2800 - 160, 2020 - 505, [
    "Carte : l'Afrique subsaharienne et l'Océanie concentrent les accès les plus faibles",
    "Barres : où vivent les personnes sans accès, par continent",
    "Courbes 2000-2017 : l'écart ville / campagne se réduit lentement",
    "Barres empilées : la qualité de service (accès sûr) par continent"],
    "Vue mondiale : tous les indicateurs sont agrégés et pondérés par la population. On voit la carte, la répartition par continent, l'évolution et la qualité de service. Un clic sur un pays de la carte ouvre directement sa fiche."],
  ["slide_vue_continent.png", "Vue 2 · Continent : quels pays sont en retard ?", 2800 - 160, 2793 - 509, [
    "Afrique : 62 % d'accès basique contre 90 % dans le monde",
    "Éthiopie, Nigeria et RD Congo comptent 164 M de personnes sans accès",
    "Les 15 pays les moins équipés : qualité de service et écart ville / campagne",
    "Les pays exclus par le filtre de stabilité sont hachurés et signalés"],
    "Vue continentale, ici l'Afrique : les indicateurs sont agrégés pour le continent choisi. On repère les pays les plus en retard en taux (Tchad, Soudan du Sud, Éthiopie) et en nombre de personnes (Éthiopie, Nigeria, RD Congo)."],
  ["slide_vue_pays.png", "Vue 3 · Pays : la fiche de décision", 2800 - 160, 2180 - 650, [
    "Madagascar : 54 % d'accès basique, 12 M de personnes sans accès",
    "Progression lente depuis 2000, campagnes très en retard sur les villes",
    "Comparaison au continent et au monde, population urbaine / rurale",
    "Stabilité politique dans le temps, comparée au seuil du filtre"],
    "Vue nationale, ici Madagascar : la fiche montre l'évolution, la comparaison au continent et au monde, la population urbaine et rurale, et la stabilité dans le temps avec le seuil choisi. Les trois nuages de points placent le pays parmi ses voisins."],
];
views.forEach(([file, title, pw, ph, pts, note]) => {
  s = slide("CONTENU", "Résultats");
  s.addText(title, { placeholder: "title" });
  const maxW = 8.4, maxH = 5.45;
  let w = maxW, h = w * ph / pw;
  if (h > maxH) { h = maxH; w = h * pw / ph; }
  s.addShape(pres.shapes.RECTANGLE, { x: M - 0.02, y: 1.43, w: w + 0.04, h: h + 0.04, fill: { color: C.background2 }, line: { color: "D3E0EB", width: 0.75 } });
  img(s, file, M, 1.45, w, h, title + " : capture du tableau de bord");
  const tx = M + w + 0.4, tw = W - M - tx;
  T(s, pts.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < pts.length - 1 } })), { x: tx, y: 1.5, w: tw, h: 5.2, fontSize: 15, paraSpaceAfter: 10 });
  s.addNotes(note);
});

// ================================================================== 11. pays candidats
s = slide("CONTENU", "Recommandations");
s.addText("Des pays candidats pour chaque domaine (stabilité ≥ -1)", { placeholder: "title" });
const cand = [
  ["1", "Création", "Accès basique le plus faible, 2017", [["Ouganda", "49 % · 21 M sans accès"], ["Tanzanie", "57 % · 24 M"], ["Burkina Faso", "48 % · 10 M"], ["Madagascar", "54 % · 12 M"], ["Mozambique", "56 % · 13 M"]]],
  ["2", "Modernisation", "Accès basique ≥ 80 %, plus grand écart avec l'accès sûr", [["Laos", "82 % basique · 16 % sûr"], ["Népal", "89 % · 27 %"], ["Bhoutan", "97 % · 36 %"], ["Mongolie", "83 % · 24 %"], ["Mexique", "99 % · 43 %"]]],
  ["3", "Consulting", "Pays stables (indice > 0), score d'efficacité le plus faible, 2016", [["Zambie", "score 22 / 100"], ["Kiribati", "36"], ["Comores", "38"], ["Îles Salomon", "39"], ["Namibie", "45"]]],
];
cand.forEach(([k, t, crit, list], i) => {
  const x = M + i * 4.1;
  card(s, x, 1.5, 3.85, 5.25);
  num(s, x + 0.3, 1.72, k);
  T(s, t, { x: x + 0.95, y: 1.75, w: 2.7, h: 0.45, fontSize: 20, bold: true, color: C.accent1, valign: "middle" });
  T(s, crit, { x: x + 0.3, y: 2.4, w: 3.3, h: 0.7, fontSize: 13, color: C.accent6 });
  list.forEach(([p, v], j) => {
    const y = 3.2 + j * 0.68;
    T(s, [{ text: p, options: { bold: true, breakLine: true } }, { text: v, options: { fontSize: 13, color: HEX.accent6 } }], { x: x + 0.3, y, w: 3.3, h: 0.62, fontSize: 15 });
  });
});
s.addNotes("En appliquant un seuil de stabilité de -1, qui exclut 29 pays en 2017, voici les candidats que fait ressortir le tableau de bord. Création : Ouganda et Tanzanie cumulent faible accès et plus de 20 millions de personnes sans eau, majoritairement rurales. Modernisation : Laos, Népal, Bhoutan, Mongolie ont un bon accès basique mais très peu d'eau sûre. Consulting : la Zambie est stable mais combine faible accès et forte mortalité. Ce sont des pistes à approfondir, pas une décision : le seuil de stabilité est réglable par l'utilisateur.");

// ================================================================== 12. accessibilité
s = slide("CONTENU", "Qualité");
s.addText("Accessible et rapide, pour un public non spécialiste", { placeholder: "title" });
const acc = [
  ["Couleur", "Palette Bleu à une seule teinte : la luminosité porte l'information, lisible par les personnes daltoniennes"],
  ["Pas que la couleur", "Traits pleins, tirets ou pointillés ; pays exclus hachurés ; valeurs écrites sur les barres"],
  ["Clavier et lecteur d'écran", "Onglets aux flèches, filtres étiquetés, focus visible, tableau de données sous chaque vue"],
  ["Lisibilité", "Une phrase clé chiffrée par vue, grands indicateurs, repères de lecture sur les nuages de points"],
  ["Contrastes", "Texte au niveau WCAG AA, thème sombre automatique"],
  ["Vitesse", "Modèle pré-agrégé, 3 492 lignes : chaque filtre se recalcule sans délai"],
];
acc.forEach(([t, d], i) => {
  const col = i % 2, row = Math.floor(i / 2);
  const x = M + col * 6.15, y = 1.5 + row * 1.75;
  card(s, x, y, 5.95, 1.55);
  num(s, x + 0.25, y + 0.25, i + 1);
  T(s, t, { x: x + 0.95, y: y + 0.27, w: 4.8, h: 0.45, fontSize: 17, bold: true, color: C.accent1, valign: "middle" });
  T(s, d, { x: x + 0.95, y: y + 0.75, w: 4.8, h: 0.75, fontSize: 14 });
});
s.addNotes("Le tableau de bord est destiné à des décideurs non spécialistes : chaque vue commence par une phrase qui donne le chiffre principal, et la complexité des graphiques reste limitée. Côté accessibilité, l'information n'est jamais portée par la couleur seule, tout est utilisable au clavier, et chaque vue propose ses données sous forme de tableau.");

// ================================================================== 13. démonstration
s = slide("CONTENU", "Démonstration");
s.addText("Démonstration : de la carte du monde à une décision", { placeholder: "title" });
const demo = [
  ["Monde", "Lire la phrase clé et la carte ; montrer l'évolution 2000-2017"],
  ["Filtre stabilité", "Monter le seuil à -1 : 29 pays exclus, hachurés sur la carte"],
  ["Année et zone", "Passer en rural, remonter à 2000 : l'écart ville / campagne"],
  ["Continent", "Afrique : les pays les plus en retard, en taux et en nombre"],
  ["Pays", "Clic sur Madagascar : fiche, évolution, position dans les 3 domaines"],
  ["Domaines", "Revenir aux nuages de points : survol et clic sur un pays candidat"],
];
demo.forEach(([t, d], i) => {
  const y = 1.5 + i * 0.86;
  num(s, M, y + 0.08, i + 1);
  T(s, t, { x: M + 0.75, y: y + 0.1, w: 2.4, h: 0.5, fontSize: 17, bold: true, color: C.accent1, valign: "middle" });
  T(s, d, { x: M + 3.2, y: y + 0.1, w: 4.6, h: 0.6, fontSize: 15, valign: "middle" });
});
card(s, 8.35, 1.6, 4.4, 2.9);
T(s, [{ text: "Filtres", options: { bold: true, color: HEX.accent3, breakLine: true } },
  { text: "Année : temporel", options: { bullet: true, breakLine: true } },
  { text: "Zone total / urbain / rural : qualitatif", options: { bullet: true, breakLine: true } },
  { text: "Stabilité minimale : quantitatif", options: { bullet: true, breakLine: true } },
  { text: "Continent et pays : géographique", options: { bullet: true } }],
  { x: 8.6, y: 1.85, w: 4.0, h: 2.5, fontSize: 15, paraSpaceAfter: 6 });
s.addNotes("Démonstration en direct (dashboard/index.html). 1) Vue Monde : lire la phrase en haut, la carte, survoler un pays. 2) Monter le curseur de stabilité à -1 : 29 pays sont exclus et hachurés, les chiffres se recalculent. 3) Passer la zone en Rural et l'année à 2000 pour montrer l'écart ville-campagne et la progression. 4) Onglet Continent, Afrique : Tchad et Soudan du Sud en taux, Éthiopie et Nigeria en nombre. 5) Cliquer sur Madagascar sur la carte : la fiche pays s'ouvre. 6) Montrer Madagascar dans les trois nuages de points et conclure sur le domaine adapté.");

// ================================================================== 14. conclusion
s = slide("TITRE", "Conclusion");
s.addText("Recommandation : commencer par l'Afrique de l'Est", { placeholder: "title" });
s.addText("Création de services en Ouganda ou en Tanzanie : faible accès, plus de 20 M de personnes sans eau, majoritairement rurales, stabilité acceptable.\nProchaines étapes : valider le seuil de stabilité avec DWFA, compléter avec des données de coût et de présence locale, puis approfondir les 3 pays retenus.", { placeholder: "body" });
s.addNotes("Ma recommandation, au vu des données : le domaine Création en Afrique de l'Est, où le besoin augmente encore. Les autres domaines ont aussi des candidats clairs (Laos pour la modernisation, Zambie pour le consulting) si le bailleur privilégie un autre axe. Prochaines étapes : arrêter le seuil de stabilité avec DWFA, ajouter des données de coût et de présence sur le terrain, et approfondir trois pays. Merci, je suis disponible pour vos questions.");

(async () => {
  await pres.writeFile({ fileName: OUT });
  if (process.env.APPLY_THEME) await require(process.env.APPLY_THEME).applyTheme(OUT, THEME);
  console.log(`${n} diapositives -> ${OUT}`);
})();
