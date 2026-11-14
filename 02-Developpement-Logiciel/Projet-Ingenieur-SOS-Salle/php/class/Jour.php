<?php

include_once "cours.php";
include_once "TraitementCoursTrait.php";

/* Classe tableau de cours */
class Jour extends ArrayObject{
    use TraitementCoursTrait;

    private Datetime $date;

    public function __construct($date){
        parent::__construct();
        $this->date = $date;
    }

    public function append(mixed $value): void {
        if (!($value instanceof cours)){
            throw new Exception("La classe Jour attend des cours");
        }
        parent::append($value);
    }

    public function getDate(): Datetime{
        return this->$date;
    }
    
    public function printCours(cours $cours): void{
        $cours->printHTML(2);
    }

    public function setCoursDay(PDO $pdo, string $nom_fichier): void{
        $sql =  "SELECT uid, titre, date_deb, date_fin, ";
        $sql .= "text_enseignant as prof, text_salle as salle ";
        $sql .= "FROM cours AS c ";
        $sql .= "JOIN groupe_cours AS gc ON c.id = gc.cours_id ";
        $sql .= "JOIN groupe AS g ON gc.groupe_id = g.id ";
        $sql .= "JOIN salle_cours AS sc ON c.id = sc.cours_id ";
        $sql .= "JOIN salle AS s ON sc.salle_id = s.id ";


        if (preg_match('/([A-Z][0-9]{3})/', $nom_fichier, $matches)) {
            $identifiant = $matches[1];
            $sql .= "WHERE CONCAT(batiment,num) ='$identifiant' ";
        } else {
            $identifiant = $nom_fichier;
            $sql .= "WHERE g.nom ='$identifiant' ";
        }

        $date_start = clone $this->date;
        $date_j = $date_start->format('Y-m-d');
        $date_start->modify('+1 day');
        $date_jplus1 = $date_start->format('Y-m-d');

        $sql .= "AND date_deb >= :date_j ";
        $sql .= "AND date_deb < :date_jplus1";
        
        $stmt = $pdo->prepare($sql);
        $stmt->execute([
            ':date_j' => $date_j,
            ':date_jplus1' => $date_jplus1
        ]);

        $lignes = $stmt->fetchAll(PDO::FETCH_ASSOC);
        $coursList = [];

        // 1. Instanciation manuelle et traitement des dates
        foreach ($lignes as $row) {
            $date_deb = new Datetime($row['date_deb']);
            $date_fin = new Datetime($row['date_fin']);
            $cours = new cours(
                $row['uid'],
                $row['titre'],
                $row['salle'],
                $row['prof'],
                $date_deb,
                $date_fin
            );
            $coursList[] = $cours;
        }

        // 2. Appliquer les traitements du Trait sur les vrais objets
        $coursList = $this->fusionnerCoursLangues($coursList);
        $coursList = $this->gererSuperpositions($coursList);

        // 3. Injecter le tableau final dans l'ArrayObject
        $this->exchangeArray($coursList);
    }
}