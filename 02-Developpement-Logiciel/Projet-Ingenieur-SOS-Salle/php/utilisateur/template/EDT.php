<?php
require_once '../functions.php';
require_once '../../class/Jour.php';
require_once '../../class/Semaine.php';
require_once '../../class/squelette_EDT.php';
require '../../../vendor/autoload.php';

const JOURS = [
    1 => 'Lundi',2 => 'Mardi',3 => 'Mercredi',4 => 'Jeudi',
    5 => 'Vendredi',6 => 'Samedi',7 => 'Dimanche'
];

const MOIS = [
    1 => 'Janvier',2 => 'Février',3 => 'Mars',4 => 'Avril',
    5 => 'Mai',6 => 'Juin',7 => 'Juillet',8 => 'Août',
    9 => 'Septembre',10 => 'Octobre',11 => 'Novembre',
    12 => 'Décembre'
];

$today = new DateTime();

$jour = (int) (isset($_GET['jour']) ? $_GET['jour'] : $today->format('N')); // Jour de la semaine (1 = Lundi, 2 = Mardi...)
$semaine = (int) (isset($_GET['semaine']) ? $_GET['semaine'] : $today->format('W')); // Semaine de l'année
$annee = (int) (isset($_GET['annee']) ? $_GET['annee'] : $today->format('Y')); // Année

$version_print = (string) (isset($_GET['version']) ? $_GET['version'] : 'jour'); // Version à afficher : 'jour' ou 'semaine'*

$formation = isset($_GET['formation']) ? $_GET['formation'] : 'IS3';

$class_jour = new Jour(getDateTimeFromWeek($annee, $semaine, $jour));
$limites_semaines = getLimitesSemaine($annee, $semaine);
$class_semaine = new Semaine($limites_semaines['lundi'], $limites_semaines['dimanche']);

?>
<!DOCTYPE html>
<html lang='fr'>
    <head>
        <meta charset='utf-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1'>
        <title>EDT Polytech Lille</title>
        <link rel='stylesheet' href='style-grid.css'>
    </head>
    <body>

        <div class="edt-controles">
    
            <!-- Bouton Retour -->
            <button class="btn btn-secondaire" onclick="window.location.href='../../../index.php';">Retour à l'accueil</button>

            <!-- Contrôles Semaine -->
            <div class="btn-groupe">
                <button id="-1semaineButton" class="btn btn-secondaire">&lt;</button>
                <button id="semaineButton" class="btn btn-secondaire">Semaine</button>
                <button id="+1semaineButton" class="btn btn-secondaire">&gt;</button>
            </div>

            <!-- Contrôles Jour -->
            <div class="btn-groupe">
                <button id="-1jourButton" class="btn btn-secondaire">&lt;</button>
                <button id="jourButton" class="btn btn-secondaire">Jour</button>
                <button id="+1jourButton" class="btn btn-secondaire">&gt;</button>
            </div>
            <form method="get" action="" class="form-groupe">
                <select name="formation" class="form-select">
                    <?php foreach (getAllFormations($pdo) as $groupe) : ?>
                        <option value="<?= htmlspecialchars($groupe) ?>" <?= $groupe === $formation ? 'selected' : '' ?>>
                            <?= htmlspecialchars($groupe) ?></option>
                    <?php endforeach; ?>
                </select>
                <input type="submit" value="Valider" class="btn btn-primaire">
            </form>
            <button class="btn btn-secondaire" onclick="window.location.href='Salle-EDT.php';">Recherche-Salles</button>
            
        </div>
        <div class="message-rotation">
            📱 Veuillez tourner votre téléphone en mode paysage pour afficher l'emploi du temps de la semaine.
        </div>
        <h1 style="text-align: center;">Emploi du temps - <?= htmlspecialchars($formation) ?></h1>
        <div class="date-title">
            <h2 id="titre-date"></h2>
        </div>
        
        <div class="edt-grid">
            <div class="edt-grid-day">
                <?php $squelette = new squelette_EDT();
                $squelette->printSqueletteDay(JOURS[$jour]); ?>
                <!-- Cours -->
                <?php $class_jour->setCoursDay($pdo, $formation); ?>
                <?php foreach ($class_jour as $cours): ?>
                    <?php $class_jour->printCours($cours); ?>
                <?php endforeach; ?>
            </div>
            <div class="grille-semaine">
                <div class="edt-grid-week">
                    <?php $squelette = new squelette_EDT();
                    $squelette->printSqueletteWeek(); ?>
                    <?php $class_semaine->setCoursWeek($pdo, $formation); ?>
                    <!-- Cours -->
                    <?php foreach ($class_semaine as $cours): ?>
                        <?php $class_semaine->printCours($cours); ?>
                    <?php endforeach; ?>
                </div>
            </div>
        </div>
        <script>
        const versionPrint = <?= json_encode($version_print) ?>;

        const JOURS = <?= json_encode(JOURS) ?>;
        const MOIS = <?= json_encode(MOIS) ?>;

        const jour = <?php echo $jour; ?>;
        const semaine = <?php echo $semaine; ?>;
        const annee = <?php echo $annee; ?>;
        const select = <?= json_encode($formation) ?>;

        </script>
        <script src="EDT.js"></script>
    </body>
</html>