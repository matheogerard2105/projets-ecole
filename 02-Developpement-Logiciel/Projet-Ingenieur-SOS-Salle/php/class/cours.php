<?php

class cours{

    /* Propriétés */
    // Heure de début de l'emploi du temps (8h)
    const HEURE_DEBUT = 8;
    // Heue de fin de l'emploi du temps (20h)
    const HEURE_FIN = 20;
    const DECOUPAGE_HEURE = 15; // Découpage en minutes (ex: 15 pour des créneaux de 15 minutes)
        
    public string $uid;
    public string $titre;
    public string $salle;
    public string $professeur;
    public DateTime $date_debut;
    public DateTime $date_fin;

    // NOUVEAU : Propriétés pour gérer les superpositions
    public int $overlap_count = 1; // Combien de cours en même temps ?
    public int $overlap_index = 0; // Quelle est la position de ce cours (0, 1, 2...) ?

    // Utiles pour l'affichage des langues
    public string $groupe;

    /* Constructeur */

    public function __construct(string $uid, string $titre, string $salle, string $professeur, Datetime $date_debut, Datetime $date_fin) {
        $this->uid = $uid;
        $this->titre = $titre;
        $this->salle = $salle;
        $this->professeur = $professeur;
        $this->date_debut = $date_debut;
        $this->date_fin = $date_fin;
    }

    /**************************************

    Fonctions d'affichage de l'EDT

    ***************************************/

    /* Méthode d'information sur l'objet */

    //Permet de positionner le bloc du cours dans l'EDT
    public function calculateLignGrid($datetime) {
        $h = (int) $datetime->format('H');
        $m = (int) $datetime->format('i');
        return 2 + ($h - self::HEURE_DEBUT) * 4 + ($m / self::DECOUPAGE_HEURE);
    }

    public function calculateColGrid(){
        return (int) $this->getDay() + 1; // +1 car la première colonne est réservée aux heures
    }

    public function printHTML(int $col){
        $lig_haut = $this->calculateLignGrid($this->date_debut);
        $lig_bas  = $this->calculateLignGrid($this->date_fin);
        
        $width = 100 / $this->overlap_count;
        $margin_left = $width * $this->overlap_index;
        
        $style = "grid-row: {$lig_haut} / {$lig_bas}; ";
        $style .= "grid-column: {$col}; ";
        $style .= "width: calc({$width}% - 2px); ";
        $style .= "margin-left: {$margin_left}%; ";

        $classeType = $this->determinerTypeCss();
        
        echo "<div class='cours {$classeType}' style='{$style}'>";
        echo "<div class='cours-contenu'>";

        if (!empty($this->groupeHtml)) {
            // Affichage spécifique pour les langues fusionnées (le HTML est déjà échappé)
            echo "<strong>Langues</strong>";
            echo "<div class='cours-groupes-container'>" . $this->groupeHtml . "</div>";
        } else {
            // Affichage classique
            echo "<strong>" . htmlspecialchars($this->titre) . "</strong>";
            echo "<span>" . htmlspecialchars($this->salle) . "</span>";
            echo "<span>" . htmlspecialchars($this->professeur) . "</span>";
        }

        echo "</div>"; // Fin cours-contenu

        // Bulle d'information globale du cours (déjà existante)
        $heure_debut = $this->date_debut->format('H:i');
        $heure_fin = $this->date_fin->format('H:i');
        
        echo "<div class='cours-tooltip {$classeType}'>";
        echo "<strong>" . htmlspecialchars($this->titre) . "</strong><br>";
        echo "🕓 {$heure_debut} - {$heure_fin}<br>";
        echo "📍 " . htmlspecialchars($this->salle) . "<br>";
        echo "👨‍🏫 " . htmlspecialchars($this->professeur);
        echo "</div>";

        echo "</div>";
    }

    protected function determinerTypeCss(): string {
        // On cherche les mots clés sans tenir compte de la casse (i),
        // entourés de n'importe quoi sauf des lettres (tirets, espaces, chiffres autorisés)
        $pattern = '/(?<![a-z])(DS|EXAMEN|CMTP|CMTD|CM|TD|TP|LANGUES|Espagnol)(?![a-z])/i';
        
        if (preg_match($pattern, $this->titre, $matches)) {
            $type = strtoupper($matches[1]);
            
            return match($type) {
                'CM' => 'cours-cm',
                'TD' => 'cours-td',
                'TP' => 'cours-tp',
                'CMTD' => 'cours-cmtd',
                'CMTP' => 'cours-cmtp',
                'DS', 'EXAMEN' => 'cours-ds',
                'LANGUES','Espagnol' => 'cours-langues', // Si tu as utilisé la fusion des cours de langues
                default => 'cours-default',
            };
        }
        return 'cours-default';
    }

    /* Getters du numéro de semaine de la date actuelle */

    public function getWeek(){
        return (int) $this->date_debut->format('W');
    }

    /* Getters de l'année de la date actuelle */

    public function getYear(){
        return (int) $this->date_debut->format('Y');
    }

    /* Getters du numéro du jour de la semaine de la date actuelle */

    public function getDay(){
        return (int) $this->date_debut->format('N');
    }

    /* Getters */

    public function getUID(): string{
        return $this->uid;
    }

    public function getTitre(): string{
        return $this->titre;
    }

    public function getSalle(): string{
        return $this->salle;
    }

    public function getProfesseur(): string{
        return $this->professeur;
    }

    public function getDateDebut(): Datetime{
        return $this->date_debut;
    }

    public function getDateFin(): Datetime{
        return $this->date_fin;
    }

    /* Setters */
    public function setTitre($newTitre): void{
        $this->titre = $newTitre;
    }
}