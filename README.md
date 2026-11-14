# Projets d'école – Polytech Lille

**Mathéo GERARD** – Élève ingénieur en 5e année à Polytech Lille, spécialité
**Informatique, Statistique et Intelligence Artificielle (ISIA)**.

Ce dépôt rassemble les principaux projets que j'ai réalisés au cours de mon cycle ingénieur
(2024 – 2027), le plus souvent en binôme ou en équipe, ainsi que mes projets personnels.
Il accompagne mes deux CV :

- **CV « Stage Data Scientist / Data Analyst »** → voir la partie [01 – Data Science & IA](#01--data-science--ia)
- **CV « Stage Développeur logiciel »** → voir la partie [02 – Développement logiciel](#02--développement-logiciel)
  et les [projets personnels](#projets-personnels)

---

## Organisation du dépôt

```
projets-ecole/
├── projet-ecole/                      → projets réalisés à Polytech Lille
│   ├── 01-Data-Science-IA/            → projets mis en avant dans le CV Data
│   ├── 02-Developpement-Logiciel/     → projets mis en avant dans le CV Développeur
│   ├── 03-Mathematiques-Appliquees/   → modélisation, probabilités, optimisation
│   └── 04-Gestion-de-Projet/          → projet commun aux deux CV (PSI)
└── projet-perso/                      → projets personnels, réalisés en dehors des cours
```

Le dépôt est séparé en deux : les **projets d'école** d'un côté, les **projets personnels**
de l'autre.

### Pourquoi ce classement ?

J'ai rangé les projets d'école selon **la manière dont ils sont présentés dans mes CV**, pour qu'un
recruteur qui lit l'un ou l'autre trouve tout de suite le code correspondant :

1. **Data Science & IA** regroupe les projets de la rubrique « Projets » du CV Data
   (Data Engineering, Data Visualisation, Machine Learning) ainsi que les projets qui illustrent
   les compétences de ce CV : Python (pandas, Plotly), R, SQL, statistiques et pipelines ETL.
2. **Développement logiciel** regroupe les projets du CV Développeur (Projet Ingénieur,
   Architecture des SI, POO / Test et Maintenance, Algorithmique et Graphes en C) et les projets
   qui illustrent ses compétences : Java, C, PHP, JavaScript, HTML/CSS, SQL, architecture 3-tiers,
   tests et Git.
3. **Mathématiques appliquées** rassemble les projets de modélisation et d'optimisation. Ils
   n'apparaissent pas en tant que tels dans les CV, mais ils correspondent à la compétence
   « Statistiques, probabilités, optimisation » du CV Data et à la formation ISIA.
4. **Gestion de projet** contient le projet PSI. Il figure sur **les deux CV**, c'est pourquoi
   il a sa propre catégorie.

Le dossier **projet-perso** regroupe les applications et les jeux que je développe en dehors des
cours. Ils correspondent à la rubrique « Projets personnels » du CV Développeur.

Dans chaque catégorie, les projets sont classés **du plus représentatif au moins représentatif**
du poste visé.

---

## 01 – Data Science & IA

| Projet | Description | Technologies |
|---|---|---|
| [Data Engineering – pipeline d'une compagnie aérienne](projet-ecole/01-Data-Science-IA/Data-Engineering-Pipeline-Aerien) | Pipeline ELT quotidien en architecture médaillon (bronze / silver / gold) sur un mois de données : chargements idempotents (insert, upsert, soft delete), modèle en étoile, contrôles d'intégrité. Voir `DOCUMENTATION.md`. | Python, SQL, DuckDB |
| [Data Visualisation – accès à l'eau potable (cas DWFA)](projet-ecole/01-Data-Science-IA/Data-Visualisation-DWFA) | Tableau de bord interactif (vues Monde / Continent / Pays) pour aider une ONG à choisir où investir, à partir des données OMS/UNICEF, FAO et Banque mondiale 2000-2017. Préparation des données, schéma en étoile, document de synthèse et présentation. | Python, pandas, Plotly, Tableau |
| [Machine Learning – joueurs de football](projet-ecole/01-Data-Science-IA/Machine-Learning-Football) | Classification de joueurs de football, avec comparaison de plusieurs méthodes d'apprentissage. | Python, Jupyter, scikit-learn |
| [Modélisation avancée – salaires des professeurs](projet-ecole/01-Data-Science-IA/Modelisation-Avancee-Regression) | Rapport : prétraitement, analyse exploratoire, régression linéaire (MCO), diagnostic des résidus, VIF, sélection de variables et modélisation prédictive. | R, statistiques |
| [Big Data – PageRank sur Wikispeedia](projet-ecole/01-Data-Science-IA/Big-Data-PageRank) | Implémentation de PageRank (méthode de la puissance) et de PageRank personnalisé sur le graphe de navigation Wikispeedia (Stanford SNAP), étude du facteur d'amortissement. | Python, NumPy |
| [Analyse de données web – chômage en France (2023)](projet-ecole/01-Data-Science-IA/Analyse-Donnees-Chomage-Web) | Site d'analyse d'un fichier de l'enquête Emploi (≈ 350 000 lignes) : lecture du CSV en JavaScript et graphiques interactifs. | JavaScript, Plotly, Bootstrap |

## 02 – Développement logiciel

| Projet | Description | Technologies |
|---|---|---|
| [Projet Ingénieur – SOS Salle](projet-ecole/02-Developpement-Logiciel/Projet-Ingenieur-SOS-Salle) | Refonte de SOS Salle, l'application web qui affiche les emplois du temps et la disponibilité des salles de l'école : import de calendriers ICS, espace d'administration, script d'installation. | PHP, PostgreSQL, HTML/CSS, Bash |
| [Architecture des SI – Solidar'Tool](projet-ecole/02-Developpement-Logiciel/ASI-Location-Outils-3-tiers) | Plateforme de prêt / location d'outils entre particuliers en architecture 3-tiers (client, EJB, web). Rapport et diagramme UML inclus. | Java EE, EJB, WildFly, PostgreSQL, Ant |
| [POO – CKOALA, classification d'espèces](projet-ecole/02-Developpement-Logiciel/POO-CKOALA-Classification) | Application Java de classification d'observations naturelles à partir d'une typologie hiérarchique chargée depuis des fichiers XML. `phase1-noyau` : noyau fonctionnel, tests, intégration continue GitLab (Checkstyle, JaCoCo). `phase2-ihm` : interface graphique développée sur le noyau fonctionnel d'un autre binôme. | Java, Swing, JUnit, GitLab CI |
| [Test et Maintenance](projet-ecole/02-Developpement-Logiciel/Test-Maintenance-JUnit) | Écriture de tests unitaires et mesure de la couverture de code sur plusieurs classes Java. | Java, JUnit 5, JaCoCo |
| [Algorithmique et Graphes (C)](projet-ecole/02-Developpement-Logiciel/Algorithmique-Graphes-C) | Implémentation d'algorithmes sur les graphes en C, à partir de fichiers au format DIMACS (graphes jusqu'à 2 500 sommets et 7 500 arêtes). Voir `Readme.txt` pour la compilation. | C |
| [Web – jeu Flood-It](projet-ecole/02-Developpement-Logiciel/Web-Jeu-FloodIt) | Jeu de grille Flood-It dans le navigateur, avec taille de grille et nombre de couleurs paramétrables. | JavaScript, HTML, CSS |

## 03 – Mathématiques appliquées

| Projet | Description | Technologies |
|---|---|---|
| [MAM – modélisation d'une endémie](projet-ecole/03-Mathematiques-Appliquees/MAM-Modelisation-Endemie) | Comparaison d'un modèle stochastique (chaîne de Markov) et d'un modèle déterministe pour l'évolution d'une endémie, avec interface graphique. Le dossier `Bonus` contient deux simulations interactives en JavaScript. | Python, NumPy, Matplotlib, Tkinter, JavaScript |
| [Recherche opérationnelle – optimisation de production](projet-ecole/03-Mathematiques-Appliquees/Recherche-Operationnelle-Lindo) | Modélisation d'un problème de production en programme linéaire, résolution du primal et du dual avec Lindo, analyse de l'impact de variations de prix (coûts réduits). | Programmation linéaire, Lindo |

## 04 – Gestion de projet

| Projet | Description |
|---|---|
| [PSI – projet d'entreprise simulé](projet-ecole/04-Gestion-de-Projet/PSI-Projet-Entreprise-Simule) | Projet mené en équipe de 6 dans les conditions d'une entreprise : dossier d'organisation, spécifications, réunions, plannings, comptes rendus et respect des délais. |

---

## Projets personnels

Ces projets ont chacun leur propre dépôt. Dans le dossier `projet-perso`, ils apparaissent comme
des liens (sous-modules Git) vers ces dépôts : un clic ouvre le dépôt complet, toujours à jour.
Seule la version Unity de Turn It est stockée directement ici.

| Projet | Description | Technologies |
|---|---|---|
| [Paddock 26](https://github.com/matheogerard2105/paddock26) | Simulateur de course automobile en 3D inspiré du règlement 2026, jouable dans le navigateur et sur Android : moteur physique indépendant du rendu (adhérence, usure des pneus, météo, stratégies des IA), 24 circuits, mode carrière, replays et export vidéo. | JavaScript, three.js, Web Audio, Node.js, Android (WebView) |
| [Nofon](https://github.com/matheogerard2105/nofon) | Application Android pour reprendre le contrôle de son temps d'écran : objectifs avec mises (argent simulé), seul ou en groupe, badges, fil d'activité entre amis. Toute la logique sensible est côté serveur. | Kotlin, Jetpack Compose, MVVM, Hilt, Room, Supabase (PostgreSQL, Row Level Security) |
| [Turn It](https://github.com/matheogerard2105/turn-it) | Jeu d'alignement de pions sur une grille qui pivote : IA minimax sur 13 niveaux, multijoueur en ligne validé par le serveur, parties classées avec système elo, application installable (PWA) et Android. | JavaScript, Node.js, WebSocket, SQLite |
| [Quadrille](https://github.com/matheogerard2105/quadrille) | Entraînement illimité aux casse-tête logiques Zip, Queens, Tango et Patches, avec des grilles générées automatiquement (solution unique, trois niveaux) et des défis entre amis par code, avec classement en direct. | JavaScript, Capacitor (Android, iOS), Supabase |
| [Relevé Terrain QR](https://github.com/matheogerard2105/releve-terrain-qr) | Application mobile créée pour le travail de mon père, technicien : inventaire des équipements d'un chantier par scan de QR code, suivi de l'avancement par étage et par local, import et export Excel. Fonctionne hors connexion. | JavaScript, IndexedDB, jsQR, SheetJS |
| [Turn It – version Unity](projet-perso/turn-it-unity) | Première version mobile de Turn It, développée sous Unity. La logique du jeu se trouve dans `Assets/GameManager.cs`. | Unity, C# |

---

## Remarques

- La plupart des projets d'école ont été réalisés en binôme ou en équipe. Les noms des autres
  membres figurent dans les rapports et dans les fichiers README des projets.
- Les supports de cours fournis par les enseignants ne sont pas inclus. Certains énoncés sont
  conservés lorsqu'ils aident à comprendre le contexte du projet.
