<?php

class squelette_EDT {

    const JOURS = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi'];
    const HEURES = [
        '08:00', '08:15', '08:30', '08:45',
        '09:00', '09:15', '09:30', '09:45',
        '10:00', '10:15', '10:30', '10:45',
        '11:00', '11:15', '11:30', '11:45',
        '12:00', '12:15', '12:30', '12:45',
        '13:00', '13:15', '13:30', '13:45',
        '14:00', '14:15', '14:30', '14:45',
        '15:00', '15:15', '15:30', '15:45',
        '16:00', '16:15', '16:30', '16:45',
        '17:00', '17:15', '17:30', '17:45',
        '18:00', '18:15', '18:30', '18:45',
        '19:00', '19:15', '19:30', '19:45',
        '20:00'
    ];

    public function __construct() {
        // Initialisation si nécessaire
    }

    public function printSqueletteWeek() {
        // 1. Boucle sur les jours
        foreach (self::JOURS as $index => $jour) {
            $col = $index + 2;
            echo '<div class="jour" style="grid-column: ' . $col . ';">' . htmlspecialchars($jour) . '</div>';
        }

        // 2. Boucle sur les heures (de 8h à 20h)
        for ($heure = 8; $heure <= 20; $heure++) {
            $ligne = 2 + ($heure - 8) * 4; // Chaque heure correspond à 4 lignes (15 minutes par ligne)
            $heureFormatee = sprintf("%02d:00", $heure);
            
            echo "<div class='heure' style='grid-row: {$ligne};'>{$heureFormatee}</div>";
        }

        for ($i = 2; $i <= 50; $i++) {
            // Tous les 4 blocs (1 heure = 4 x 15min), on applique la classe 'heure-pleine'
            $classLigne = (($i - 2) % 4 === 0) ? 'heure-pleine' : 'quart-heure';
            
            echo "<div class='ligne-grille {$classLigne}' style='grid-row: {$i};'></div>";
        }

        // Génération des 6 colonnes verticales (du Lundi au Vendredi)
        for ($col = 2; $col <= 7; $col++) {
            echo "<div class='colonne-grille' style='grid-column: {$col};'></div>";
        }
    }

    public function printSqueletteDay($jour) {

        // 1. Boucle sur les jours
        $col = 2;
        echo '<div class="jour" style="grid-column: ' . $col . ';">' . htmlspecialchars($jour) . '</div>';

        // 2. Boucle sur les heures (de 8h à 20h)
        for ($heure = 8; $heure <= 20; $heure++) {
            $ligne = 2 + ($heure - 8) * 4; // Chaque heure correspond à 4 lignes (15 minutes par ligne)
            $heureFormatee = sprintf("%02d:00", $heure);
            
            echo "<div class='heure' style='grid-row: {$ligne};'>{$heureFormatee}</div>";
        }

        for ($i = 2; $i <= 50; $i++) {
            // Tous les 4 blocs (1 heure = 4 x 15min), on applique la classe 'heure-pleine'
            $classLigne = (($i - 2) % 4 === 0) ? 'heure-pleine' : 'quart-heure';
            
            echo "<div class='ligne-grille {$classLigne}' style='grid-row: {$i};'></div>";
        }

        echo "<div class='colonne-grille' style='grid-column: 2;'></div>";
        echo "<div class='colonne-grille' style='grid-column: 3;'></div>";

    }
}