# Protocole Tableau : projet DWFA (accès à l'eau potable)

Ce document décrit pas à pas comment réaliser le projet dans Tableau Desktop / Tableau Public, de l'import des fichiers jusqu'à la publication de l'histoire. Il s'appuie sur les fichiers présents dans ce dossier, qui ont tous été lus et analysés.

---

## 0. Inventaire du dossier

| Rôle | Fichier(s) |
| --- | --- |
| **Énoncé** | `projet_data_viz/Scénario.docx` (contexte, compétences évaluées), `projet_data_viz/mail.docx` (demande du chef de mission), `projet_data_viz/CR+réunion+lancement+DWFA.pdf` (**le cahier des charges technique, c'est la référence**), `Projet Data Visualisation _.docx` (liste de tâches reformulée par l'équipe) |
| **Cours** | `cours_data_viz/Data Viz.pptx` (23 slides, M. Cissé : pourquoi visualiser, définition d'un dashboard, choix du graphique, public, surcharge visuelle, couleurs, mauvais design) ; notebooks Python : pandas (chargement CSV/Excel, encodage), nettoyage (valeurs manquantes, valeurs incohérentes, dates), Plotly (barres groupées/cumulées, nuages de points, séries temporelles, camemberts, heatmaps) ; `cours_data_viz/Data/` = données d'exercice (Superstore, personnes), **sans rapport avec le projet** |
| **Données du projet** | `DAN-P8-donnees/` : 5 CSV + `Dictionnaire de données.xlsx` (le dossier `__MACOSX/` contient des fichiers parasites à ignorer) |
| Déjà produit par l'équipe | `preparation/` (script Python + `referentiel_pays.csv` : ISO3, nom FR, région), `modele/` (schéma en étoile), `dashboard/` (tableau de bord **HTML/Plotly, pas Tableau**), `livrables/` (document de synthèse, présentation PPT, maquettes) |

> ⚠️ Le tableau de bord actuel (`dashboard/index.html`) est en Plotly. Le cahier des charges demande **Tableau ou Power BI** (le mail précise : « une histoire Tableau que tu partageras sur Tableau Public »). Ce protocole sert à produire la version Tableau. Le document de synthèse et la présentation devront ensuite être mis à jour (captures, justification de l'outil).

---

## 1. Ce que demande l'énoncé

### 1.1 Objectif métier
L'ONG DWFA veut un tableau de bord qui permette :
1. d'identifier les pays qui ont des difficultés d'accès à l'eau potable ;
2. d'identifier ceux où concentrer ses efforts, pour **un** de ses 3 domaines d'expertise :
   - **D1 Création** de services d'accès à l'eau ;
   - **D2 Modernisation** de services existants ;
   - **D3 Consulting** auprès des gouvernements.

### 1.2 Livrables
| # | Livrable | Source |
| --- | --- | --- |
| L1 | **Document de synthèse** présentant les indicateurs choisis pour chaque vue (+ blueprint ou mockup basse fidélité, facultatif) | mail |
| L2 | **Histoire Tableau (Story) publiée sur Tableau Public**, contenant les 3 vues (dashboards) | mail + CR |
| L3 | **Présentation PowerPoint** : contexte, prétraitement des données, justification de l'outil retenu | CR + tâches |
| L4 | **Démonstration interactive** du tableau de bord, avec un récit | mail + tâches |

### 1.3 Contraintes fonctionnelles
- **3 vues** : Monde (indicateurs agrégés au niveau mondial), Continent (agrégés pour le continent choisi par l'utilisateur), Pays (indicateurs du pays choisi).
- Toutes les vues reprennent les indicateurs choisis, avec des périmètres différents mais des données cohérentes entre elles.
- Indicateurs généraux suggérés : mortalité due à l'eau insalubre, population / densité, part d'accès à l'eau potable, stabilité politique, évolution dans le temps.
- Indicateurs **à l'échelle nationale** pour chaque domaine :
  - D1 : accès à l'eau potable × taux de population urbaine ;
  - D2 : taux de services « basiques » × taux de services « safely managed » ;
  - D3 : efficacité de la politique publique (mortalité faible + bon accès) × stabilité politique.
- **Filtre modifiable par l'utilisateur pour exclure les pays trop instables.**
- Indicateur qui combine 2 variables ⇒ **nuage de points obligatoire**.
- **Palette « Bleu » obligatoire.**
- Accessibilité ; complexité adaptée au public (chef de mission et bailleur, pas des data analysts).

### 1.4 Attendu technique minimal (CR de réunion)
- [ ] line plot ; [ ] scatter plot ; [ ] grouped barplot ; [ ] stacked ou percent stacked barplot
- [ ] une représentation temporelle ; [ ] une représentation géographique (« option A »)
- [ ] au moins 4 filtres, dont au moins : 1 quantitatif, 1 qualitatif, 1 temporel, 1 géographique
- [ ] au moins un champ calculé d'agrégation (ex. : ×1 000, moyenne)
- [ ] au moins une jointure entre fichiers
- [ ] modèle de données optimisé pour la vitesse d'affichage
- [ ] critères d'accessibilité respectés

### 1.5 Date de rendu et grille de notation
**Ni l'une ni l'autre ne figure dans les fichiers.** Les seuls éléments d'évaluation sont les 3 compétences du `Scénario.docx` :
1. créer un tableau de bord interactif pour rendre la visualisation disponible et accessible ;
2. optimiser une solution de visualisation accessible, adaptée au public et au type de données ;
3. proposer un récit dynamique des résultats pour engager un public.

---

## 2. Ce que le cours apporte

Le cours **ne contient pas de partie spécifique à Tableau** : la slide « Objectifs » annonce « Réaliser un dashboard avec Tableau », mais aucune slide ne traite des LOD, des paramètres ou des stories. Les fonctionnalités Tableau citées plus bas répondent au cahier des charges, pas au cours. Les notions du cours qui servent au projet sont les suivantes :

| Notion du cours | Où elle sert dans le projet |
| --- | --- |
| *What is a dashboard / How to choose* (slides 9 à 12, data-to-viz.com) | Choix du graphique pour chaque indicateur (étape 6) |
| *Define your audience* (slides 13-14) | Graphiques simples, titres sous forme de question, pas de jargon (étapes 6 et 7) |
| *Avoid overloading the graph / Visual overload* (slides 15, 16, 22) | 4 à 6 feuilles maximum par dashboard, étiquettes directes plutôt que légendes |
| *The choice of colors* (slides 17 à 21) | Palette bleue séquentielle, contraste, pas de couleur comme seul codage |
| *Wrong design* (slide 23) | Pas de 3D, pas de camembert à 6 parts ou plus, axes qui commencent à 0 pour les barres |
| Notebook « Valeurs manquantes » (suppression / valeur par défaut / valeur calculée) | Traitement des NULL : safely managed, stabilité 2001, Soudan (étape 3) |
| Notebook « Valeurs incohérentes » (cohérence des valeurs possibles) | Accès basique > 100 %, population à 0, noms de pays divergents (étape 3) |
| Notebook « Chargement CSV » (séparateur, encodage) | Fichiers UTF-8 avec BOM (étape 1) |
| Notebook « Gestion des dates » | Conversion de l'année (entier) en date (étape 4) |
| Notebook « Diagrammes en bâton » (barres cumulées, barres groupées) | Grouped barplot et stacked barplot (étape 6) |
| Notebook « Nuages de points » (3e dimension en taille, 4e en couleur, info-bulles) | Les 3 scatter plots des domaines (étape 6) |
| Notebook « Séries temporelles » (limiter la pollution visuelle, marqueurs) | Line plots (étape 6) |

---

## 3. Diagnostic des données (`DAN-P8-donnees/`)

### 3.1 Description des fichiers

| Fichier | Lignes | Colonnes | Grain | Années |
| --- | --- | --- | --- | --- |
| `BasicAndSafelyManagedDrinkingWaterServices.csv` (OMS) | 10 476 | Year, Country, Granularity (Total/Urban/Rural), *at least basic (%)*, *safely managed (%)* | pays × année × milieu | 2000 à 2017 |
| `Population.csv` (FAO) | 20 914 | Country, Granularity (Total/Urban/Rural/Male/Female), Year, Population (**milliers**) | pays × année × granularité | 2000 à 2018 |
| `PoliticalStability.csv` (FAO / Banque mondiale) | 3 526 | Country, Year, Political_Stability (indice d'environ -3,3 à +2), Granularity (toujours « Total ») | pays × année | 2000 et 2002 à 2018 |
| `MortalityRateAttributedToWater.csv` (OMS) | 549 | Year, Country, Granularity (Total/Male/Female), Mortality rate, WASH deaths | pays × sexe | **2016 uniquement** |
| `RegionCountry.csv` (OMS) | 194 | REGION (DISPLAY), COUNTRY (DISPLAY) | pays | n/a |

Les 5 fichiers sont en UTF-8 **avec BOM**, séparateur virgule. Aucune ligne n'est en double, et aucune clé n'est en double (pays + année + granularité).

### 3.2 Problèmes de qualité constatés

| # | Problème | Ampleur | Traitement proposé |
| --- | --- | --- | --- |
| Q1 | **Noms de pays divergents.** La FAO (population, stabilité) écrit `North Macedonia` et `China, mainland` alors que l'OMS écrit `Republic of North Macedonia` et `China`. Population contient aussi un agrégat `China` (Chine continentale + Hong Kong + Macao + Taïwan) | 2 pays | Calcul de jointure (étape 2.3) |
| Q2 | **Territoires hors référentiel** : Population compte 239 pays/territoires et Stabilité 200, contre 194 dans RegionCountry (Porto Rico, Groenland, Hong Kong, Palestine…) | 46 et 10 entités | Exclus naturellement par la jointure à gauche sur le fichier Eau |
| Q3 | **Soudan** : la FAO ne publie `Sudan` et `South Sudan` qu'à partir de 2012 (`Sudan (former)` de 2000 à 2011), alors que l'OMS les distingue dès 2000 | 2 pays × 12 ans | Accepter la population NULL avant 2012 (ces pays sortent des moyennes pondérées de ces années) et le documenter. Option avancée : répartir `Sudan (former)` dans Tableau Prep |
| Q4 | **Safely managed manquant** | 69 % des lignes ; 1 747 lignes « Total » sur 3 492 ; **96 pays sur 194 n'ont aucune valeur** | Ne pas imputer. Les moyennes pondérées ne portent que sur les pays renseignés. Le nombre de pays couverts est affiché dans l'info-bulle |
| Q5 | **Accès basique manquant** | 1 061 lignes, dont 43 « Total » | Ne pas imputer |
| Q6 | **Accès basique > 100 %** (100,00001) | 7 lignes | Plafonner à 100 (calcul `[Basic % corrigé]`) |
| Q7 | **Stabilité 2001 absente pour tous les pays** ; 14 pays ont une série incomplète | 1 année | Axe continu : la courbe relie directement 2000 et 2002. Signaler dans une note. Interdire 2001 dans le paramètre Année, ou afficher « Stabilité inconnue » |
| Q8 | **Population en milliers** | tout le fichier | Champ calculé ×1 000 (c'est l'exemple d'agrégation cité par l'énoncé) |
| Q9 | **Population = 0** | 253 lignes, surtout des micro-territoires et des « Rural » nuls (Koweït, Monaco, Nauru…), ce qui est plausible | Garder. Tableau renvoie NULL en cas de division par 0 |
| Q10 | **Mortalité : une seule année (2016)** ; `WASH deaths` n'existe que pour la ligne « Total » ; 11 micro-États absents | n/a | Toujours afficher « (2016) » dans les titres. Ne pas soumettre la mortalité au filtre Année |
| Q11 | **Unité du taux de mortalité absente du dictionnaire** | n/a | C'est un taux pour 100 000 habitants selon l'indicateur OMS SDG 3.9.2 (à vérifier sur le site de l'OMS) |
| Q12 | **« Continent » ≠ données** : RegionCountry contient les **6 régions OMS** (Africa, Americas, Eastern Mediterranean, Europe, South-East Asia, Western Pacific), pas des continents | n/a | Utiliser les régions OMS et l'écrire (voir ambiguïté A1) |
| Q13 | **Densité de population impossible** : aucune superficie dans les données | n/a | Voir ambiguïté A2 |
| Q14 | **Géocodage** : des noms OMS comme `Bolivia (Plurinational State of)`, `Iran (Islamic Republic of)`, `Micronesia (Federated States of)` ou `Republic of North Macedonia` risquent d'être « inconnus » pour Tableau | une dizaine | Joindre `preparation/referentiel_pays.csv` (ISO3) et géocoder par code ISO3 |
| Q15 | La colonne `Granularity` porte des sens différents selon le fichier : milieu (eau, population), sexe (mortalité), constante (stabilité) | n/a | La renommer en `Milieu` ou `Sexe` ; masquer celle de la stabilité |

---

## 4. Protocole Tableau pas à pas

> **Mise à jour : nettoyage fait en Python.** Pour la connexion, le modèle et les calculs de base, suivre la **§6.2** à la place des étapes 1 à 4. Pour les axes des nuages, les filtres et le contenu des vues, la **§6.3** (alignée sur le document de synthèse) prime sur l'étape 6. Les étapes 7 à 11 restent valables, avec une 4ᵉ vue (§6.7).

### Étape 1 : Connexion aux données
*Notion du cours : chargement CSV, encodage.*

1. Tableau Desktop (ou Public) → **Se connecter → Fichier texte** → `DAN-P8-donnees/BasicAndSafelyManagedDrinkingWaterServices.csv`.
2. Sur la page **Source de données**, vérifier que la première colonne s'appelle bien `Year` et non `﻿Year` (BOM). Si le caractère parasite apparaît, renommer le champ.
3. Ajouter au même dossier de connexion : `Population.csv`, `PoliticalStability.csv`, `MortalityRateAttributedToWater.csv`, `RegionCountry.csv`, puis `preparation/referentiel_pays.csv` (connexion texte supplémentaire, même source).
4. Ne pas ouvrir les fichiers de `__MACOSX/`.

### Étape 2 : Modèle de données (jointures et relations)
*Attendu : « une jointure sera réalisée » + « modèle optimisé ». Ce modèle combine les deux mécanismes de Tableau : relations dans la couche logique, jointures dans la couche physique.*

```
                 ┌──────────────────────────┐
                 │  Pays  (table logique)   │
                 │  RegionCountry           │
                 │   ⟕ referentiel_pays     │  ← jointure physique sur le nom
                 └──────┬─────────────┬─────┘
          relation Pays │             │ relation Pays
                        ▼             ▼
┌───────────────────────────────┐   ┌──────────────────────────┐
│ Eau_Pop_Stab (table logique)  │   │ Mortalité (table logique)│
│  Water                        │   │  MortalityRate…csv       │
│   ⟕ Population  (pays, année, │   │  (2016, Total/M/F)       │
│                  milieu)      │   └──────────────────────────┘
│   ⟕ PoliticalStab (pays,année)│
└───────────────────────────────┘
```

#### 2.1 Table logique « Pays »
1. Glisser `RegionCountry.csv` sur le canevas. Double-cliquer dessus pour ouvrir la couche physique.
2. Y glisser `referentiel_pays.csv` : **jointure à gauche**, `COUNTRY (DISPLAY)` = `country`.
3. Renommer : `REGION (DISPLAY)` → **Région OMS**, `COUNTRY (DISPLAY)` → **Pays**, `iso3` → **ISO3**, `pays` → **Nom FR**, `continent` → **Région (FR)**.
4. Vérifier : 194 lignes et aucun ISO3 NULL.

#### 2.2 Table logique « Eau_Pop_Stab » (la table de faits principale)
1. Glisser `BasicAndSafely…csv` à côté de Pays. Tableau propose une **relation** : la régler sur `Pays` = `Country`.
2. Double-cliquer sur la table pour ouvrir la couche physique et y glisser `Population.csv` : **jointure à gauche** (Eau à gauche) avec 3 clauses :
   - `Country` = **calcul de jointure** côté Population (étape 2.3) ;
   - `Year` = `Year (Population)` ;
   - `Granularity` = `Granularity (Population)`. Les valeurs Total/Urban/Rural sont identiques ; Male/Female ne trouvent pas de correspondance, ce qui est voulu.
3. Glisser `PoliticalStability.csv` : **jointure à gauche** avec 2 clauses :
   - `Country` = calcul de jointure côté Stabilité ;
   - `Year` = `Year (PoliticalStability)`.
4. **Contrôle** : le nombre de lignes doit rester **10 476** (= 3 492 × 3 milieux). S'il augmente, une clé est en double.
5. Renommer : `Year` → **Année**, `Granularity` → **Milieu**, `Population using at least basic…` → **Basic %**, `Population using safely managed…` → **Géré %**, `Population` → **Population (milliers)**, `Political_Stability` → **Stabilité brute**.
6. Masquer les doublons : `Country (Population)`, `Year (Population)`, `Granularity (Population)`, `Country/Year/Granularity (PoliticalStability)`.

#### 2.3 Calculs de jointure (à saisir dans la boîte de jointure : « Créer un calcul de jointure… »)
Côté **Population** :
```
IF [Country (Population)] = "China, mainland" THEN "China"
ELSEIF [Country (Population)] = "China" THEN "China (agrégat FAO)"
ELSEIF [Country (Population)] = "North Macedonia" THEN "Republic of North Macedonia"
ELSE [Country (Population)]
END
```
Côté **PoliticalStability** :
```
IF [Country (PoliticalStability)] = "China, mainland" THEN "China"
ELSEIF [Country (PoliticalStability)] = "North Macedonia" THEN "Republic of North Macedonia"
ELSE [Country (PoliticalStability)]
END
```
> Choix argumenté : la Chine OMS correspond à la Chine continentale, d'où `China, mainland`. L'agrégat FAO `China` est écarté pour éviter de compter Taïwan, Hong Kong et Macao.

#### 2.4 Table logique « Mortalité »
1. Glisser `MortalityRateAttributedToWater.csv` sur le canevas logique, en **relation avec Pays** : `Pays` = `Country (Mortality…)`.
2. Renommer : `Granularity` → **Sexe**, `Mortality rate attributed…` → **Mortalité WASH**, `WASH deaths` → **Décès WASH**. Masquer `Year`, qui vaut toujours 2016.
3. Ne pas la joindre physiquement à Eau_Pop_Stab : elle n'a qu'une année et 3 lignes par pays, ce qui dupliquerait les lignes.

#### 2.5 Optimisation (*attendu « vitesse d'affichage »*)
1. Passer la connexion en **Extrait** (obligatoire pour Tableau Public de toute façon).
2. Avant l'extraction, **masquer les champs inutilisés** (menu de la source → « Masquer tous les champs inutilisés » une fois les feuilles construites, puis réextraire).
3. Rôles géographiques : `ISO3` → *Pays/Région* ; `Pays` → *Pays/Région*. Vérifier qu'il reste **0 lieu inconnu** en bas à droite de la carte ; sinon, utiliser « Modifier les emplacements ».
4. Dans les filtres rapides, préférer « Toutes les valeurs de la base » à « Uniquement les valeurs pertinentes », qui coûte une requête par filtre.

### Étape 3 : Nettoyage dans Tableau
*Notions du cours : valeurs manquantes (ne pas imputer, ou valeur calculée), valeurs incohérentes.*

| Problème | Action dans Tableau |
| --- | --- |
| Q6 (> 100 %) | Calcul `[Basic % corrigé]` (étape 4) |
| Q4/Q5 (NULL) | Aucune imputation. Les calculs pondérés excluent les NULL du dénominateur. Info-bulle « n pays renseignés » |
| Q7 (stabilité 2001) | `Année` en continu sur les courbes ; note « 2001 non publiée » sous le graphique |
| Q8 (milliers) | Calcul `[Population (hab)]` |
| Q12 (régions) | **Alias** sur `Région OMS` (clic droit → Alias) : Africa → Afrique, Americas → Amériques, Eastern Mediterranean → Méditerranée orientale, Europe → Europe, South-East Asia → Asie du Sud-Est, Western Pacific → Pacifique occidental |
| Q15 | Alias de `Milieu` : Total → Ensemble, Urban → Urbain, Rural → Rural ; alias de `Sexe` : Male → Hommes, Female → Femmes |
| Types | `Année` : nombre entier, dimension ; `Basic %` et `Géré %` : nombre décimal |

Option : faire ces étapes dans **Tableau Prep Builder** (renommage, pivot, répartition du Soudan) si vous voulez un flux de préparation à montrer dans la présentation. Ce n'est pas exigé.

### Étape 4 : Champs calculés
*Attendu : « une agrégation sera réalisée (champ calculé) ». Les calculs pondérés par la population, le ×1 000 et les LOD répondent à cet attendu.*

Format conseillé : les taux en **pourcentage, 1 décimale** (les calculs renvoient des valeurs entre 0 et 1).

#### 4.1 Base (table Eau_Pop_Stab, niveau ligne)
| Nom | Formule | Rôle |
| --- | --- | --- |
| Population (hab) | `[Population (milliers)] * 1000` | ×1 000, demandé par l'énoncé |
| Basic % corrigé | `MIN([Basic %], 100)` | Q6 |
| Année (date) | `MAKEDATE([Année], 1, 1)` | axe temporel continu (notebook « Dates ») |
| Pop totale | `IF [Milieu] = "Total" THEN [Population (hab)] END` | |
| Pop urbaine | `IF [Milieu] = "Urban" THEN [Population (hab)] END` | |
| Hab accès basique | `IF [Milieu] = "Total" THEN [Population (hab)] * [Basic % corrigé] / 100 END` | numérateur pondéré |
| Pop couverte basique | `IF [Milieu] = "Total" AND NOT ISNULL([Basic % corrigé]) THEN [Population (hab)] END` | dénominateur sans les NULL |
| Hab accès géré | `IF [Milieu] = "Total" THEN [Population (hab)] * [Géré %] / 100 END` | |
| Pop couverte géré | `IF [Milieu] = "Total" AND NOT ISNULL([Géré %]) THEN [Population (hab)] END` | |
| Stabilité | `IF [Milieu] = "Total" THEN [Stabilité brute] END` | évite de compter 3 fois la même valeur (jointure × 3 milieux) |
| Stab x pop | `[Stabilité] * [Pop totale]` | |
| Pop couverte stab | `IF NOT ISNULL([Stabilité]) THEN [Pop totale] END` | |

Pour le graphique « par milieu » (Urbain / Rural) :
| Nom | Formule |
| --- | --- |
| Hab basique (milieu) | `[Population (hab)] * [Basic % corrigé] / 100` |
| Pop couverte (milieu) | `IF NOT ISNULL([Basic % corrigé]) THEN [Population (hab)] END` |

Pour l'échelle de service (barres empilées), on prend uniquement les pays où les deux taux sont connus, pour que les trois parts aient le même dénominateur :
| Nom | Formule |
| --- | --- |
| Pop couverte échelle | `IF [Milieu] = "Total" AND NOT ISNULL([Basic % corrigé]) AND NOT ISNULL([Géré %]) THEN [Population (hab)] END` |
| Hab géré (échelle) | `IF NOT ISNULL([Pop couverte échelle]) THEN [Population (hab)] * [Géré %] / 100 END` |
| Hab basique (échelle) | `IF NOT ISNULL([Pop couverte échelle]) THEN [Population (hab)] * [Basic % corrigé] / 100 END` |

#### 4.2 Indicateurs agrégés (valables au niveau Monde, Région et Pays)
| Nom | Formule |
| --- | --- |
| **Accès basique %** | `SUM([Hab accès basique]) / SUM([Pop couverte basique])` |
| **Accès géré %** | `SUM([Hab accès géré]) / SUM([Pop couverte géré])` |
| **Sans accès basique %** | `1 - [Accès basique %]` |
| **Pop sans accès basique** | `SUM([Pop couverte basique]) - SUM([Hab accès basique])` |
| **Taux urbain %** | `SUM([Pop urbaine]) / SUM([Pop totale])` (Tableau renvoie NULL en cas de division par 0, sans erreur) |
| **Accès basique % (milieu)** | `SUM([Hab basique (milieu)]) / SUM([Pop couverte (milieu)])` |
| **Écart basique − géré** | `[Accès basique %] - [Accès géré %]` |
| **Stabilité moyenne** | `AVG([Stabilité])` (moyenne simple des pays) |
| **Stabilité pondérée** | `SUM([Stab x pop]) / SUM([Pop couverte stab])` (pour les agrégats Monde et Région) |
| Part gérée en sécurité | `SUM([Hab géré (échelle)]) / SUM([Pop couverte échelle])` |
| Part basique seulement | `(SUM([Hab basique (échelle)]) - SUM([Hab géré (échelle)])) / SUM([Pop couverte échelle])` |
| Part sous le basique | `1 - SUM([Hab basique (échelle)]) / SUM([Pop couverte échelle])` |
| Nb pays renseignés (géré) | `COUNTD(IF NOT ISNULL([Géré %]) AND [Milieu] = "Total" THEN [Country] END)` |

> Au niveau d'un pays, ces moyennes pondérées redonnent la valeur brute du pays. Au niveau d'une région ou du monde, elles donnent une vraie moyenne pondérée par la population, plus juste qu'une moyenne de pourcentages.

#### 4.3 Référence mondiale fixe (LOD FIXED)
Pour afficher la région choisie face au monde, même quand un filtre Région est actif (un FIXED ignore les filtres de dimension non contextuels) :
| Nom | Formule |
| --- | --- |
| Accès basique monde | `{FIXED [Année] : SUM([Hab accès basique])} / {FIXED [Année] : SUM([Pop couverte basique])}` |
| Accès géré monde | `{FIXED [Année] : SUM([Hab accès géré])} / {FIXED [Année] : SUM([Pop couverte géré])}` |

À utiliser avec `AVG(...)` ou `ATTR(...)` dans la vue.

#### 4.4 Table Mortalité (2016)
| Nom | Formule |
| --- | --- |
| Mortalité totale | `IF [Sexe] = "Total" THEN [Mortalité WASH] END` |
| Pop implicite 2016 | `IF [Sexe] = "Total" THEN [Décès WASH] / [Mortalité WASH] * 100000 END` |
| **Mortalité pondérée (pour 100 000)** | `SUM([Décès WASH]) / SUM([Pop implicite 2016]) * 100000` |
| Mortalité H/F | utiliser directement `[Mortalité WASH]` avec un filtre `Sexe` ≠ Total |

> Astuce : la population implicite est déduite des décès et du taux, dans la même table. On obtient ainsi une mortalité régionale pondérée sans croiser deux tables de faits, ce qui évite les pièges des relations.

#### 4.5 Score d'efficacité de la politique publique (D3)
L'énoncé définit une politique efficace par « mortalité faible + bon accès », sans donner de formule. Celle-ci est un **choix à justifier** dans le document de synthèse :
| Nom | Formule |
| --- | --- |
| Accès basique 2016 | `{FIXED [Pays] : SUM(IF [Année] = 2016 THEN [Hab accès basique] END) / SUM(IF [Année] = 2016 THEN [Pop couverte basique] END)}` |
| Mortalité pays | `{FIXED [Pays] : SUM([Mortalité totale])}` |
| Mortalité max | `{FIXED : MAX([Mortalité totale])}` |
| Score mortalité | `1 - LN(1 + [Mortalité pays]) / LN(1 + [Mortalité max])` |
| **Score efficacité (0-100)** | `100 * (0.5 * [Accès basique 2016] + 0.5 * [Score mortalité])` |
| Stabilité 2016 | `{FIXED [Pays] : AVG(IF [Année] = 2016 THEN [Stabilité] END)}` |

Le logarithme est nécessaire car la mortalité est très asymétrique (de 0,004 à 107 pour 100 000) : sans lui, tous les pays sauf une poignée auraient un score proche de 100. Cette formule est la même que celle du script `preparation_donnees.py`, ce qui assure la cohérence avec le document de synthèse.

#### 4.6 Paramètres et calculs de filtre
| Paramètre | Type / plage | Défaut | Usage |
| --- | --- | --- | --- |
| **p_Seuil stabilité** | Décimal, plage -3,5 à 2, pas de 0,25 | -1,5 | Exclusion des pays instables (demandé explicitement) |
| **p_Année** | Entier, liste 2000 à 2017 (sans 2001 si vous voulez éviter la stabilité vide) | 2017 | Année des vues « instantanées » (carte, nuages de points, barres) |
| **p_Pays** | Chaîne, liste remplie depuis le champ `Pays` | France ou un pays cible | Pays de la vue nationale, mise en évidence dans les nuages |

| Nom | Formule |
| --- | --- |
| Stabilité année choisie | `{FIXED [Pays] : AVG(IF [Année] = [p_Année] THEN [Stabilité] END)}` |
| **Statut stabilité** | `IF ISNULL([Stabilité année choisie]) THEN "Stabilité inconnue" ELSEIF [Stabilité année choisie] >= [p_Seuil stabilité] THEN "Assez stable" ELSE "Trop instable" END` |
| Est année choisie | `[Année] = [p_Année]` |
| Est pays choisi | `[Pays] = [p_Pays]` |
| Mise en évidence pays | `IF [Pays] = [p_Pays] THEN [Pays] ELSE "Autres pays" END` |

### Étape 5 : Filtres (au moins 4 exigés, plus le filtre de stabilité)

| Filtre | Type d'exigence | Mise en œuvre | Appliqué à |
| --- | --- | --- | --- |
| F1 **Exclure les pays instables** | demandé explicitement (et quantitatif) | Contrôle du paramètre `p_Seuil stabilité` (curseur) + filtre `Statut stabilité` = « Assez stable » (case « Stabilité inconnue » laissée au choix de l'utilisateur) | toutes les feuilles des 3 vues (Filtre → Appliquer aux feuilles de calcul → toutes celles qui utilisent cette source) |
| F2 **Population** (quantitatif) | variable quantitative | Glisser `Pop totale` (agrégée en SOMME) en filtre → plage de valeurs, par ex. pour écarter les micro-États | feuilles Monde et Continent |
| F3 **Milieu** (qualitatif) | variable qualitative | Filtre `Milieu` en liste à cases (Urbain / Rural / Ensemble) | barres groupées, barres empilées, courbes de la vue Pays |
| F4 **Années** (temporel) | données temporelles | Filtre `Année (date)` → plage de dates (curseur) sur les courbes, + contrôle `p_Année` sur les vues instantanées (filtre `Est année choisie` = Vrai) | courbes / instantanés |
| F5 **Région OMS** (géographique) | données géographiques | Filtre `Région OMS` en liste déroulante à valeur unique | toutes les feuilles de la vue Continent |
| F6 **Pays** (géographique) | données géographiques | Contrôle `p_Pays` + filtre `Est pays choisi` = Vrai | feuilles de détail de la vue Pays |

### Étape 6 : Feuilles (visualisations)
*Notions du cours : How to choose, Define your audience, Avoid overloading, Choice of colors. Couleurs : palette **Bleu** séquentielle (Tableau : « Bleu » ou « Bleu-Sarcelle »), avec des nuances bien distinctes quand il n'y a que 2 catégories.*

Règle générale : chaque feuille a un **titre en forme de réponse ou de question** (« Où l'accès à l'eau reste-t-il le plus faible ? »), une info-bulle en français avec unités et année, et la **source** en note (« OMS / FAO, 2000-2017 »).

#### Vue 1 : Monde

| Feuille | Graphique | Colonnes | Lignes | Repères (couleur / taille / étiquette / détail) | Filtres | Pourquoi |
| --- | --- | --- | --- | --- | --- | --- |
| **M1 Carte accès** | carte remplie (**géographique**) | Longitude (générée) | Latitude (générée) | Détail : `ISO3`, `Pays` ; **Couleur** : `Sans accès basique %` (Bleu séquentiel, plus foncé = plus de population sans accès) ; info-bulle : accès basique, accès géré, population, stabilité | Est année choisie, F1, F2 | Identifier d'un coup d'œil les pays en difficulté (objectif 1 du mail) |
| **M2 Évolution mondiale** | **line plot** (**temporel**) | `YEAR(Année (date))` continu | `Valeurs de mesure` = Accès basique %, Accès géré % | Couleur : `Noms de mesures` (bleu foncé / bleu clair) ; étiquettes en fin de ligne au lieu d'une légende ; axe 0-100 % | F4 (plage d'années), F1 | « Évolution de ces facteurs dans le temps » ; montre l'écart persistant entre le basique et le « safely managed » |
| **M3 Échelle de service par région** | **percent stacked barplot** | `Valeurs de mesure` = Part gérée en sécurité, Part basique seulement, Part sous le basique | `Région OMS` (triée par Part sous le basique) | Couleur : `Noms de mesures` (3 bleus : foncé = géré, moyen = basique, très clair = sous le basique) ; étiquettes en % | Est année choisie, F1 | Montre ensemble l'accès (D1) et la qualité (D2) par région, en une barre lisible |
| **M4 Urbain vs rural par région** | **grouped barplot** | `Région OMS`, `Milieu` | `Accès basique % (milieu)` | Couleur : `Milieu` (bleu foncé = Urbain, bleu clair = Rural) | Milieu ∈ {Urban, Rural} (F3), Est année choisie, F1 | Prépare la lecture de D1 : l'écart ville/campagne guide le type de projet de création |
| **M5 Chiffres clés** | BAN (texte) | n/a | n/a | Texte : Pop sans accès basique (Md), Accès basique %, Accès géré %, Mortalité pondérée 2016 | Est année choisie, F1 | Donner l'ordre de grandeur au bailleur |

#### Vue 2 : Continent (région OMS sélectionnée)

| Feuille | Graphique | Colonnes | Lignes | Repères | Filtres | Pourquoi |
| --- | --- | --- | --- | --- | --- | --- |
| **C1 Carte de la région** | carte remplie | Longitude | Latitude | Couleur : `Sans accès basique %` ; détail `Pays` | F5, Est année choisie, F1 | Localiser les pays prioritaires de la région ; **action de dashboard** : un clic sur un pays modifie `p_Pays` (action de paramètre) |
| **C2 Région vs monde** | **line plot** | `YEAR(Année (date))` | Axe 1 : `Accès basique %` (région) ; axe 2 : `AVG([Accès basique monde])` → **axe double synchronisé** | Ligne région en bleu foncé pleine, monde en gris-bleu ; étiquettes en fin de ligne | F5, F4, F1 | La région progresse-t-elle plus ou moins vite que le monde ? (LOD FIXED) |
| **C3 D1 Création** | **scatter plot** | `Accès basique %` | `Taux urbain %` | Détail : `Pays` ; **Taille** : `Pop totale` ; **Couleur** : `Pop sans accès basique` (Bleu séquentiel) ; **lignes de référence** = moyenne sur chaque axe (quadrants) ; annotation du quadrant « accès faible & population rurale » | F5, Est année choisie, F1 | Indicateur combinant 2 variables, donc nuage de points (CR). Faible accès + faible urbanisation = création en zone rurale |
| **C4 D2 Modernisation** | **scatter plot** | `Accès basique %` | `Accès géré %` | Détail : `Pays` ; Couleur : `Écart basique − géré` (Bleu) ; ligne de référence Y = moyenne ; info-bulle avec l'écart | F5, Est année choisie, F1 | Pays à fort accès basique mais faible part gérée = gros besoin de modernisation. Afficher en note « n pays sans donnée safely managed » |
| **C5 D3 Consulting** | **scatter plot** | `AVG([Score efficacité])` | `AVG([Stabilité 2016])` | Détail : `Pays` ; Couleur : `Score efficacité` ; **ligne de référence Y = `p_Seuil stabilité`** (rend le seuil d'exclusion visible) ; ligne X = médiane | F5, F1 | Consulting pertinent = administration stable et politique à améliorer (quadrant stable / score moyen ou faible) |
| **C6 Mortalité par sexe** | **grouped barplot** | `Pays` (Top 10 par Mortalité totale, filtre Top N = filtre quantitatif) | `Mortalité WASH` | Couleur : `Sexe` (2 bleus) ; titre « (2016, pour 100 000 hab.) » | Sexe ≠ Total, F5, F1 | Deuxième grouped barplot ; met en évidence les pays où l'eau insalubre tue le plus |

#### Vue 3 : Pays (pays sélectionné)

| Feuille | Graphique | Colonnes | Lignes | Repères | Filtres | Pourquoi |
| --- | --- | --- | --- | --- | --- | --- |
| **P1 Fiche pays** | BAN / tableau texte | n/a | n/a | Population, Taux urbain %, Accès basique %, Accès géré %, Stabilité, Mortalité 2016, Score efficacité, **rang mondial** du score d'efficacité (calcul de table `RANK(AVG([Score efficacité]))` le long de `Pays`, dans une feuille où le pays est sélectionné avec un filtre calculé de table `LOOKUP(ATTR([Pays]), 0) = [p_Pays]` plutôt qu'un filtre de dimension, sinon le rang vaut toujours 1) | F6, Est année choisie | Synthèse pour la décision |
| **P2 Accès dans le temps** | **line plot** | `YEAR(Année (date))` | `Accès basique % (milieu)` | Couleur : `Milieu` (3 bleus) ; étiquettes en fin de ligne | F6, F3, F4 | Évolution nationale ville / campagne |
| **P3 Stabilité dans le temps** | line plot | `YEAR(Année (date))` | `AVG([Stabilité])` | ligne de référence = `p_Seuil stabilité` ; bande sous le seuil grisée | F6, F4 | Le pays est-il durablement au-dessus du seuil ? |
| **P4 Échelle de service par milieu** | **stacked barplot** (100 %) | 3 parts de l'échelle | `Milieu` | Couleur : `Noms de mesures` (3 bleus) | F6, Est année choisie | Où se situe le déficit : basique ou qualité, ville ou campagne ? |
| **P5 Position dans les 3 domaines** | 3 scatter plots (C3, C4, C5 dupliqués **sans** filtre Région) | idem | idem | Couleur : `Mise en évidence pays` (pays choisi en bleu foncé, autres en bleu très clair) ; étiquette du pays choisi | Est année choisie, F1 | Situer le pays face aux autres pour chaque domaine et choisir le domaine d'intervention |

**Vérification de couverture de l'attendu technique** :
line plot (M2, C2, P2, P3) ✔ · scatter (C3, C4, C5, P5) ✔ · grouped barplot (M4, C6) ✔ · stacked / percent stacked (M3, P4) ✔ · temporel (M2, C2, P2, P3) ✔ · géographique (M1, C1) ✔ · 4 filtres de types différents (F2/F1 quantitatif, F3 qualitatif, F4 temporel, F5/F6 géographique) ✔ · champs calculés d'agrégation ✔ · jointures (Eau ⟕ Population ⟕ Stabilité ; RegionCountry ⟕ référentiel) ✔.

### Étape 7 : Dashboards
*Notions du cours : What is a dashboard, Avoid overloading, Define your audience.*

1. **Taille fixe** : 1200 × 800 px (bien adaptée à Tableau Public et à la projection). Vérifier aussi l'aperçu « Téléphone » s'il est généré.
2. Structure commune aux 3 dashboards (même gabarit, pour la cohérence entre vues) :
   - **bandeau titre** (conteneur horizontal) : titre de la vue + sous-titre sous forme de question + boutons de **Navigation** (objet *Navigation* → Monde / Continent / Pays) ;
   - **colonne gauche (≈ 220 px)** : filtres et paramètres (Année, Seuil de stabilité avec une phrase d'aide « Les pays sous ce seuil sont masqués », Région ou Pays, Milieu, Population) ;
   - **zone centrale** : 4 à 6 feuilles au maximum, dans des conteneurs en mosaïque ;
   - **pied de page** : sources (OMS, FAO, Banque mondiale), définitions (« basique » = point d'eau amélioré à moins de 30 minutes ; « géré en sécurité » = sur place, disponible, non contaminé), limites (mortalité 2016 seule, safely managed manquant pour 96 pays).
3. Mise en page proposée :
   - **Monde** : M5 (BAN) en haut ; M1 (carte) en grand au centre ; M2 et M3 en dessous ; M4 à droite.
   - **Continent** : C1 + C2 en haut ; C3, C4, C5 côte à côte (les 3 domaines) ; C6 en bas.
   - **Pays** : P1 en haut ; P2 + P3 ; P4 ; P5 (les 3 petits nuages).
4. **Actions** (Dashboard → Actions) :
   - *Filtre* : un clic sur une région dans M3 filtre M1 et M4 ;
   - *Paramètre* : un clic sur un pays dans C1, C3, C4 ou C5 → `p_Pays` = Pays ;
   - *Aller à la feuille* : un double-clic (ou un bouton) ouvre le dashboard Pays ;
   - *Mise en surbrillance* : survol d'un pays → surbrillance dans les 3 nuages.
5. Appliquer F1 (stabilité) « à toutes les feuilles utilisant cette source » pour que l'exclusion soit cohérente partout.

### Étape 8 : Histoire (Story) Tableau
*Attendu du mail : « une histoire Tableau partagée sur Tableau Public ». Compétence 3 : « récit dynamique ».*

1. Nouvelle histoire, taille identique aux dashboards (1200 × 800 + hauteur de la barre de navigation).
2. Points d'histoire (légendes = phrases de récit, pas seulement des titres) :
   1. *« 2 milliards de personnes sans eau gérée en sécurité : où ? »* → Dashboard Monde.
   2. *« L'Afrique concentre l'essentiel du déficit d'accès basique »* → Dashboard Continent (filtre Africa enregistré dans le point).
   3. *« Trois domaines, trois profils de pays »* → Dashboard Continent avec les nuages mis en avant (annotations sur 2 ou 3 pays cibles).
   4. *« Zoom sur [pays recommandé] : quel domaine financer ? »* → Dashboard Pays.
   5. (facultatif) *« Recommandation »* : texte et chiffres clés.
3. Garder exactement **3 dashboards distincts**. Les points supplémentaires réutilisent ces dashboards avec un autre état de filtre (voir ambiguïté A3).
4. **Annotations** (clic droit sur un repère → Annoter) sur les pays cités dans le récit.
5. Avant de valider chaque point, régler les filtres dans l'état voulu, puis « Mettre à jour » le point.

### Étape 9 : Accessibilité (attendu explicite)
*Notion du cours : The choice of colors, Visual overload.*

- [ ] Palette bleue **séquentielle** pour les mesures ; 2 ou 3 nuances seulement pour les catégories, avec un contraste suffisant (vérifier le bleu le plus clair sur fond blanc ; ajouter une bordure grise aux repères très clairs).
- [ ] **Jamais la couleur seule** : étiquettes directes, valeurs dans les info-bulles, formes différentes si besoin.
- [ ] Polices ≥ 10 pt pour les axes, ≥ 12 pt pour les filtres, ≥ 16 pt pour les titres ; une seule famille de police (Tableau Book/Regular).
- [ ] Titres et légendes en français, unités et année toujours visibles (« %, 2017 », « pour 100 000 hab., 2016 »).
- [ ] Pas de camembert, pas de 3D ; barres partant de 0.
- [ ] Ordre logique des objets (haut-gauche vers bas-droite), utile pour la navigation au clavier sur Tableau Public.
- [ ] Ajouter une feuille « Données » (tableau texte) ou laisser l'option « Télécharger » ouverte : alternative textuelle pour les lecteurs d'écran.
- [ ] Simuler le daltonisme sur une capture (Coblis, ou un outil de Chrome DevTools).

### Étape 10 : Publication et livrables
1. **Fichier → Enregistrer sur Tableau Public** (compte gratuit ; les données sont publiques : rien de sensible ici). Vérifier l'option « Afficher les feuilles sous forme d'onglets » (désactivée si l'on veut ne montrer que l'histoire).
2. Copier le **lien public** dans la présentation et le document de synthèse.
3. Mettre à jour `livrables/Document_de_synthese_DWFA.docx` : indicateurs par vue (étape 6), formules (étape 4), captures Tableau.
4. Mettre à jour `livrables/Presentation_DWFA.pptx` : contexte de la mission, étapes de prétraitement (section 3 de ce document : noms de pays, ×1 000, Soudan, NULL, plafond à 100 %, alias des régions), **justification de Tableau** (Story native, Tableau Public gratuit et partageable, outil déjà utilisé par les prédécesseurs, LOD et actions de paramètres), scénario de démonstration.
5. Mettre à jour le `README.md` pour pointer vers le classeur `.twbx` et le lien Tableau Public.

### Étape 11 : Vérifications finales avant rendu

**Données**
- [ ] Eau_Pop_Stab = 10 476 lignes ; Pays = 194 ; Mortalité = 549.
- [ ] 0 lieu inconnu sur les cartes.
- [ ] Contrôle croisé d'un pays (ex. Afghanistan 2000 : accès basique 27,8 %, population 20,78 M, stabilité -2,44) : les valeurs dans Tableau doivent correspondre au CSV.
- [ ] Contrôle d'un agrégat : accès basique mondial 2017 cohérent avec le chiffre OMS/JMP (≈ 90 %) ; accès géré ≈ 70 % (sur les pays renseignés uniquement).
- [ ] Chine et Macédoine du Nord présentes avec population et stabilité.

**Interactivité**
- [ ] Changer `p_Seuil stabilité` modifie bien les 3 vues, la ligne de référence de C5 et celle de P3.
- [ ] Changer `p_Année` met à jour cartes, barres, nuages et BAN ; 2001 affiche « Stabilité inconnue » sans erreur.
- [ ] Le filtre Région n'affecte pas la courbe « monde » de C2 (LOD FIXED).
- [ ] Les actions (clic sur un pays → vue Pays) fonctionnent **après publication** sur Tableau Public.
- [ ] Temps d'affichage < 2 s par changement de filtre (sinon, masquer les champs inutilisés et réextraire).

**Conformité au cahier des charges** (cocher la section 1.4) + **palette bleue partout** + 3 dashboards + story + accessibilité.

**Livrables** : lien Tableau Public, `.twbx` dans le dépôt, document de synthèse à jour, PPT à jour, démo répétée (5 minutes : Monde → Afrique → nuages → pays recommandé → recommandation).

---

## 5. Points ambigus ou non vérifiés

| # | Point | Ce qu'il faut décider ou vérifier |
| --- | --- | --- |
| A1 | **« Vue continentale »** alors que les données ne contiennent que les **6 régions OMS** (Amériques sans distinction Nord/Sud, Égypte en Méditerranée orientale, etc.) | Utiliser les régions OMS en le disant clairement (« continent = région OMS »), ou créer un **groupe** Tableau vers les vrais continents (saisie manuelle de 194 pays). Je recommande la première option, déjà retenue dans `referentiel_pays.csv` |
| A2 | **Densité de population** citée comme indicateur, mais **aucune superficie** n'est fournie | Ajouter la superficie (Banque mondiale, indicateur AG.LND.TOTL.K2) par une jointure supplémentaire, ou remplacer par population / taux urbain et le justifier. Le CR précise que ces indicateurs ne sont « que des exemples » |
| A3 | **Nombre de vues** : « très exactement 3 » (liste de tâches de l'équipe) contre « au moins 3 vues » (CR) | Livrer 3 dashboards. Les points d'histoire supplémentaires ne sont que des états de ces 3 dashboards |
| A4 | **Formule de « l'efficacité de la politique gouvernementale »** non définie | Score 50/50 accès + mortalité (log) proposé (étape 4.5), à justifier dans la synthèse |
| A5 | **« Option A »** pour la géographie et les filtres : l'option B n'est décrite nulle part | Faire l'option A (carte + filtre géographique), qui est couverte |
| A6 | **Seuil d'instabilité** : aucune valeur imposée | Paramètre modifiable, -1,5 par défaut (l'indice Banque mondiale va d'environ -2,5 à +2,5 ; en dessous de -1,5, on parle de forte instabilité). À justifier |
| A7 | **Mortalité : une seule année (2016)** alors que l'énoncé veut l'évolution temporelle | Évolution montrée pour l'accès et la stabilité ; la mortalité reste un instantané 2016 (le dire). Une série plus longue peut être récupérée sur le site de l'OMS si besoin |
| A8 | **Unité du taux de mortalité** absente du dictionnaire | À confirmer sur le site de l'OMS (SDG 3.9.2 : décès pour 100 000 habitants) |
| A9 | **Date de rendu et barème** | **Absents de tous les fichiers** : à demander à l'enseignant |
| A10 | **Le livrable actuel est en HTML/Plotly**, pas en Tableau/Power BI | À remplacer (ou compléter) par le classeur Tableau ; adapter la « justification de l'outil » dans la présentation |
| A11 | Le cours ne contient **aucune partie pratique sur Tableau** | Les fonctionnalités utilisées (relations, LOD, paramètres, actions, story) viennent du cahier des charges et de la documentation Tableau, pas du cours |
| A12 | Fichiers en double dans le dépôt (`Dictionnaire de données.xlsx`, `CR…pdf`, `Scénario.docx` apparaissent deux fois, sans doute une différence de normalisation Unicode des accents) | Sans impact sur le projet ; à nettoyer dans Git si vous le souhaitez |
| A13 | Version de Tableau inconnue | Les fonctionnalités utilisées existent depuis Tableau 2020.2 (relations), 2019.2 (actions de paramètre) et 2018.3 (objet Navigation). Avec une version plus ancienne, remplacer les relations par des jointures |

---

## 6. Revue complète du dépôt : existant, écarts et reste à faire (mise à jour)

### 6.1 Ce qui existe déjà (et ce qui est réutilisable)
| Élément | État | Réutilisation dans Tableau |
| --- | --- | --- |
| `preparation/preparation_donnees.py` | Pipeline pandas complet : alias de noms, ×1 000, Soudan scindé avant 2012, stabilité 2001 interpolée, grille 194 pays × 2000-2017, score d'efficacité | **Oui** : il produit le modèle à charger |
| `modele/dim_pays.csv` (194) · `fait_pays_annee.csv` (3 492) · `fait_mortalite_2016.csv` (183) | Schéma en étoile, clé `iso3` | **Source Tableau recommandée** (cohérente avec le document de synthèse et le PPT, qui décrivent ce modèle) |
| `livrables/Document_de_synthese_DWFA.docx` | Indicateurs, 3 vues, filtres, palette, accessibilité : **la spécification de référence** | Le classeur Tableau doit le reproduire ; seules l'accessibilité et les captures sont à réécrire |
| `livrables/Presentation_DWFA.pptx` (14 diapositives + notes) | La diapo 5 justifie **Plotly** ; les diapos 8-10 et 13 renvoient au HTML | Diapos 5, 8-10, 12 et 13 à refaire pour Tableau |
| `dashboard/index.html` | Tableau de bord Plotly : **ne remplit pas le livrable « histoire Tableau sur Tableau Public »** | Sert de maquette visuelle (couleurs, mise en page, chiffres de contrôle) |
| `livrables/captures/blueprint_vue_*.png` | Maquettes des 3 vues | Gabarit des dashboards Tableau |

### 6.2 Source de données (décision : nettoyage en Python)
**Décision** : tout le nettoyage est fait en Python. Tableau ne fait que charger le modèle, le joindre et l'agréger. Les étapes 1 à 3 de la §4 (CSV bruts, calculs de jointure, nettoyage dans Tableau) **ne s'appliquent plus**.

Régénérer le modèle : `python preparation/preparation_donnees.py`. Le script se charge de :
- l'harmonisation des noms FAO/OMS et la suppression de l'agrégat « China » ;
- la population ×1 000 ;
- la répartition du Soudan (avant 2012) et de la **Serbie-et-Monténégro (avant 2006)** selon les parts de la première année séparée ;
- les **taux bornés à [0, 100]** ;
- la stabilité 2001 interpolée ;
- les jointures à gauche sur les 194 pays OMS ;
- le score d'efficacité.

Les 4 fichiers à charger dans Tableau (Texte → `modele/`) :
| Fichier | Grain | Colonnes |
| --- | --- | --- |
| `dim_pays.csv` (194) | pays | `iso3` (rôle géographique : Pays/Région → ISO 3166-1 alpha-3), `pays` (nom français, à afficher), `continent` (région OMS en français), `region_oms`, `country` |
| `fait_zone.csv` (10 476) | pays × année × zone | `zone` (Total / Urbain / Rural), `population`, `basic`, `safe`, `hab_basic`, `pop_couv_basic`, `hab_safe`, `pop_couv_safe`, `pop_sans_basic`, `part_sur`, `part_basique_seul`, `part_sans_basique` |
| `fait_pays_annee.csv` (3 492) | pays × année | `pop`, `pop_urb`, `pop_rur`, `urban_rate`, `stability`, `basic_T/U/R`, `safe_T/U/R`, `gap_basic_safe` |
| `fait_mortalite_2016.csv` (183) | pays (2016) | `mortality`, `mortality_m`, `mortality_f`, `deaths`, `efficiency_score`, `pop`, `stability` |

Modèle Tableau :
- **Jointure** (couche physique, attendu du compte rendu) : `fait_zone` ⟕ `fait_pays_annee` sur `iso3` = `iso3` **et** `year` = `year`. Le résultat compte 10 476 lignes. Pour chaque ligne zone, il apporte la stabilité et l'urbanisation de l'année.
- **Relations** (couche logique) : cette table jointe ↔ `dim_pays` (`iso3`) ; `fait_mortalite_2016` ↔ `dim_pays` (`iso3`).
- **Extrait** (.hyper) avant publication : Tableau Public l'impose de toute façon.
- Attention : les colonnes de `fait_pays_annee` sont répétées 3 fois, une par zone. Avec elles, filtrer `zone = "Total"` ou utiliser `AVG` / `MIN` plutôt que `SUM`, ou bien prendre `population` de `fait_zone`.

Champs calculés (exigence « agrégation par champ calculé ») :
```
Accès basique %        = SUM([hab_basic]) / SUM([pop_couv_basic])
Accès sûr %            = SUM([hab_safe])  / SUM([pop_couv_safe])
Personnes sans accès   = SUM([pop_sans_basic])
Taux urbain %          = SUM(IF [zone]="Urbain" THEN [population] END) / SUM(IF [zone]="Total" THEN [population] END)
Zone choisie ?         = [zone] = [p_Zone]                   // filtre qualitatif (paramètre Total / Urbain / Rural)
Année choisie ?        = [year] = [p_Année]
Exclu (instable)       = [stability] < [p_Seuil stabilité]   // les NULL (stabilité inconnue) ne sont pas exclus
Accès basique % monde  = {FIXED [year],[zone] : SUM([hab_basic])} / {FIXED [year],[zone] : SUM([pop_couv_basic])}
Accès basique % cont.  = {FIXED [continent],[year],[zone] : SUM([hab_basic])} / {FIXED [continent],[year],[zone] : SUM([pop_couv_basic])}
Mortalité pondérée     = SUM([deaths]) / SUM([pop (fait_mortalite)]) * 100000
```

**Mise en garde sur les LOD et le filtre de stabilité.** Par défaut, un FIXED est calculé *avant* les filtres de dimension. Si le monde doit lui aussi exclure les pays instables, il faut **ajouter le filtre `Exclu` au contexte** (clic droit → Ajouter au contexte).

### 6.3 Écarts entre les sections 4 et 6 et le document de synthèse (c'est le document de synthèse qui fait foi)
| Point | Protocole §4 | Document de synthèse (à suivre) |
| --- | --- | --- |
| D1 Création | X = accès, Y = taux urbain | **X = taux d'urbanisation, Y = accès basique, taille = personnes sans accès** |
| D2 Modernisation | couleur = écart | X = basique, Y = sûr, **diagonale y = x** (ligne de référence ou courbe de tendance fixe) |
| D3 Consulting | X = score, Y = stabilité | **X = stabilité 2016, Y = score d'efficacité** |
| Filtres | Population (quantitatif), Milieu… | **Année (curseur), Zone T/U/R (qualitatif), Stabilité minimale −3,5 à +1,5 (quantitatif), Continent, Pays (géographique)** |
| Vue Monde | M1-M5 | Carte, barres « sans accès » par continent, courbes T/U/R + sûr, échelle de service en barres 100 % empilées, urbain/rural en barres groupées, **3 nuages de points** |
| Vue Continent | C1-C6 | Carte zoomée, courbe du continent, **Top 8** « sans accès », échelle de service des **15 pays les moins équipés**, urbain/rural de ces 15 pays, 3 nuages |
| Vue Pays | P1-P5 | Courbes T/U/R + sûr, carte du continent avec le pays encadré, **barres groupées pays / continent / monde**, **population urbaine/rurale en barres empilées**, stabilité avec ligne de seuil, 3 nuages avec le pays mis en évidence |

### 6.4 Notions de cours supplémentaires (slides et notebooks relus)
- **Choisir le graphique selon l'intention** (data-to-viz : comparaison, relation, distribution, composition) : barres pour comparer, nuage de points pour relier 2 variables, barres 100 % pour la composition, lignes pour le temps.
- **Mettre en évidence** (slide 19) : autres pays en gris ou bleu très clair, pays sélectionné ou candidats en bleu foncé, avec une étiquette.
- **Même couleur pour un même concept** sur tous les graphiques (slide 20) : Urbain, Rural, Total et Sûr gardent la même nuance partout.
- **L'œil lit mal les angles** : pas de camembert. **Ne jamais couper l'axe Y** des barres (slide 21).
- **Moins d'information** : agréger, Top N, **étiquettes directes plutôt que légende** (slide 22).
- **Temps à l'horizontale, en lignes**, pas en barres empilées sur le temps (slide 23). La population urbaine/rurale de la vue Pays peut rester en aires ou barres empilées, mais en série continue.
- **Gabarit du dashboard Superstore** (slide 5) : bandeau de chiffres clés en haut, carte, filtres et légendes à droite, série temporelle en bas.
- **Notebooks** :
  - barres horizontales quand les libellés sont longs (noms de pays) ;
  - Top 10 ;
  - nuage de points avec taille = 3ᵉ variable, couleur = 4ᵉ, info-bulles riches ;
  - fond blanc et peu de quadrillage ;
  - titre sous forme de question ;
  - libellés traduits ;
  - valeurs manquantes affichées « n.d. » plutôt qu'imputées (méthode « supprimer, défaut ou précalcul » vue en cours, justifiée dans le PPT).

### 6.5 Chiffres de contrôle (le classeur Tableau doit retrouver les chiffres du PPT)
- Monde 2017 : **776 M** de personnes sans accès basique (1 121 M en 2000) ; accès basique ≈ **90 %** (80 % en 2000).
- Afrique : **62 %** d'accès basique, + 48 M de personnes sans accès depuis 2000 ; Éthiopie + Nigeria + RD Congo = **164 M**.
- Madagascar 2017 : **54 %**, 12 M de personnes sans accès.
- Seuil de stabilité −1 : **29 pays exclus** en 2017.
- Décès WASH 2016 ≈ **870 000** ; Zambie : score d'efficacité **22/100**.

### 6.6 Ambiguïtés tranchées
- **A14** : nettoyage → **Python** (§6.2).
- **A3** : nombre de vues → **au moins 3**. On fait 3 vues + 1 vue « Domaines » (§6.7), ce qui couvre aussi le cas où « exactement 3 » serait attendu, puisque les 3 vues obligatoires restent complètes.
- 2000 : le monde compte **1 122 M** de personnes sans accès basique (1 121 M dans le PPT avant l'ajout de la Serbie et du Monténégro 2000-2005). Corriger la slide 7.

### 6.7 Quatrième vue : « Domaines » (comparer et décider)
Question : *« Pour chaque domaine, quels pays financer ? »*
- **3 nuages de points en grand** (D1, D2, D3, mêmes axes que §6.3) sur tous les pays non exclus, dans l'année choisie :
  - candidats en bleu foncé avec étiquette, autres pays en bleu très clair (notion « mettre en évidence ») ;
  - lignes de référence : moyenne pour D1 ; diagonale pour D2 ; seuil de stabilité et médiane du score pour D3.
- **3 Top 5 en barres horizontales**, un par domaine, avec les règles de la slide 11 du PPT :
  - Création : accès basique le plus faible (Total), trié par personnes sans accès ;
  - Modernisation : accès basique ≥ 80 % et plus grand `gap_basic_safe` ;
  - Consulting : stabilité > 0 et score d'efficacité le plus faible (2016).
- Paramètre `p_Domaine` (Création / Modernisation / Consulting) pour les afficher un par un si l'écran est trop chargé (feuilles masquées par un calcul `[p_Domaine] = "…"`, ou conteneurs à afficher/masquer).
- Action de paramètre : un clic sur un pays ouvre la vue Pays.
- Résultats attendus avec un seuil de −1 : Ouganda, Tanzanie (Création) ; Laos, Népal (Modernisation) ; Zambie 22/100 (Consulting).

Story (sur les 4 dashboards) :
1. Monde, 776 M ;
2. Continent Afrique, 62 % ;
3. Domaines, avec un candidat par domaine ;
4. Pays Madagascar ou Ouganda ;
5. Recommandation (Domaines, filtré sur Création, avec annotation).
