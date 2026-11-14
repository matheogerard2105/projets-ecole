<?php

require_once '../auth.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && checkCsrf()) {
    logoutAdmin();
}

header('Location: ' . ADMIN_LOGIN_URL);
exit;
