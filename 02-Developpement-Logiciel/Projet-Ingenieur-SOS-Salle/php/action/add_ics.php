<?php

require_once __DIR__ . '/../admin/auth.php';
requireAdmin();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    require_once __DIR__ . '/../admin/functions.php';

    $url_ics = $_POST['url_ics'] ?? '';
    $formation = $_POST['formation'] ?? '';

    $pdo = connectAdminDatabase();

    if (!empty($url_ics) && !empty($formation)) {
        echo json_encode
        (['status' => 'success'
        , 'message' => 'ICS URL and formation received successfully.'
        , 'url_ics' => $url_ics, 'formation' => $formation]);
        insertGroupeLienADE($pdo, $formation, $url_ics);
    } else {
        echo json_encode(['status' => 'error', 'message' => 'Missing required fields.']);
    }
} else {
    echo json_encode(['status' => 'error', 'message' => 'Invalid request method.']);
}

echo "<br><a href='../../index.html'>Retour à l'accueil</a>";
echo "<br><a href='../template/add_ics.html'>Retour au formulaire</a>";