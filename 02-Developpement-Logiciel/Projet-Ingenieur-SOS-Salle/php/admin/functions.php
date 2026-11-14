<?php

require_once __DIR__ . '/config.php';
require __DIR__ . '/../../vendor/autoload.php';

use Sabre\VObject\Reader;

$UPLOADS_FILE = "uploads";
while (!file_exists($UPLOADS_FILE)){
    $UPLOADS_FILE = '../' . $UPLOADS_FILE;
}

/**************************************

    Database connection functions

***************************************/

function connectAdminDatabase() {
    global $host, $port, $db, $user, $pass;
    // Correct
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

function connectUserDatabase($user, $pass) {
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

/***************************************************

    Fonctions d'accès à la base de données

****************************************************/

function getAllICSEntries(PDO $pdo) {
    $stmt = $pdo->query("SELECT g.id, g.nom AS formation, l.lien AS url_ics
                         FROM groupe g
                         JOIN liens_groupes lg ON g.id = lg.groupe_id
                         JOIN lien_ade l ON lg.lien_id = l.id");
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

function getAllICSNotSuperGroupe(PDO $pdo) {
    $stmt = $pdo->query("SELECT g.id, g.nom AS formation, l.lien AS url_ics
                         FROM groupe g
                         JOIN liens_groupes lg ON g.id = lg.groupe_id
                         JOIN lien_ade l ON lg.lien_id = l.id
                         WHERE NOT g.is_super_group");
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

function getLienADE(PDO $pdo, string $nom_fichier) {
    $sql = "SELECT l.lien FROM lien_ade as l JOIN liens_";
    // Détection : on vérifie si la chaîne contient une salle (ex: A123)
    if (preg_match('/([A-Z][0-9]{3})/', $nom_fichier, $matches)) {
        $identifiant = $matches[1];
        $sql .= "salles AS ls ON l.id = ls.lien_id ";
        $sql .= "JOIN salle as s ON ls.salle_id = s.id ";
        $sql .= "WHERE CONCAT(s.batiment, s.num) = :identifiant";
    } else {
        $identifiant = $nom_fichier;
        $sql .= "groupes AS lg ON l.id = lg.lien_id ";
        $sql .= "JOIN groupe as g ON lg.groupe_id = g.id ";
        $sql .= "WHERE nom = :identifiant";
    }
    $stmt = $pdo->prepare($sql);
    $stmt->execute([':identifiant' => $identifiant]);
    return (string) $stmt->fetchColumn();
}

function getUploadICS(string $nom_fichier): string {
    global $UPLOADS_FILE;

    // Détection : on vérifie si la chaîne contient une salle (ex: A123)
    if (preg_match('/([A-Z][0-9]{3})/', $nom_fichier, $matches)) {
        $identifiant = $matches[1];
    } else {
        $identifiant = $nom_fichier;
    }

    // Construction des chemins avec l'identifiant (salle ou formation)
    $TRI_EDT = $UPLOADS_FILE . "/TRI_EDT_" . $identifiant . ".ics";
    $EDT = $UPLOADS_FILE . "/EDT_" . $identifiant . ".ics";

    if (file_exists($TRI_EDT)) {
        return $TRI_EDT;
    } elseif (file_exists($EDT)) {
        return $EDT;
    } else {
        throw new Exception("Fichier ICS introuvable pour : " . $identifiant, 404);
    }
}

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


/* Existence des éléments des tables SQL */

/* GROUPE */
function existsGroupe(PDO $pdo, string $formation): int{
    return (int) $pdo->query("SELECT id FROM groupe WHERE nom = '$formation'")->fetchColumn();
}

/* LIEN_ADE */
function existsLien(PDO $pdo, string $url_ics): int{
    return (int) $pdo->query("SELECT id FROM lien_ade WHERE lien = '$url_ics'")->fetchColumn();
}

/* SALLE */
function existsSalle(PDO $pdo, string $batiment, String $num): int{
    $stmt = $pdo->prepare("SELECT id FROM salle
                            WHERE batiment = :batiment
                            AND num = :num");
    $stmt->execute([
        ':batiment' => $batiment,
        ':num' => $num
    ]);
    return (int) $stmt->fetchColumn();
}

/* COURS */
function existsCours(PDO $pdo, $cours): int{
    $uid = $cours->getUID();
    return (int) $pdo->query("SELECT id FROM cours WHERE uid = '$uid'")->fetchColumn();
}

/* ENSEIGNANT */
function existsEnseignant(PDO $pdo, string $professeur): int{
    return (int) $pdo->query("SELECT id FROM enseignant WHERE nom = '$professeur'")->fetchColumn();
}

/***************************************************

    Fonctions de modification de la base de données

 ***************************************************/

/* INSERT/DELETE GROUPE */

function insertGroupe(PDO $pdo, string $formation): int{
    $id = existsGroupe($pdo, $formation);
    if (!$id){
        $stmt = $pdo->prepare("INSERT INTO groupe (nom) VALUES (:formation) RETURNING id");
        $stmt->execute([':formation' => $formation]);
        return (int) $stmt->fetchColumn();
    } else {
        return $id;
    }
}

function deleteGroupe(PDO $pdo, string $formation): int{
    $id = existsGroupe($pdo, $formation);
    if ($id){
        $stmt = $pdo->prepare("DELETE FROM groupe WHERE nom=:formation RETURNING id");
        $stmt->execute([':formation' => $formation]);
        return (int) $stmt->fetchColumn();
    }
    return 0;
}

/* INSERT/DELETE LIEN_ADE */

function insertLienADE(PDO $pdo, string $url_ics): int{
    $id = existsLien($pdo, $url_ics);
    if (!$id){
        $stmt = $pdo->prepare("INSERT INTO lien_ade (lien) VALUES (:url_ics) RETURNING id");
        $stmt->execute([':url_ics' => $url_ics]);
        return (int) $stmt->fetchColumn();
    } else {
        return $id;
    }
}

// à vérifier
function deleteLienADE(PDO $pdo, string $url_ics): int{
    $id = existsLien($pdo, $url_ics);
    if ($id){
        $stmt = $pdo->prepare("DELETE FROM lien_ade WHERE lien=:url_ics RETURNING id");
        $stmt->execute([':url_ics' => $url_ics]);
        return (int) $stmt->fetchColumn();
    }
    return 0;
}

/* INSERT/DELETE SALLE */

// à tester et les amphis ne marchent pas
function filtre_salle(string $salle): array{
    $pattern = '/([A-Z])(\d{3})/';
    if (preg_match($pattern, $salle, $matches)) {
        $batiment = $matches[1];
        $num_salle = $matches[2];
    } else {
        return ['Z999', 'Z', '999'];
    }
    return $matches;
}

function insertSalle(PDO $pdo, string $salle): int{
    $salle_filtree = filtre_salle($salle);
    $id = existsSalle($pdo, $salle_filtree[1], $salle_filtree[2]);
    if (!$id){
        $stmt = $pdo->prepare("INSERT INTO salle (num, batiment)
                                VALUES (:num, :batiment) RETURNING id");
        $stmt->execute([':num' => $salle_filtree[2], ':batiment' => $salle_filtree[1]]);
        return (int) $stmt->fetchColumn();
    }
    return $id;
}

// à tester
function deleteSalle(PDO $pdo, string $salle): int{
    $salle_filtree = filtre_salle($salle);
    $id = existsSalle($pdo, $salle_filtree[1], $salle_filtree[2]);
    if ($id){
        $stmt = $pdo->prepare("DELETE FROM salle
                                WHERE batiment=:batiment
                                AND num=:num RETURNING id");
        $stmt->execute([':num' => $salle_filtree[2], ':batiment' => $salle_filtree[1]]);
        return (int) $stmt->fetchColumn();
    }
    return 0;
}

/* INSERT/DELETE COURS */

function insertCours(PDO $pdo, $cours): int{
    $id = existsCours($pdo, $cours);
    if (!$id){
        $stmt = $pdo->prepare(" INSERT INTO cours (uid, date_deb, date_fin, titre, text_salle, text_enseignant)
                                VALUES (:uid ,:date_deb, :date_fin, :titre, :text_salle, :text_enseignant)
                                RETURNING id");
        $stmt->execute([
            ':uid'              => $cours->getUID(),
            ':date_deb'         => $cours->getDateDebut()->format('Y-m-d H:i:s'),
            ':date_fin'         => $cours->getDateFin()->format('Y-m-d H:i:s'),
            ':titre'            => $cours->getTitre(),
            ':text_salle'       => $cours->getSalle(),
            ':text_enseignant'  => $cours->getProfesseur()
        ]);
        return (int) $stmt->fetchColumn();
    }
    return $id;
}

function deleteCours(PDO $pdo, $cours): int{
    $id = existsCours($pdo, $cours);
    if ($id){
        $stmt = $pdo->prepare(" DELETE FROM cours WHERE uid = :uid RETURNING id");
        $stmt->execute([':uid' => $cours->getUID()]);
        return (int) $stmt->fetchColumn();
    }
    return 0;
}

/* INSERT/DELETE PROFESSEUR */

function insertEnseignant(PDO $pdo, string $professeur): int{
    $id = existsEnseignant($pdo, $professeur);
    if (!$id){
        $stmt = $pdo->prepare("INSERT INTO enseignant (nom) VALUES (:prof) RETURNING id");
        $stmt->execute([':prof' => $professeur]);
        return (int) $stmt->fetchColumn();
    }
    return $id;
}

function deleteEnseignant(PDO $pdo, string $professeur): int{
    $id = existsEnseignant($pdo, $professeur);
    if ($id){
        $stmt = $pdo->prepare("DELETE FROM enseignant WHERE nom=:prof RETURNING id");
        $stmt->execute([':prof' => $professeur]);
        return (int) $stmt->fetchColumn();
    }
    return 0;
}

/* TABLE CLÉ ÉTRANGÈRE */
/* Les tables sql principales étant mises en 'cascade' les suppressions des valeurs
de clé étrangères sont automatiques */

/* TABLE LIENS_GROUPES */

function insertGroupeLienADE(PDO $pdo, string $formation, string $url_ics){

    $id_groupe = insertGroupe($pdo, $formation);
    $id_lien_ade = insertLienADE($pdo, $url_ics);

    // Vérification si la relation existe déjà dans la table liens_groupes

    $stmt = $pdo->prepare("SELECT 1 FROM liens_groupes WHERE groupe_id = :id_groupe AND lien_id = :id_lien_ade");
    $stmt->execute([':id_groupe' => $id_groupe, ':id_lien_ade' => $id_lien_ade]);
    $exists = (bool) $stmt->fetchColumn();

    if ($exists) {
        echo json_encode(['status' => 'info', 'message' => 'Relation already exists in liens_groupes',
        'id_groupe' => $id_groupe, 'id_lien_ade' => $id_lien_ade]);
        return false; // Relation already exists
    } else {
        echo json_encode(['status' => 'info', 'message' => 'Inserting relation into liens_groupes',
        'id_groupe' => $id_groupe, 'id_lien_ade' => $id_lien_ade]);
    }

    $stmt = $pdo->prepare("INSERT INTO liens_groupes (groupe_id, lien_id) VALUES (:id_groupe, :id_lien_ade)");
    return $stmt->execute([':id_groupe' => $id_groupe, ':id_lien_ade' => $id_lien_ade]);
}

/* TABLE LIENS_SALLES */
function insertSalleLienADE(PDO $pdo, string $salle, string $url_ics){
    $id_salle = insertSalle($pdo, $salle);
    $id_ics = insertLienADE($pdo, $url_ics);

    $stmt = $pdo->prepare("SELECT 1 FROM liens_salles WHERE salle_id = :id_salle AND lien_id = :id_lien");
    $stmt->execute([':id_salle' => $id_salle, ':id_lien' => $id_ics]);
    $exists = (bool) $stmt->fetchColumn();

    if ($exists) {
        echo json_encode(['status' => 'info', 'message' => 'Relation already exists in liens_salles',
        'id_salle' => $id_salle, 'id_lien_ade' => $id_ics]);
        return false; // Relation already exists
    } else {
        echo json_encode(['status' => 'info', 'message' => 'Inserting relation into liens_salles',
        'id_salle' => $id_salle, 'id_lien_ade' => $id_ics]);
    }

    $stmt = $pdo->prepare("INSERT INTO liens_salles (salle_id, lien_id) VALUES (:id_salle, :id_lien_ade)");
    return $stmt->execute([':id_salle' => $id_salle, ':id_lien_ade' => $id_ics]);
}

/* TABLE SALLE_COURS */

function insertSalleCours(PDO $pdo, $cours, string $salle){
    $id_cours = insertCours($pdo, $cours);
    $id_salle = insertSalle($pdo, $salle);

    // Vérification si la relation existe déjà dans salle_cours
    $stmtExist = $pdo->prepare("SELECT 1 FROM salle_cours WHERE salle_id = :id_salle AND cours_id = :id_cours");
    $stmtExist->execute([
        ':id_salle' => $id_salle,
        ':id_cours' => $id_cours
    ]);
    
    // Insertion ou annulation
    if ($stmtExist->fetchColumn()) {
        echo json_encode(['status' => 'info', 'message' => 'Relation already exists in salle_cours', 'id_salle' => $id_salle, 'id_cours' => $id_cours]);
        return false; // La relation existe déjà
    } else {
        echo json_encode(['status' => 'info', 'message' => 'Inserting relation into salle_cours', 'id_salle' => $id_salle, 'id_cours' => $id_cours]);
        $stmtInsert = $pdo->prepare("INSERT INTO salle_cours (salle_id, cours_id) VALUES (:id_salle, :id_cours)");
        return $stmtInsert->execute([
            ':id_salle' => $id_salle,
            ':id_cours' => $id_cours
        ]);
    }
}

/* TABLE GROUPE_COURS */
// à tester
function insertGroupeCours(PDO $pdo, $cours, string $formation){
    $id_cours = insertCours($pdo, $cours);
    $id_groupe = insertGroupe($pdo, $formation);

    // Vérification si la relation existe déjà dans salle_cours
    $stmtExist = $pdo->prepare("SELECT 1 FROM groupe_cours WHERE groupe_id = :id_groupe AND cours_id = :id_cours");
    $stmtExist->execute([
        ':id_groupe' => $id_groupe,
        ':id_cours' => $id_cours
    ]);
    
    // Insertion ou annulation
    if ($stmtExist->fetchColumn()) {
        echo json_encode(['status' => 'info', 'message' => 'Relation already exists in groupe_cours', 'id_groupe' => $id_groupe, 'id_cours' => $id_cours]);
        return false; // La relation existe déjà
    } else {
        echo json_encode(['status' => 'info', 'message' => 'Inserting relation into salle_cours', 'id_salle' => $id_groupe, 'id_cours' => $id_cours]);
        $stmtInsert = $pdo->prepare("INSERT INTO groupe_cours (groupe_id, cours_id) VALUES (:id_groupe, :id_cours)");
        return $stmtInsert->execute([
            ':id_groupe' => $id_groupe,
            ':id_cours' => $id_cours
        ]);
    }
}

/* TABLE ENSEIGNANT_COURS */
// à tester
function insertEnseignantCours(PDO $pdo, $cours, string $prof){
    $id_cours = insertCours($pdo, $cours);
    $id_prof = insertEnseignant($pdo, $prof);

    // Vérification si la relation existe déjà dans salle_cours
    $stmtExist = $pdo->prepare("SELECT 1 FROM enseignant_cours WHERE enseignant_id = :id_prof AND cours_id = :id_cours");
    $stmtExist->execute([
        ':id_prof' => $id_prof,
        ':id_cours' => $id_cours
    ]);
    
    // Insertion ou annulation
    if ($stmtExist->fetchColumn()) {
        echo json_encode(['status' => 'info', 'message' => 'Relation already exists in groupe_cours', 'id_enseignant' => $id_prof, 'id_cours' => $id_cours]);
        return false; // La relation existe déjà
    } else {
        echo json_encode(['status' => 'info', 'message' => 'Inserting relation into salle_cours', 'id_enseignant' => $id_prof, 'id_cours' => $id_cours]);
        $stmtInsert = $pdo->prepare("INSERT INTO enseignant_cours (enseignant_id, cours_id) VALUES (:id_prof, :id_cours)");
        return $stmtInsert->execute([
            ':id_prof' => $id_prof,
            ':id_cours' => $id_cours
        ]);
    }
}

/* TABLE JOURNAL_LIEN */

/* TABLE JOURNAL_COURS */

/* UPDATES */

function updateSuperGroupe(PDO $pdo, string $formation, bool $isSuperGroupe){
    $stmt = $pdo->prepare("UPDATE groupe SET is_super_group = :is_super_groupe WHERE groupe.nom = :formation");
    
    $stmt->bindValue(':is_super_groupe', $isSuperGroupe, PDO::PARAM_BOOL);
    $stmt->bindValue(':formation', $formation, PDO::PARAM_STR);
    
    return $stmt->execute();
}

/* INSERTION EVEVENEMENTS */

function insertEvenement(PDO $pdo, $cours){
    $professeurs = explode(", ", $cours->getProfesseur());
    $salle = $cours->getSalle();
    foreach ($professeurs as $prof){
        insertEnseignantCours($pdo, $cours, $prof);
    }
    insertSalleCours($pdo, $cours, $salle);
}

function insertFichierICS(PDO $pdo, string $formation){
    $file_path = getUploadICS($formation);
    $events = parseICS($file_path);
    $fuseauParis = new DateTimeZone("Europe/Paris");
    foreach ($events as $event){
        if (empty($event['debut']) || empty($event['fin'])) {
            continue;
        }
        $date_debut = new DateTime($event['debut']);
        $date_debut->setTimezone($fuseauParis);
        $date_fin = new DateTime($event['fin']);
        $date_fin->setTimezone($fuseauParis);
        $uid = $event['uid'];
        $titre = $event['titre'];
        $salle = $event['salle'];
        $professeur = $event['professeur'];
    
        $cours = new cours(
            $uid,
            $titre,
            $salle,
            $professeur,
            $date_debut,
            $date_fin
        );

        insertEvenement($pdo, $cours);
        insertGroupeCours($pdo, $cours, $formation);
    }
}

/***************************************************

    Gestion des correspondances formation <-> URL ICS (F16)

 ***************************************************/

// Nom utilisé dans les noms de fichiers (uploads/EDT_<nom>.ics) : on reste strict
const REGEX_NOM_FORMATION = '/^[A-Za-z0-9_-]{1,63}$/';

function validerNomFormation(string $nom): ?string {
    if (!preg_match(REGEX_NOM_FORMATION, $nom)) {
        return "Le nom de la formation ne doit contenir que des lettres, chiffres, - ou _ (63 caractères max).";
    }
    return null;
}

function validerUrlICS(string $url): ?string {
    if (strlen($url) > 1024 || !filter_var($url, FILTER_VALIDATE_URL)) {
        return "L'URL ICS n'est pas valide.";
    }
    $scheme = parse_url($url, PHP_URL_SCHEME);
    if (!in_array($scheme, ['http', 'https'], true)) {
        return "L'URL ICS doit commencer par http:// ou https://.";
    }
    return null;
}

// Toutes les formations avec leurs flux, regroupées par formation
function getAllCorrespondances(PDO $pdo): array {
    $stmt = $pdo->query("SELECT g.id, g.nom, g.is_super_group, g.actif, g.date_modif,
                                l.id AS lien_id, l.lien AS url_ics
                         FROM groupe g
                         LEFT JOIN liens_groupes lg ON g.id = lg.groupe_id
                         LEFT JOIN lien_ade l ON lg.lien_id = l.id
                         ORDER BY g.is_super_group, g.nom, l.id");

    $groupes = [];
    foreach ($stmt->fetchAll(PDO::FETCH_ASSOC) as $row) {
        $id = $row['id'];
        if (!isset($groupes[$id])) {
            $groupes[$id] = [
                'id'             => $id,
                'nom'            => $row['nom'],
                'is_super_group' => (bool) $row['is_super_group'],
                'actif'          => (bool) $row['actif'],
                'date_modif'     => $row['date_modif'],
                'liens'          => [],
            ];
        }
        if ($row['lien_id'] !== null) {
            $groupes[$id]['liens'][] = ['id' => $row['lien_id'], 'url' => $row['url_ics']];
        }
    }
    return array_values($groupes);
}

function getCorrespondance(PDO $pdo, int $id): ?array {
    foreach (getAllCorrespondances($pdo) as $groupe) {
        if ($groupe['id'] == $id) {
            return $groupe;
        }
    }
    return null;
}

function getIdGroupeParNom(PDO $pdo, string $nom): ?int {
    $stmt = $pdo->prepare("SELECT id FROM groupe WHERE nom = :nom");
    $stmt->execute([':nom' => $nom]);
    $id = $stmt->fetchColumn();
    return $id === false ? null : (int) $id;
}

function getIdLienParUrl(PDO $pdo, string $url): ?int {
    $stmt = $pdo->prepare("SELECT id FROM lien_ade WHERE lien = :url");
    $stmt->execute([':url' => $url]);
    $id = $stmt->fetchColumn();
    return $id === false ? null : (int) $id;
}

// Crée la formation et son flux (le flux est réutilisé s'il existe déjà).
// Retourne un message d'erreur, ou null en cas de succès.
function ajouterCorrespondance(PDO $pdo, string $nom, string $url): ?string {
    if ($erreur = validerNomFormation($nom) ?? validerUrlICS($url)) {
        return $erreur;
    }
    if (getIdGroupeParNom($pdo, $nom) !== null) {
        return "La formation « $nom » existe déjà.";
    }

    $pdo->beginTransaction();
    try {
        $idLien = getIdLienParUrl($pdo, $url);
        if ($idLien === null) {
            $stmt = $pdo->prepare("INSERT INTO lien_ade (lien) VALUES (:url) RETURNING id");
            $stmt->execute([':url' => $url]);
            $idLien = (int) $stmt->fetchColumn();
        }

        $stmt = $pdo->prepare("INSERT INTO groupe (nom) VALUES (:nom) RETURNING id");
        $stmt->execute([':nom' => $nom]);
        $idGroupe = (int) $stmt->fetchColumn();

        $stmt = $pdo->prepare("INSERT INTO liens_groupes (groupe_id, lien_id) VALUES (:groupe, :lien)");
        $stmt->execute([':groupe' => $idGroupe, ':lien' => $idLien]);

        $pdo->commit();
    } catch (PDOException $e) {
        $pdo->rollBack();
        throw $e;
    }
    return null;
}

// Renomme une formation et/ou change l'URL de son flux.
// L'URL est modifiée sur la ligne lien_ade existante : les super-groupes
// qui partagent ce flux suivent donc automatiquement le changement.
function modifierCorrespondance(PDO $pdo, int $id, string $nom, string $url): ?string {
    if ($erreur = validerNomFormation($nom) ?? validerUrlICS($url)) {
        return $erreur;
    }

    $groupe = getCorrespondance($pdo, $id);
    if ($groupe === null) {
        return "Formation introuvable.";
    }
    if ($groupe['is_super_group'] || count($groupe['liens']) > 1) {
        return "Les super-groupes ne sont pas modifiables depuis ce formulaire.";
    }

    $idHomonyme = getIdGroupeParNom($pdo, $nom);
    if ($idHomonyme !== null && $idHomonyme !== $id) {
        return "La formation « $nom » existe déjà.";
    }

    $idLienActuel = $groupe['liens'][0]['id'] ?? null;
    $idLienUrl = getIdLienParUrl($pdo, $url);
    if ($idLienUrl !== null && $idLienUrl != $idLienActuel) {
        return "Cette URL ICS est déjà utilisée par une autre formation.";
    }

    $pdo->beginTransaction();
    try {
        $stmt = $pdo->prepare("UPDATE groupe SET nom = :nom WHERE id = :id");
        $stmt->execute([':nom' => $nom, ':id' => $id]);

        if ($idLienActuel === null) {
            $stmt = $pdo->prepare("INSERT INTO lien_ade (lien) VALUES (:url) RETURNING id");
            $stmt->execute([':url' => $url]);
            $idLienNouveau = (int) $stmt->fetchColumn();

            $stmt = $pdo->prepare("INSERT INTO liens_groupes (groupe_id, lien_id) VALUES (:groupe, :lien)");
            $stmt->execute([':groupe' => $id, ':lien' => $idLienNouveau]);
        } else {
            $stmt = $pdo->prepare("UPDATE lien_ade SET lien = :url WHERE id = :id");
            $stmt->execute([':url' => $url, ':id' => $idLienActuel]);
        }

        $pdo->commit();
    } catch (PDOException $e) {
        $pdo->rollBack();
        throw $e;
    }
    return null;
}

// Une formation désactivée n'est plus proposée côté utilisateur
function setFormationActive(PDO $pdo, int $id, bool $actif): bool {
    $stmt = $pdo->prepare("UPDATE groupe SET actif = :actif WHERE id = :id");
    $stmt->bindValue(':actif', $actif, PDO::PARAM_BOOL);
    $stmt->bindValue(':id', $id, PDO::PARAM_INT);
    $stmt->execute();
    return $stmt->rowCount() === 1;
}

/**************************************

    Fonctions du fichier ICS

***************************************/

// Regex pour récupérer le nom et le prénom dans le SUMMARY
function filtrage_summary($description) {
    $description = trim($description);
    $regex = '/([A-ZÀ-Ö]+ [A-ZÀ-Ö]+)/u';
    $result = preg_match($regex, $description, $matches) ? $matches[0] : null;

    if ($result) {
        echo "Trouvé : " . $matches[1]; // Affiche : NOM PRENOM
    } else {
        echo "Aucune correspondance trouvée.";
    }
}

// Test de la fonction filtrage_summary
// filtrage_summary("\n\nIS3-Remédiation Mathémati-TD-Grp1\nLIETARD THIBAULT\n(Exp
//  orté le:30/09/2026 12:50)\n");
// Résultat attendu : "LIETARD THIBAULT"

function downloads_ics($pdo, $identifiant) {
    global $UPLOADS_FILE;
    // Récupération de l'URL ICS depuis la base de données
    $icsUrl = getLienADE($pdo, $identifiant);
    print_r($icsUrl);
    $localFilePath = $UPLOADS_FILE . '/' . 'EDT' . '_' . $identifiant . '.ics';
    print_r($localFilePath);
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