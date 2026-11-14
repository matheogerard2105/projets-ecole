# DWFA : étude d'accès à l'eau potable

Tableau de bord pour aider l'ONG Drinking Water For All à choisir dans quel pays et dans quel domaine d'expertise (création, modernisation, consulting) investir un nouveau financement.

## Livrables

| Livrable | Fichier |
| --- | --- |
| Tableau de bord interactif (3 vues : Monde, Continent, Pays) | `dashboard/index.html` (ouvrir dans un navigateur ; connexion internet requise pour Plotly et les polices) |
| Document de synthèse : indicateurs par vue + maquette (blueprint) | `livrables/Document_de_synthese_DWFA.docx` |
| Support de présentation, avec notes de l'orateur et scénario de démonstration | `livrables/Presentation_DWFA.pptx` |
| Script de préparation des données | `preparation/preparation_donnees.py` |
| Modèle de données (schéma en étoile, chargeable dans Tableau / Power BI) | `modele/*.csv` |

## Organisation

```
DAN-P8-donnees/        données brutes fournies (OMS, FAO, Banque mondiale) + dictionnaire
preparation/           script de préparation + référentiel pays (ISO3, nom français, continent)
modele/                dim_pays.csv, fait_pays_annee.csv, fait_mortalite_2016.csv
dashboard/             index.html + data.js (généré) + geo.js (contours des pays)
livrables/             document de synthèse, présentation, captures et leurs scripts (sources/)
projet_data_viz/       énoncé : scénario, mail, compte rendu de la réunion de lancement
```

## Regénérer

```bash
pip install -r requirements.txt
python preparation/preparation_donnees.py        # modele/*.csv et dashboard/data.js
python livrables/sources/blueprint.py            # maquettes des 3 vues
python livrables/sources/graphique_continents.py # graphique de la présentation
python livrables/sources/document_synthese.py    # document de synthèse
npm install pptxgenjs && node livrables/sources/presentation.js   # présentation
```

Les captures du tableau de bord (`livrables/captures/vue_*.png`) ont été faites dans Chrome à 1400 px de large.

## Choix de préparation

- Les noms de pays FAO sont alignés sur ceux de l'OMS (`North Macedonia`, `China, mainland`).
- La FAO ne distingue Soudan et Soudan du Sud qu'à partir de 2012 : avant, « Sudan (former) » est réparti selon les parts de 2012.
- La stabilité politique 2001, absente de la source, est interpolée linéairement. Les autres valeurs manquantes ne sont pas imputées.
- Les agrégats mondiaux et continentaux sont des moyennes pondérées par la population.
- Le score d'efficacité (domaine 3, 2016) se calcule ainsi : 50 % accès basique normalisé + 50 % (100 - mortalité WASH normalisée sur échelle log).
