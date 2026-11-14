<?php

// Copier ce fichier en config.php (non versionné) et adapter les valeurs.

$host = 'localhost';
$port = '5432';
# à changer selon l'utilisateur
$db   = 'sos-salle-<user>';

$user = 'app_writer';
$pass = 'postgres';

// Compte administrateur (accès aux pages php/admin)
// Générer le hash avec : php -r "echo password_hash('mot_de_passe', PASSWORD_DEFAULT), PHP_EOL;"
$admin_login         = 'admin';
$admin_password_hash = '';

// Développement uniquement : désactive la connexion admin (ignoré hors localhost)
$admin_auth_desactivee = false;
