# CKOALA — Noyau de Classification (Phase 1) 

## Aperçu du Projet

Le projet CKOALA implémente un **système de classification de connaissances** basé sur une **typologie hiérarchique** chargée et interprétée à partir de fichiers XML. La **Phase 1** couvre le développement du noyau fonctionnel (classes métier, logique d'héritage, vérification de cohérence et mécanisme de classification).

| Statut de l'Intégration Continue (CI) | Couverture de Code (JaCoCo) |
| :--- | :--- | 
| ![Pipeline Status](https://gitlab.univ-lille.fr/nabil.hani.etu/ppo_projet/badges/master/pipeline.svg) | ![Coverage Report](https://gitlab.univ-lille.fr/nabil.hani.etu/ppo_projet/badges/master/coverage.svg) |

-----

## Structure et Fichiers

| Répertoire | Contenu | Description |
| :--- | :--- | :--- |
| **`src/`** | Classes Java | Noyau fonctionnel (`Typologie`, `Categorie`, `Domaine...`). |
| **`tests/`** | Classes Java | Programmes `main` de test pour la validation locale et CI/CD. |
| **`data/`** | Fichiers XML | Données de typologie du professeur (`arbres.xml`, `nuages.xml`). |
| **`out/`** | Classes compilées | Dossier de construction et de compilation (généré par l'exécution locale / CI). |

-----

## Exécution et Compilation Locales

Pour compiler le projet et exécuter les tests sans passer par le pipeline GitLab (CI/CD), suivez ces étapes :

### 1\. Compilation

```bash
# Crée les dossiers de compilation
mkdir -p out/classes out/test-classes

# 1. Compilation des sources (src/)
find src -name "*.java" > sources.txt
javac -d out/classes @sources.txt

# 2. Création de la liste des fichiers de tests
find tests -name "*.java" > tests.txt 

# 3. Compilation des tests (tests/)
javac -classpath out/classes:lib/junit-platform-console-standalone.jar -d out/test-classes @tests.txt
```

### 2\. Exécution des Tests Fonctionnels

```bash
# Définit le CLASSPATH pour l'exécution
CP=out/classes:out/test-classes

# 1. Tests d'isolation (Vérification de la cohérence d'héritage en mémoire)
java -cp $CP tests.HerediteInclusionTest

# 2. Tests de chargement XML et de classification
java -cp $CP tests.ChargementXmlTest
java -cp $CP tests.ClassificationArbresTest
java -cp $CP tests.ClassificationNuagesTest
java -cp $CP tests.LireXML data/arbres.xml
```

-----

## Rapport de Couverture (JaCoCo)

Le pipeline CI/CD génère un rapport JaCoCo au format XML (via le job `build-report`).

### 1\. Localiser le Rapport

Le fichier de rapport est généré dans le répertoire de construction : `out/jacoco/jacoco.xml`.

  * **Sur GitLab (CI) :** Le fichier est un **artefact** du job `build-report`. Vous devez télécharger l'archive des artefacts pour le récupérer.
  * **En Local :** Si vous avez `git pull` le fichier `jacoco.xml`, cela signifie que le fichier **a été ajouté à votre dépôt Git** (bien que cela soit généralement une mauvaise pratique pour les fichiers générés). Si ce fichier est présent, vous pouvez l'analyser.

### 2\. Formule d'Extraction du Pourcentage

Le job **`extract-coverage`** de la CI utilise la formule XPath suivante pour calculer le pourcentage d'instructions couvertes (et mettre à jour le badge) :

```bash
XML_FILE=out/jacoco/jacoco.xml

# Calcule le pourcentage couvert (arrondi 2 décimales)
COVERAGE=$(xmllint --xpath 'string(//counter[@type="INSTRUCTION"]/@missed * 100 div (//counter[@type="INSTRUCTION"]/@missed + //counter[@type="INSTRUCTION"]/@covered))' $XML_FILE | awk '{printf "%.2f", 100 - $1}')

echo "Coverage (instructions) : $COVERAGE %"
# Exemple de sortie attendue : Coverage (instructions) : 92.37 %
```

-----

Le noyau fonctionnel est développé en respectant strictement les critères de la grille d'évaluation PPO :

  * **Encapsulation & Immutabilité :** Utilisation de champs `private final` et retour de vues **non modifiables** pour les collections (`Collections.unmodifiable*` / `Map.copyOf`).
  * **Conception Objet (OCP) :** Le mot-clé `instanceof` est évité dans la logique métier. La vérification du type de domaine est gérée par `try/catch(ClassCastException)` au niveau de l'interface `DomaineValeur`, forçant le polymorphisme.
  * **Lisibilité :** Les `Magic Strings` (ex: `"TOP"`) sont remplacés par des constantes `static final`.
  * **Validation des Invariants :** Les constructeurs vérifient les conditions de base (ex: pas de domaines vides, bornes valides).
  * **`toString()` Cohérent :** Les méthodes `toString()` délèguent à une méthode métier (`decrire()`) si applicable, pour une meilleure cohérence d'affichage.