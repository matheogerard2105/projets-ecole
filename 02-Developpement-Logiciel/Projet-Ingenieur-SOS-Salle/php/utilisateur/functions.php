<?php

require_once 'config.php';

$UPLOADS_FILE = "uploads";
while (!file_exists($UPLOADS_FILE)){
    $UPLOADS_FILE = '../' . $UPLOADS_FILE;
}

$pdo = connectUserDatabase("app_reader","postgres");

/**************************************

    Database connection functions

***************************************/

function connectUserDatabase(String $user, String $pass): PDO {
    global $host, $port, $db;
    $dsn = "pgsql:host=$host;port=$port;dbname=$db;options='--client_encoding=UTF8'";
    try {
        $pdo = new PDO($dsn, $user, $pass);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        // echo "Database connection successful.";
        return $pdo;
    } catch (PDOException $e) {
        die("Database connection failed: " . $e->getMessage());
    }
}


/**************************************

    Getteurs de données

***************************************/

function getUploadICS(string $formation): string{
    global $UPLOADS_FILE;

    $TRI_EDT = $UPLOADS_FILE . "/TRI_EDT_" . $formation . ".ics";
    if (file_exists($TRI_EDT)){
        return $TRI_EDT;
    } else {
    $EDT = $UPLOADS_FILE . "/EDT_" . $formation . ".ics";
        if (file_exists($EDT)){
            return $EDT;
        } else {
            throw new Exception("Fichier ICS introuvable",404);
        }
    }
}

function getAllICSEntries(PDO $pdo){
    $stmt = $pdo->query("SELECT g.id, g.nom AS formation, l.lien AS url_ics
                         FROM groupe g
                         JOIN liens_groupes lg ON g.id = lg.groupe_id
                         JOIN lien_ade l ON lg.lien_id = l.id");
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

function getAllFormations(PDO $pdo){
    $stmt = $pdo->query("SELECT g.nom FROM groupe as g WHERE g.actif AND NOT g.is_super_group");
    return $stmt->fetchAll(PDO::FETCH_COLUMN);
}

function getLienADE(PDO $pdo, string $formation){
    $stmt = $pdo->prepare("SELECT l.lien AS url_ics
                           FROM groupe g
                           JOIN liens_groupes lg ON g.id = lg.groupe_id
                           JOIN lien_ade l ON lg.lien_id = l.id
                           WHERE g.nom = :formation");
    $stmt->execute([':formation' => $formation]);
    return $stmt->fetchColumn();
}

function getAllSalles(PDO $pdo){
    $stmt = $pdo->query("SELECT concat(batiment, num) AS NOM FROM salle");
    return $stmt->fetchAll(PDO::FETCH_COLUMN);
}

// à tester
function getAllCoursSalle(PDO $pdo, string $salle){
    $stmt = $pdo->prepare(" SELECT c.titre, c.date_deb, c.date_fin, c.text_salle, c.text_enseignant
                            FROM cours AS c
                            JOIN salle_cours cs ON c.id = cs.cours_id
                            JOIN salle s ON cs.salle_id = s.id
                            WHERE CONCAT(s.batiment, s.num) = :salle");
    stmt->execute([':salle' => $salle]);
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

function getAllCoursGroupe(PDO $pdo, string $formation){
    $stmt = $pdo->prepare("SELECT titre, date_deb, date_fin, e.nom, concat(s.batiment, s.num)
                           FROM cours AS c
                           JOIN groupe_cours AS gc ON c.id = gc.cours_id
                           JOIN groupe AS g ON gc.groupe_id = g.id
                           JOIN salle_cours AS sc ON c.id = sc.cours_id
                           JOIN salle AS s ON sc.salle_id = s.id
                           JOIN enseignant_cours AS ec ON c.id = ec.cours_id
                           JOIN enseignant AS e ON ec.enseignant_id = e.id
                           WHERE g.nom = :formation");
    $stmt->execute([':formation' => $formation]);
    return $stmt->fetchAll();
}

function getAllCoursGroupeDay(PDO $pdo, string $identifiant, Datetime $date){
    $date_start = clone $date;
    $date_j = $date_start->format('Y-m-d');

    $date_start->modify('+1 day');
    $date_jplus1 = $date_start->format('Y-m-d');

    $stmt = $pdo->prepare("SELECT titre, date_deb, date_fin,
                            e.nom as prof, concat(s.batiment, s.num) as salle
                           FROM cours AS c
                           JOIN groupe_cours AS gc ON c.id = gc.cours_id
                           JOIN groupe AS g ON gc.groupe_id = g.id
                           JOIN salle_cours AS sc ON c.id = sc.cours_id
                           JOIN salle AS s ON sc.salle_id = s.id
                           JOIN enseignant_cours AS ec ON c.id = ec.cours_id
                           JOIN enseignant AS e ON ec.enseignant_id = e.id
                           WHERE g.nom = :formation
                           AND date_deb >= :date_j
                           AND date_deb < :date_jplus1");
    $stmt->execute([
        ':formation' => $formation,
        ':date_j' => $date_j,
        ':date_jplus1' => $date_jplus1
    ]);
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}


/**************************************

    Fonctions de parsing de l'EDT

***************************************/

function parseICS(string $localFilePath): array {
    // Lecture et parsing depuis la copie locale
    // 1. VÉRIFICATION DU FICHIER (Correction de l'erreur)
    if (!file_exists($localFilePath) || !is_readable($localFilePath)) {
        throw new Exception("Erreur : Le fichier ICS est introuvable ou illisible à l'emplacement : " . $localFilePath);
    }

    // 2. LECTURE DU FICHIER (C'est la ligne qui manquait !)
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

/***********************************************

    Fonctions d'affichage des cours en semaine

************************************************/

// Code inutilisé ici maintenant
function fusionnerCoursLangues(array $coursList): array {
    $coursFusionnes = [];
    $groupesLangues = [];

    // 1. Isoler les cours de langues
    foreach ($coursList as $cours) {
        if (str_starts_with(trim($cours->titre), '--')) {
            $clef_horaire = $cours->date_debut->getTimestamp() . '_' . $cours->date_fin->getTimestamp();
            $groupesLangues[$clef_horaire][] = $cours;
        } else {
            $coursFusionnes[] = $cours;
        }
    }

    // 2. Traiter les créneaux
    foreach ($groupesLangues as $clef => $listeCours) {
        if (count($listeCours) === 1) {
            $cours = $listeCours[0];
            $cours->titre = ltrim($cours->titre, '- ');
            $coursFusionnes[] = $cours;
        } else {
            $groupementsParMatiere = [];

            // Regroupement par matière
            foreach ($listeCours as $c) {
                $nomNettoye = ltrim($c->titre, '- ');
                $parts = explode('-Grp', $nomNettoye);
                
                if (count($parts) >= 2) {
                    $matiere = trim($parts[0]);
                    $groupe = 'Grp' . trim($parts[1]);
                } else {
                    $matiere = $nomNettoye;
                    $groupe = 'Sans groupe';
                }

                $groupementsParMatiere[$matiere][] = [
                    'groupe' => $groupe,
                    'salle'  => !empty($c->salle) ? $c->salle : 'Sans salle',
                    'prof'   => !empty($c->professeur) ? $c->professeur : 'Inconnu'
                ];
            }

            // Génération du bloc HTML spécifique pour ce regroupement
            // Génération du bloc HTML spécifique pour ce regroupement
            $htmlGroupes = "";
            foreach ($groupementsParMatiere as $matiere => $details) {
                $listeGroupes = array_column($details, 'groupe');
                $groupesStr = implode(', ', $listeGroupes);

                // Remplacement de 'matiere-bloc' par 'matiere-ligne'
                $htmlGroupes .= "<div class='matiere-ligne'>";
                $htmlGroupes .= "<span class='matiere-titre'>▪ " . htmlspecialchars($matiere) . "</span>";
                $htmlGroupes .= "<span class='matiere-groupes'>(" . htmlspecialchars($groupesStr) . ")</span>";
                
                // Bouton Détails
                $htmlGroupes .= "<div class='details-wrapper'>";
                $htmlGroupes .= "<span class='btn-details'>...</span>";
                $htmlGroupes .= "<div class='details-content'>";
                foreach ($details as $d) {
                    $htmlGroupes .= "<strong>" . htmlspecialchars($d['groupe']) . "</strong> : " .
                                    htmlspecialchars($d['salle']) . " - " .
                                    htmlspecialchars($d['prof']) . "<br>";
                }
                $htmlGroupes .= "</div></div>"; // Fin details-content & details-wrapper
                $htmlGroupes .= "</div>"; // Fin matiere-ligne
            }

            $nouveauCoursLangue = new cours(
                'UID',
                'Langues',
                'Salles multiples',
                'Multiples',
                $listeCours[0]->date_debut,
                $listeCours[0]->date_fin
            );

            // On stocke le HTML généré dans une nouvelle propriété
            $nouveauCoursLangue->groupeHtml = $htmlGroupes;
            $coursFusionnes[] = $nouveauCoursLangue;
        }
    }

    return $coursFusionnes;
}

// Code inutilisé ici maintenant
function gererSuperpositions(array $coursList): array {
    // 1. Grouper par jour de la semaine (1 = Lundi, 2 = Mardi...)
    $coursParJour = [];
    foreach ($coursList as $cours) {
        $jour = $cours->getDateDebut()->format('N');
        $coursParJour[$jour][] = $cours;
    }

    // 2. Traiter chaque jour indépendamment
    foreach ($coursParJour as $jour => $coursDuJour) {
        
        // Trier les cours du jour par ordre chronologique
        usort($coursDuJour, function($a, $b) {
            return $a->getDateDebut() <=> $b->getDateDebut();
        });

        // Créer des "grappes" de cours qui se touchent ou se chevauchent
        $groupes = [];
        $groupeActuel = [];
        $finMaxGroupe = null;

        foreach ($coursDuJour as $cours) {
            if (empty($groupeActuel)) {
                $groupeActuel[] = $cours;
                $finMaxGroupe = $cours->getDateFin();
            } else {
                if ($cours->getDateDebut() < $finMaxGroupe) { // Chevauchement détecté
                    $groupeActuel[] = $cours;
                    if ($cours->getDateFin() > $finMaxGroupe) {
                        $finMaxGroupe = $cours->getDateFin();
                    }
                } else { // Pas de chevauchement, on démarre une nouvelle grappe
                    $groupes[] = $groupeActuel;
                    $groupeActuel = [$cours];
                    $finMaxGroupe = $cours->getDateFin();
                }
            }
        }
        if (!empty($groupeActuel)) $groupes[] = $groupeActuel;

        // 3. Répartir les cours en colonnes dans chaque grappe
        foreach ($groupes as $groupe) {
            $colonnes = []; // Nos "sous-colonnes" virtuelles

            foreach ($groupe as $cours) {
                $place = false;
                foreach ($colonnes as $index => &$colonne) {
                    $chevauche = false;
                    foreach ($colonne as $coursExistant) {
                        if ($cours->getDateDebut() < $coursExistant->getDateFin() && $cours->getDateFin() > $coursExistant->getDateDebut()) {
                            $chevauche = true;
                            break;
                        }
                    }
                    if (!$chevauche) {
                        $colonne[] = $cours;
                        $cours->overlap_index = $index;
                        $place = true;
                        break;
                    }
                }
                if (!$place) {
                    $colonnes[] = [$cours];
                    $cours->overlap_index = count($colonnes) - 1;
                }
            }

            // Mettre à jour tous les cours de la grappe avec le nombre total de colonnes
            $total_colonnes = count($colonnes);
            foreach ($groupe as $cours) {
                $cours->overlap_count = $total_colonnes;
            }
        }
    }
    return $coursList;
}

// Code inutilisé ici maintenant
function getCoursWeek(String $localFilePath, int $weekNumber, int $annee = 2026): array {
    $events = parseICS($localFilePath);
    $coursList = [];
    $fuseauParis = new DateTimeZone("Europe/Paris");

    foreach ($events as $event) {
        
        if (empty($event['debut']) || empty($event['fin'])) {
            continue;
        }
        
        $date_debut = new DateTime($event['debut']);
        $date_debut->setTimezone($fuseauParis);

        if ((int) $date_debut->format('W') !== $weekNumber) {
            continue; // Ignore les cours qui ne sont pas dans la semaine demandée
        }

        $date_fin = new DateTime($event['fin']);
        $date_fin->setTimezone($fuseauParis);

        $uid = $event['uid'];
        $titre = $event['titre'];
        $salle = $event['salle'];
        $professeur = $event['professeur'];
        

        $coursList[] = new cours(
            $uid,
            $titre,
            $salle,
            $professeur,
            $date_debut,
            $date_fin
        );
    }
    $coursFusionnés = fusionnerCoursLangues($coursList);
    return gererSuperpositions($coursFusionnés);
}

// Code inutilisé ici maintenant
function getCoursDay(String $localFilePath, int $dayNumber, int $weekNumber, int $annee = 2026): array {
    $events = parseICS($localFilePath);
    $coursList = [];
    $fuseauParis = new DateTimeZone("Europe/Paris");

    foreach ($events as $event) {
        
        if (empty($event['debut']) || empty($event['fin'])) {
            continue;
        }

        $date_debut = new DateTime($event['debut']);
        $date_debut->setTimezone($fuseauParis);

        if ((int) $date_debut->format('N') !== $dayNumber || (int) $date_debut->format('W') !== $weekNumber) {
            continue; // Ignore les cours qui ne sont pas dans le jour ou la semaine demandée
        }
        
        $date_fin = new DateTime($event['fin']);
        $date_fin->setTimezone($fuseauParis);

        $uid = $event['uid'];
        $titre = $event['titre'];
        $salle = $event['salle'];
        $professeur = $event['professeur'];
        

        $coursList[] = new cours(
            $uid,
            $titre,
            $salle,
            $professeur,
            $date_debut,
            $date_fin
        );
    }
    $coursFusionnés = fusionnerCoursLangues($coursList);
    return gererSuperpositions($coursFusionnés);
}

function getDatetimeFromWeek(int $annee, int $semaine, int $jour): DateTime {
    $date = new DateTime();
    // Le 3ème paramètre est le jour de la semaine : 1 = Lundi
    $date->setISODate($annee, $semaine, $jour);
    $date->setTime(0, 0, 0); // On s'assure d'être à 00:00:00
    
    return $date;
}

function getLimitesSemaine(int $annee, int $semaine): array {
    $lundi = new DateTime();
    $lundi->setISODate($annee, $semaine, 1); // 1 = Lundi
    $lundi->setTime(0, 0, 0); // Début de journée

    $dimanche = new DateTime();
    $dimanche->setISODate($annee, $semaine, 7); // 7 = Dimanche
    $dimanche->setTime(23, 59, 59); // Fin de journée

    return [
        'lundi'    => $lundi,
        'dimanche' => $dimanche
    ];
}



/***********************************************

    Comportements inattendus

    1 - l'info-bulle est caché sous les cours
    du dessus sur les colonnes droites

***********************************************/
