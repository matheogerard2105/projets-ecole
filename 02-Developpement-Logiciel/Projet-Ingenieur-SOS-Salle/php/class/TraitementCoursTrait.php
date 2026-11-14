<?php

include_once __DIR__ .'/cours.php';

trait TraitementCoursTrait {

    /* Renvoie une liste de salle|amphi si le cours en contient plusieurs Ex:CTES*/
    private function filtrePlusieursSalleSimultanees(cours $cours): array{
        $regex = '/([A-Z][0-9]{3}|Amphi - .+|Amphi prestige - .+)/';
        preg_match($regex, $cours->getSalle(), $matches);
        if (count($matches) > 2){
            return $matches;
        }
        return $matches;
    }

    /* Renvoie une liste de prof */
    private function filtreProfesseur(cours $cours): array{
        return explode(", ", $cours->getProfesseur());
    }

    /* Fonction qui filtre uniquement les cours de langues lorsqu'il y en a beaucoup en même temps.
    Si le système ne change pas, cela concerne l'Allemand, l'Espagnol et l'Anglais si plus à rajouter
    Ainsi les cours en Japonais/Arabe ou autre seront affichés à part
    */
    private function isCoursLangue(cours $cours): bool{
        $regex = '/Allemand|Anglais|English|Espagnol|Spanish/';
        if (preg_match($regex, $cours->getTitre())){
            return true;
        }
        return false;
    }

    private function fusionCoursSimultanees(array $listeCours): cours {
        // S'il n'y a qu'un seul cours sur ce créneau, pas de fusion nécessaire
        if (count($listeCours) === 1) {
            $cours = $listeCours[0];
            
            // Retirer "-TD" et nettoyer les tirets résiduels
            $titre = str_replace('-TD', '', $cours->getTitre());
            $titre = trim(preg_replace('/-+/', '-', $titre), '- ');
            $cours->setTitre($titre);
            
            return $cours;
        }

        $groupementsParMatiere = [];

        // Extraire les données de chaque cours
        foreach ($listeCours as $c) {
            $titre = trim($c->getTitre(), '- ');
            $parts = explode('-Grp', $titre);
            
            if (count($parts) >= 2) {
                $matiere = trim($parts[0]);
                $numGroupe = trim($parts[1]); // On isole juste le numéro (ex: "1")
                $groupe = 'Grp ' . $numGroupe;
            } else {
                $matiere = $titre;
                $numGroupe = ''; // Géré comme cas spécial plus bas
                $groupe = 'Sans groupe';
            }

            // 3. Retirer "-TD" de la matière
            $matiere = str_replace('-TD', '', $matiere);
            $matiere = trim($matiere, '- '); // Au cas où il resterait un tiret mal placé

            $groupementsParMatiere[$matiere][] = [
                'groupe'     => $groupe,
                'num_groupe' => $numGroupe, // Sauvegardé pour le tri et l'affichage
                'salle'      => !empty($c->salle) ? $c->salle : 'Sans salle',
                'prof'       => !empty($c->professeur) ? $c->professeur : 'Inconnu'
            ];
        }

        // Générer le HTML
        $htmlGroupes = "";
        foreach ($groupementsParMatiere as $matiere => $details) {
            
            // 1. Trier les groupes par leur numéro (tri naturel pour que "2" soit avant "10")
            usort($details, function($a, $b) {
                return strnatcmp($a['num_groupe'], $b['num_groupe']);
            });

            // 2. Écrire sous la forme "Grp 1-2-3"
            $numeros = array_filter(array_column($details, 'num_groupe')); // Récupère juste [1, 2, 3]
            if (!empty($numeros)) {
                $groupesStr = 'Grp ' . implode('-', $numeros);
            } else {
                $groupesStr = 'Sans groupe';
            }

            $htmlGroupes .= "<div class='matiere-ligne'>";
            $htmlGroupes .= "<span class='matiere-titre'>▪ " . htmlspecialchars($matiere) . "</span>";
            $htmlGroupes .= "<span class='matiere-groupes'>(" . htmlspecialchars($groupesStr) . ")</span>";
            
            $htmlGroupes .= "<div class='details-wrapper'>";
            $htmlGroupes .= "<span class='btn-details'>...</span>";
            $htmlGroupes .= "<div class='details-content'>";
            
            // Le tableau $details étant trié, la liste déroulante sera triée elle aussi
            foreach ($details as $d) {
                $htmlGroupes .= "<strong>" . htmlspecialchars($d['groupe']) . "</strong> : " .
                                htmlspecialchars($d['salle']) . " - " .
                                htmlspecialchars($d['prof']) . "<br>";
            }
            $htmlGroupes .= "</div></div></div>";
        }

        // Créer l'objet fusionné
        $nouveauCoursLangue = new cours(
            'UID',
            'Langues',
            'Salles multiples',
            'Multiples',
            $listeCours[0]->getDateDebut(),
            $listeCours[0]->getDateFin()
        );

        $nouveauCoursLangue->groupeHtml = $htmlGroupes;
        return $nouveauCoursLangue;
    }

    public function fusionnerCoursLangues(iterable $coursList): array {
        $coursFusionnes = [];
        $groupesLangues = [];
        // 1. Isoler les cours de langues et les regrouper par créneau horaire
        foreach ($coursList as $cours) {
            if ($this->isCoursLangue($cours)) { // ou $this->isCoursLangue($cours) si c'est une méthode de classe
                $clef_horaire = $cours->getDateDebut()->getTimestamp() . '_' . $cours->getDateFin()->getTimestamp();
                $groupesLangues[$clef_horaire][] = $cours;
            } else {
                $coursFusionnes[] = $cours;
            }
        }
        // 2. Traiter les créneaux en appelant la méthode dédiée pour chaque groupe
        foreach ($groupesLangues as $listeCours) {
            $coursFusionnes[] = $this->fusionCoursSimultanees($listeCours);
        }
        return $coursFusionnes;
    }

    public function gererSuperpositions(iterable $coursList): array {
        // Votre code exact... (inchangé)
        $coursParJour = [];
        foreach ($coursList as $cours) {
            $jour = $cours->getDateDebut()->format('N');
            $coursParJour[$jour][] = $cours;
        }

        foreach ($coursParJour as $jour => $coursDuJour) {
            usort($coursDuJour, function($a, $b) {
                return $a->getDateDebut() <=> $b->getDateDebut();
            });

            $groupes = [];
            $groupeActuel = [];
            $finMaxGroupe = null;

            foreach ($coursDuJour as $cours) {
                if (empty($groupeActuel)) {
                    $groupeActuel[] = $cours;
                    $finMaxGroupe = $cours->getDateFin();
                } else {
                    if ($cours->getDateDebut() < $finMaxGroupe) {
                        $groupeActuel[] = $cours;
                        if ($cours->getDateFin() > $finMaxGroupe) {
                            $finMaxGroupe = $cours->getDateFin();
                        }
                    } else {
                        $groupes[] = $groupeActuel;
                        $groupeActuel = [$cours];
                        $finMaxGroupe = $cours->getDateFin();
                    }
                }
            }
            if (!empty($groupeActuel)) $groupes[] = $groupeActuel;

            foreach ($groupes as $groupe) {
                $colonnes = []; 
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

                $total_colonnes = count($colonnes);
                foreach ($groupe as $cours) {
                    $cours->overlap_count = $total_colonnes;
                }
            }
        }
        
        // Retourne un tableau simple (important pour la suite)
        return is_array($coursList) ? $coursList : iterator_to_array($coursList);
    }
}