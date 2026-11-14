<?php

require_once '../auth.php';
requireAdmin();
require_once '../functions.php';

// Vérifie si le paramètre "formation" est présent dans l'URL
if (isset($_GET['formation'])) {
    $formation = $_GET['formation'];
    $pdo = connectAdminDatabase();
    
    downloads_ics($pdo, $formation);
    
} else {
    echo "Erreur : Aucune formation spécifiée.";
}
?>

<!DOCTYPE HTML>
<html lang="fr">
    <head>
    </head>
    <body>
        <h1>Downloads ICS</h1>
        <a href="print-DB.php">Retour au tableau</a>
    </body>
</html>