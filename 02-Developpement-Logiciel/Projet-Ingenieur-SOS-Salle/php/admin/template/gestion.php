<?php

require_once '../auth.php';
requireAdmin();
require_once '../functions.php';

$pdo = connectAdminDatabase();

/**************************************

    Traitement des formulaires (POST -> redirection -> GET)

***************************************/

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';
    $id = (int) ($_POST['id'] ?? 0);
    $nom = trim($_POST['nom'] ?? '');
    $url = trim($_POST['url_ics'] ?? '');
    $erreur = null;
    $succes = null;

    if (!checkCsrf()) {
        $erreur = "Session expirée, veuillez réessayer.";
    } else {
        try {
            switch ($action) {
                case 'ajouter':
                    $erreur = ajouterCorrespondance($pdo, $nom, $url);
                    $succes = "Formation « $nom » ajoutée.";
                    break;
                case 'modifier':
                    $erreur = modifierCorrespondance($pdo, $id, $nom, $url);
                    $succes = "Formation « $nom » modifiée.";
                    break;
                case 'desactiver':
                case 'activer':
                    $actif = $action === 'activer';
                    if (!setFormationActive($pdo, $id, $actif)) {
                        $erreur = "Formation introuvable.";
                    }
                    $succes = $actif ? "Formation réactivée." : "Formation désactivée.";
                    break;
                default:
                    $erreur = "Action inconnue.";
            }
        } catch (PDOException $e) {
            error_log($e->getMessage());
            $erreur = "Erreur de base de données, l'opération n'a pas été effectuée.";
        }
    }

    $_SESSION['flash'] = $erreur
        ? ['type' => 'erreur', 'message' => $erreur]
        : ['type' => 'succes', 'message' => $succes];

    // En cas d'erreur sur un formulaire, on le réaffiche avec la saisie
    if ($erreur && in_array($action, ['ajouter', 'modifier'], true)) {
        $_SESSION['saisie'] = ['action' => $action, 'id' => $id, 'nom' => $nom, 'url_ics' => $url];
    }

    $retour = ($erreur && $action === 'modifier') ? "?modifier=$id" : '';
    header('Location: gestion.php' . $retour);
    exit;
}

/**************************************

    Affichage

***************************************/

$flash = $_SESSION['flash'] ?? null;
$saisie = $_SESSION['saisie'] ?? null;
unset($_SESSION['flash'], $_SESSION['saisie']);

$correspondances = getAllCorrespondances($pdo);
$formations = array_filter($correspondances, fn($g) => !$g['is_super_group']);
$superGroupes = array_filter($correspondances, fn($g) => $g['is_super_group']);

$enModification = isset($_GET['modifier']) ? getCorrespondance($pdo, (int) $_GET['modifier']) : null;
if ($enModification && $enModification['is_super_group']) {
    $enModification = null;
}

$saisieAjout = ($saisie['action'] ?? '') === 'ajouter' ? $saisie : null;
$saisieModif = ($saisie['action'] ?? '') === 'modifier' ? $saisie : null;

function e($valeur): string {
    return htmlspecialchars((string) $valeur, ENT_QUOTES);
}

// Les URL ICS ne doivent pas être exposées en clair (NF7) : on n'affiche que le domaine
function resumeUrl(string $url): string {
    $hote = parse_url($url, PHP_URL_HOST) ?: '';
    return $hote . '/…';
}

?>
<!DOCTYPE html>
<html lang='fr'>
    <head>
        <meta charset='utf-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1'>
        <title>Gestion des flux ICS</title>
        <link rel='stylesheet' href='../../../css/style-admin.css'>
    </head>
    <body>
        <header class='entete'>
            <h1>Gestion des flux ICS</h1>
            <nav>
                <a href='print-DB.php'>Téléchargements ICS</a>
                <a href='../../../index.html'>Accueil</a>
                <form method='POST' action='logout.php'>
                    <input type='hidden' name='csrf' value='<?= csrfToken() ?>'>
                    <button type='submit' class='btn btn-lien'>Se déconnecter</button>
                </form>
            </nav>
        </header>

        <main>
            <?php if (isAuthDesactivee()): ?>
                <p class='flash flash-erreur' role='note'>Authentification désactivée (mode développement, config.php).</p>
            <?php endif; ?>

            <?php if ($flash): ?>
                <p class='flash flash-<?= e($flash['type']) ?>' role='status'><?= e($flash['message']) ?></p>
            <?php endif; ?>

            <?php if ($enModification): ?>
                <?php
                    $valNom = $saisieModif['nom'] ?? $enModification['nom'];
                    $valUrl = $saisieModif['url_ics'] ?? ($enModification['liens'][0]['url'] ?? '');
                ?>
                <section class='carte'>
                    <h2>Modifier « <?= e($enModification['nom']) ?> »</h2>
                    <form method='POST' class='formulaire'>
                        <input type='hidden' name='csrf' value='<?= csrfToken() ?>'>
                        <input type='hidden' name='action' value='modifier'>
                        <input type='hidden' name='id' value='<?= e($enModification['id']) ?>'>

                        <label for='modif-nom'>Formation</label>
                        <input type='text' id='modif-nom' name='nom' value='<?= e($valNom) ?>'
                               pattern='[A-Za-z0-9_\-]{1,63}' maxlength='63' required>

                        <label for='modif-url'>URL ICS</label>
                        <input type='url' id='modif-url' name='url_ics' value='<?= e($valUrl) ?>' maxlength='1024' required>

                        <div class='actions'>
                            <button type='submit' class='btn btn-principal'>Enregistrer</button>
                            <a href='gestion.php' class='btn'>Annuler</a>
                        </div>
                    </form>
                </section>
            <?php endif; ?>

            <section class='carte'>
                <h2>Ajouter une formation</h2>
                <form method='POST' class='formulaire'>
                    <input type='hidden' name='csrf' value='<?= csrfToken() ?>'>
                    <input type='hidden' name='action' value='ajouter'>

                    <label for='ajout-nom'>Formation</label>
                    <input type='text' id='ajout-nom' name='nom' value='<?= e($saisieAjout['nom'] ?? '') ?>'
                           placeholder='ex. IS4' pattern='[A-Za-z0-9_\-]{1,63}' maxlength='63' required>

                    <label for='ajout-url'>URL ICS</label>
                    <input type='url' id='ajout-url' name='url_ics' value='<?= e($saisieAjout['url_ics'] ?? '') ?>'
                           placeholder='https://planning-2026.univ-lille.fr/…' maxlength='1024' required>

                    <div class='actions'>
                        <button type='submit' class='btn btn-principal'>Ajouter</button>
                    </div>
                </form>
            </section>

            <section class='carte'>
                <h2>Formations (<?= count($formations) ?>)</h2>
                <table class='tableau'>
                    <thead>
                        <tr>
                            <th scope='col'>Formation</th>
                            <th scope='col'>Flux ICS</th>
                            <th scope='col'>État</th>
                            <th scope='col'>Modifiée le</th>
                            <th scope='col'>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($formations as $g): ?>
                            <tr class='<?= $g['actif'] ? '' : 'inactif' ?>'>
                                <td data-label='Formation'><strong><?= e($g['nom']) ?></strong></td>
                                <td data-label='Flux ICS'>
                                    <?php if ($g['liens']): ?>
                                        <code><?= e(resumeUrl($g['liens'][0]['url'])) ?></code>
                                    <?php else: ?>
                                        <em>Aucun flux</em>
                                    <?php endif; ?>
                                </td>
                                <td data-label='État'>
                                    <span class='badge badge-<?= $g['actif'] ? 'actif' : 'inactif' ?>'>
                                        <?= $g['actif'] ? 'Active' : 'Désactivée' ?>
                                    </span>
                                </td>
                                <td data-label='Modifiée le'><?= e(date('d/m/Y H:i', strtotime($g['date_modif']))) ?></td>
                                <td data-label='Actions' class='actions'>
                                    <a href='?modifier=<?= e($g['id']) ?>' class='btn'>Modifier</a>
                                    <form method='POST'>
                                        <input type='hidden' name='csrf' value='<?= csrfToken() ?>'>
                                        <input type='hidden' name='id' value='<?= e($g['id']) ?>'>
                                        <?php if ($g['actif']): ?>
                                            <button type='submit' name='action' value='desactiver' class='btn btn-danger'
                                                    onclick="return confirm('Désactiver cette formation ? Elle ne sera plus proposée aux utilisateurs.')">
                                                Désactiver
                                            </button>
                                        <?php else: ?>
                                            <button type='submit' name='action' value='activer' class='btn'>Réactiver</button>
                                        <?php endif; ?>
                                    </form>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </section>

            <?php if ($superGroupes): ?>
                <section class='carte'>
                    <h2>Super-groupes (<?= count($superGroupes) ?>)</h2>
                    <p class='aide'>Un super-groupe regroupe les flux de plusieurs formations.</p>
                    <table class='tableau'>
                        <thead>
                            <tr>
                                <th scope='col'>Super-groupe</th>
                                <th scope='col'>Nombre de flux</th>
                                <th scope='col'>État</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($superGroupes as $g): ?>
                                <tr class='<?= $g['actif'] ? '' : 'inactif' ?>'>
                                    <td data-label='Super-groupe'><strong><?= e($g['nom']) ?></strong></td>
                                    <td data-label='Nombre de flux'><?= count($g['liens']) ?></td>
                                    <td data-label='État'>
                                        <span class='badge badge-<?= $g['actif'] ? 'actif' : 'inactif' ?>'>
                                            <?= $g['actif'] ? 'Actif' : 'Désactivé' ?>
                                        </span>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </section>
            <?php endif; ?>
        </main>
    </body>
</html>
