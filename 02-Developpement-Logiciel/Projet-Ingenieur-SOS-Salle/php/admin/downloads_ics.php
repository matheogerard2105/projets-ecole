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
    $vcalendar = \Sabre\VObject\Reader::read(fopen($localFilePath, 'r'));
    $eventsTable = [];

    if (isset($vcalendar->VEVENT)) {
        foreach ($vcalendar->VEVENT as $event) {
            $titre_brut = (string) ($event->SUMMARY ?? '');
            $lieu_brut = (string) ($event->LOCATION ?? '');
            $description = (string) ($event->DESCRIPTION ?? '');
            
            // 1. TYPE DE COURS
            $type_cours = 'Non défini';
            if (preg_match('/\b(CM|TD|TP|CTD|CMTD|DS|Projet)\b/i', $titre_brut, $match_type)) {
                $type_cours = strtoupper($match_type[1]);
            }

           // 2. NOM DE LA MATIÈRE (Nettoyage ultra-robuste)
           $matiere = $titre_brut;

           // ÉTAPE A : On enlève le suffixe (le type de cours et le groupe à la fin)
           // Cible : "-TD-Grp1", "-CMTD-Grp1", " - CM", " - CTD"
           $matiere = preg_replace('/\s*-\s*(CM|TD|TP|CTD|CMTD|DS|Projet)(?:-Grp\d+)?.*$/i', '', $matiere);

           // ÉTAPE B : On enlève les préfixes enchaînés (Majuscules/Chiffres)
           // Cible : "GO-2GU2A4-", "--S5_FISA_"
           $matiere = preg_replace('/^(?:[-_]*[A-Z0-9]+[-_]+)+/', '', $matiere);

           // ÉTAPE C : On enlève les préfixes de type "Code Formation - "
           // Cible : "ISia·2A·5 (Opt.) - ", "2GU5A - "
           // Limité à 25 caractères pour ne pas effacer accidentellement un titre complet.
           $matiere = preg_replace('/^([a-zA-Z0-9·\(\) ]{2,25})\s*-\s*/u', '', $matiere);

           // ÉTAPE D : Nettoyage final pour les résidus (espaces, tirets, underscores)
           $matiere = trim($matiere, " -_");
            // 3. SALLE (Uniquement la référence de la salle, ex: B110)
            $salle = 'Non renseignée';
            if (preg_match_all('/[A-Z]\d{3}(?:\/[A-Z]\d{3})?/i', $lieu_brut, $matches)) {
                $salle = implode(', ', $matches[0]);
            }

            // 4. PROFESSEUR ET GROUPE (Heuristique d'élimination sur la description)
            $descriptionClean = str_replace(['\n', '\r'], "\n", $description);
            $lignes = array_values(array_filter(array_map('trim', explode("\n", $descriptionClean))));
            
            $professeurs = [];
            $groupe = 'Non renseigné';

            foreach ($lignes as $ligne) {
                $ligneMin = mb_strtolower($ligne, 'UTF-8');

                // A. Extraction du numéro de groupe (ex: "Groupe 1" ou "Grp1")
                if (preg_match('/(?:groupe|grp)\s*(\d+)/i', $ligneMin, $match_grp)) {
                    $groupe = $match_grp[1];
                }

                // B. Filtrage pour isoler le professeur
                if (strpos($ligne, '(Exporté le:') === 0) continue; 
                if (strpos($ligne, 'Z--') === 0) continue;
                if (preg_match('/^groupe\s*\d+$/i', $ligneMin)) continue;
                
                // Mots clés parasites d'ADE
                $motsParasites = ['ds', 'évaluation', 'évaluation tp', 'autonomie', 'soutenance', 'soutenance finale', 'contrôle tp'];
                if (in_array($ligneMin, $motsParasites)) continue;

                // Codes des modules (qui contiennent les mots TD/CM/TP ou la formation IS...)
                if (preg_match('/-(CM|TD|TP|CMTD|Projet|TP Sciences)(-| |$)/i', $ligne)) continue;
                if (preg_match('/^(MH-)?IS\d*A?\d*-/i', $ligne)) continue; // Attrape "IS5-...", "IS2A5-...", "MH-IS5..."

                // Si la ligne survit à tous les filtres, c'est un professeur
                $professeurs[] = $ligne;
            }
            
            $nom_prof = !empty($professeurs) ? implode(', ', array_unique($professeurs)) : 'Non renseigné';

            // Masquer le groupe si c'est un cours magistral ou un examen global
            if (in_array($type_cours, ['CM', 'DS'])) {
                $groupe = null;
            }

            // 5. DATES
            $debut = isset($event->DTSTART) ? $event->DTSTART->getDateTime()->format('Y-m-d H:i:s') : null;
            $fin = isset($event->DTEND) ? $event->DTEND->getDateTime()->format('Y-m-d H:i:s') : null;

            // 6. CONSTRUCTION DU TABLEAU FINAL PROPRE
            $eventsTable[] = [
                'salle'      => $salle,
                'matiere'    => $matiere,
                'type_cours' => $type_cours,
                'professeur' => $nom_prof,
                'groupe'     => $groupe,
                'debut'      => $debut,
                'fin'        => $fin
            ];
        }
    }

    return $eventsTable;
}


// Tests de fonctionnement
$lien=downloads_ics($pdo, $formation);
echo '<pre>';
print_r(parseICS($lien));
echo '</pre>';