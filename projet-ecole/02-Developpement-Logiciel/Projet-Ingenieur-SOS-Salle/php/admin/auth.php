<?php

/**************************************

    Authentification administrateur (NF7)
    Session PHP + identifiants définis dans config.php

***************************************/

require_once __DIR__ . '/config.php';

if (session_status() === PHP_SESSION_NONE) {
    session_start([
        'cookie_httponly' => true,
        'cookie_samesite' => 'Strict',
    ]);
}

const ADMIN_LOGIN_URL = '/php/admin/template/login.php';
const ADMIN_HOME_URL  = '/php/admin/template/gestion.php';

// Option de développement ($admin_auth_desactivee dans config.php).
// Ignorée si la requête ne vient pas de la machine locale, pour ne jamais
// ouvrir l'administration par erreur sur un serveur.
function isAuthDesactivee(): bool {
    global $admin_auth_desactivee;
    $local = in_array($_SERVER['REMOTE_ADDR'] ?? '', ['127.0.0.1', '::1'], true);
    return !empty($admin_auth_desactivee) && $local;
}

function isAdmin(): bool {
    return isAuthDesactivee() || !empty($_SESSION['admin']);
}

// À appeler en haut de chaque page d'administration
function requireAdmin(): void {
    if (!isAdmin()) {
        header('Location: ' . ADMIN_LOGIN_URL);
        exit;
    }
}

function loginAdmin(string $login, string $password): bool {
    global $admin_login, $admin_password_hash;

    if (empty($admin_login) || empty($admin_password_hash)) {
        return false; // Aucun compte configuré : accès refusé
    }
    if (!hash_equals($admin_login, $login) || !password_verify($password, $admin_password_hash)) {
        return false;
    }

    session_regenerate_id(true);
    $_SESSION['admin'] = true;
    return true;
}

function logoutAdmin(): void {
    $_SESSION = [];
    session_destroy();
}

/**************************************

    Protection CSRF des formulaires

***************************************/

function csrfToken(): string {
    if (empty($_SESSION['csrf'])) {
        $_SESSION['csrf'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf'];
}

function checkCsrf(): bool {
    return isset($_POST['csrf'], $_SESSION['csrf']) && hash_equals($_SESSION['csrf'], $_POST['csrf']);
}
