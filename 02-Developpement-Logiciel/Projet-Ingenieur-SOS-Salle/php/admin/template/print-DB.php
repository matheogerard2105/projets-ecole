<?php

require_once '../auth.php';
requireAdmin();
require_once '../functions.php';

$pdo = connectAdminDatabase();

$icsEntries = getAllICSNotSuperGroupe($pdo);
$n_ics = (int) count($icsEntries);

if ($_SERVER['REQUEST_METHOD'] === 'POST'){
    $formation = (string) (isset($_POST['download_formation']) ? $_POST['download_formation'] : '');
    $set_groupe = (string) (isset($_POST['set_groupe']) ? $_POST['set_groupe'] : '');
    $pdo = connectAdminDatabase();
    if (!empty($formation)){
        print_r("Le nouveau fichier est stocké ici :");
        print_r(downloads_ics($pdo, $formation));
    }

    if (!empty($set_groupe)){
        print_r("Le groupe " . $set_groupe . " est reclassé en supergroupe");
        print_r(updateSuperGroupe($pdo, $set_groupe, true));
    }

    
}

?>

<!DOCTYPE html>
<html lang='fr'>
    <head>
        <meta charset='utf-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1'>
        <title>Print Database</title>
        <link rel='stylesheet' href='../../../css/style-tab.css'>
    </head>
    <body>
        <h1>Print Database</h1>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Formation</th>
                    <th>URL ICS</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($icsEntries as $entry): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($entry['id']); ?></td>
                        <td><?php echo htmlspecialchars($entry['formation']); ?></td>
                        <td>
                            <?php echo htmlspecialchars($entry['url_ics']); ?>
                            <form name="download-form-<?= htmlspecialchars($entry['formation']) ?>" action="" method="post">
                                <input type="hidden" name="download_formation" value="<?= htmlspecialchars($entry['formation']) ?>">
                                <button type="submit" name="btn-down-<?= htmlspecialchars($entry['formation']) ?>">Télécharger</button>
                            </form>
                            <form name="set-super-groupe-form-<?= htmlspecialchars($entry['formation']) ?>" action="" method="post">
                                <input type="hidden" name="set_groupe" value="<?= htmlspecialchars($entry['formation']) ?>">
                                <button type="submit" name="btn-set-groupe-<?= htmlspecialchars($entry['formation']) ?>">Supergroupe</button>
                            </form>
                        </td>
                        <td>
                            <button id >
                        </td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
        <br><a href='../../../index.html'>Retour à l'accueil</a>
        <script>
            const nb_btn = <?= $n_ics ?>;
            const ics_entries = <?= json_encode($icsEntries) ?>;
            
            function downloadsBtn(btn, formation) {
                btn.onclick = () => {
                    window.location.href = 'download_ics.php?formation=' + encodeURIComponent(formation);
                }
            }

            for (let i=0; i<nb_btn; i++){
                let formation = ics_entries[i].formation;
                let btn_down = document.getElementById("btn-" + formation);
                downloadsBtn(btn_down, formation);
            }
        </script>
    </body>
</html>