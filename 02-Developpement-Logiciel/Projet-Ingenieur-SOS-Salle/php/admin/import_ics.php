<?php

require '../../vendor/autoload.php';
require_once 'functions.php';

use Sabre\VObject\Reader;

$pdo = connectUserDatabase("app_reader", "postgres");
$formation = "IS3"; // Remplacez par la formation souhaitée


function downloads_ics($pdo, $formation) {
    // Récupération de l'URL ICS depuis la base de données
    $icsUrl = getLienADE($pdo, $formation);
    $uploadDir = __DIR__ . '/../uploads';
    $localFilePath = $uploadDir . '/' . 'EDT' . '_' . $formation . '.ics';

    // 2. Téléchargement uniquement si le fichier est absent
    if (!file_exists($localFilePath)) {
        $ch = curl_init($icsUrl);
        $fp = fopen($localFilePath, 'wb');

        curl_setopt_array($ch, [
            CURLOPT_FILE           => $fp,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_TIMEOUT        => 20,
            CURLOPT_USERAGENT      => 'PHP-ICS-Parser/1.0',
        ]);

        $success = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $curlError = curl_error($ch);

        fclose($fp);
        curl_close($ch);

        if (!$success || $httpCode !== 200) {
            // Nettoyage du fichier incomplet en cas d'erreur
            if (file_exists($localFilePath)) {
                unlink($localFilePath);
            }
            throw new RuntimeException("Échec du téléchargement (HTTP {$httpCode}) : {$curlError}");
        }
    }

    return $localFilePath;
}

function parseICS($localFilePath) {
    // Lecture et parsing depuis la copie locale
    $vcalendar = \Sabre\VObject\Reader::read(fopen($localFilePath, 'r'));
    $eventsTable = [];

    if (isset($vcalendar->VEVENT)) {
        foreach ($vcalendar->VEVENT as $event) {
            $uid = (string) ($event->UID ?? '');
            $titre = (string) ($event->SUMMARY ?? 'Sans titre');
            $salle = (string) ($event->LOCATION ?? 'Non renseignée');
            
            $debut = isset($event->DTSTART) ? $event->DTSTART->getDateTime()->format('Y-m-d H:i:s') : null;
            $fin = isset($event->DTEND) ? $event->DTEND->getDateTime()->format('Y-m-d H:i:s') : null;

            // --- NOUVELLE LOGIQUE PAR ÉLIMINATION ---
            $description = (string) ($event->DESCRIPTION ?? '');
            $descriptionClean = str_replace(['\n', '\r'], "\n", $description);
            $lignes = array_values(array_filter(array_map('trim', explode("\n", $descriptionClean))));
            
            $professeurs = [];

            foreach ($lignes as $ligne) {
                $ligneMin = mb_strtolower($ligne, 'UTF-8');

                // 1. Exclure la date d'export finale
                if (strpos($ligne, '(Exporté le:') === 0) {
                    continue; 
                }
                
                // 2. Exclure le code technique interne ADE
                if (strpos($ligne, 'Z--') === 0) {
                    continue;
                }

                // 3. Exclure les étiquettes de groupes (ex: "Groupe 1", "Groupe 2")
                if (preg_match('/^groupe\s*\d+$/i', $ligneMin)) {
                    continue;
                }

                // 4. Exclure les mots-clés isolés générés par ADE (évaluations, examens, etc.)
                $motsParasites = [
                    'ds', 'évaluation', 'évaluation tp', 'autonomie', 
                    'soutenance', 'soutenance finale', 'contrôle tp'
                ];
                if (in_array($ligneMin, $motsParasites)) {
                    continue;
                }

                // 5. Exclure la nomenclature technique du cours
                // D'après votre fichier ADE, les modules contiennent la mention du groupe (-GrpX)
                // ou le type de cours (-CM-, -TD-, -TP-, -CMTD-)
                if (preg_match('/-Grp\d+/i', $ligne)) {
                    continue;
                }
                if (preg_match('/-(CM|TD|TP|CMTD|Projet)(-| |$)/i', $ligne)) {
                    continue;
                }

                // Si la ligne a survécu à TOUS ces filtres, c'est que c'est un professeur.
                // Ex: "FERRAGUTI ERICH X250", "ACHDDOU JULIETTE", "Letupe Kevin X17"
                $professeurs[] = $ligne;
            }
            
            // On regroupe les profs s'il y en a plusieurs (ex: co-animation)
            $nom_prof = !empty($professeurs) ? implode(', ', $professeurs) : 'Non renseigné';
            // ----------------------------------------

            $eventsTable[] = [
                'uid'         => $uid,
                'titre'       => $titre,
                'salle'       => $salle,
                'professeur'  => $nom_prof,
                'debut'       => $debut,
                'fin'         => $fin,
            ];
        }
    }

    return $eventsTable;
}

$lien=downloads_ics($pdo,$formation);
print_r(parseICS($lien));