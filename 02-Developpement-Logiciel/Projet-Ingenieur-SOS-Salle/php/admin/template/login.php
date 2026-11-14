<?php

require_once '../auth.php';

if (isAdmin()) {
    header('Location: ' . ADMIN_HOME_URL);
    exit;
}

$erreur = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!checkCsrf()) {
        $erreur = "Session expirée, veuillez réessayer.";
    } elseif (loginAdmin($_POST['login'] ?? '', $_POST['password'] ?? '')) {
        header('Location: ' . ADMIN_HOME_URL);
        exit;
    } else {
        $erreur = "Identifiant ou mot de passe incorrect.";
    }
}

?>
<!DOCTYPE html>
<html lang='fr'>
    <head>
        <meta charset='utf-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1'>
        <title>Connexion administrateur</title>
        <link rel='stylesheet' href='../../../css/style-admin.css'>
    </head>
    <body>
        <main class='login'>
            <h1>Administration SOS Salle</h1>

            <?php if ($erreur): ?>
                <p class='flash flash-erreur' role='alert'><?= htmlspecialchars($erreur) ?></p>
            <?php endif; ?>

            <form method='POST' class='carte'>
                <input type='hidden' name='csrf' value='<?= csrfToken() ?>'>

                <label for='login'>Identifiant</label>
                <input type='text' id='login' name='login' autocomplete='username' required autofocus>

                <label for='password'>Mot de passe</label>
                <input type='password' id='password' name='password' autocomplete='current-password' required>

                <button type='submit' class='btn btn-principal'>Se connecter</button>
            </form>

            <a href='../../../index.html'>Retour à l'accueil</a>
        </main>
    </body>
</html>
