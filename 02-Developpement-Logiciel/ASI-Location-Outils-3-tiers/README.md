# ATTENTION le build.xml doit contenir le chemin du dosssier sur votre session, votre nom d'utilisateur et le nom de votre base (jeedbmom)

# 1. Lancer le serveur wildfly en entrant cette commande là ou se trouve votre dossier wildfly-38.0.1.Final :
wildfly-38.0.1.Final/bin/standalone.sh

# 2. Allez dans le dossier dans lequel vous avez importez le git et mettre les commandes suivantes : 
ant clean
ant deployAll
ant run-client

# 3. Connectez-vous à l'interface web :
http://localhost:8080/solidar_tool/Controleur

# --------- Commandes supplémentaires---------

# Commande pour ajouter tous les fichiers au git sauf build.xml
git add . ":(exclude)build.xml"
 
# Connexion à la base de donnée SQL :
psql jeedbmgerard1 ou psql jeedbnhani en fonction du build xml
mot de passe : postgres

# --------- Requêtes SQL pour vérifier les ajouts ---------

# Vérifier les particuliers ajoutés (3 utilisateurs créés)
SELECT * FROM particulier;

# Vérifier les équipements proposés (3 équipements ajoutés)
SELECT * FROM equipement;

# Vérifier les catégories d'équipements
SELECT * FROM categorie;

# Vérifier les emprunts créés (2 demandes d'emprunt)
SELECT * FROM emprunt;