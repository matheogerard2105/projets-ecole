<?php

include_once "cours.php";
include_once "TraitementCoursTrait.php";

/* Classe tableau de cours */
class Semaine extends ArrayObject{
    use TraitementCoursTrait;

    private Datetime $deb_semaine;
    // Changement possible entre Vendredi et Samedi
    private Datetime $fin_semaine;

    public function __construct(Datetime $deb_semaine, Datetime $fin_semaine){
        parent::__construct();
        $this->deb_semaine = $deb_semaine;
        $this->fin_semaine = $fin_semaine;
    }

    public function append(mixed $value): void{
        if (!($value instanceof cours)){
            throw new Exception("La classe Semaine attend des cours");
        }
        parent::append($value);
    }

    public function getDeb_semaine(): Datetime{
        return $this->deb_semaine;
    }

    public function getFin_semaine(): Datetime{
        return $this->fin_semaine;
    }

    public function printCours(cours $cours): void{
        $col = $cours->calculateColGrid();
        $cours->printHTML($col);
    }

    public function setCoursWeek(PDO $pdo, string $nom_fichier): void{
        $sql =  "SELECT uid, titre, date_deb, date_fin, ";
        $sql .= "text_enseignant as prof, text_salle as salle ";
        $sql .= "FROM cours AS c ";
        $sql .= "JOIN groupe_cours AS gc ON c.id = gc.cours_id ";
        $sql .= "JOIN groupe AS g ON gc.groupe_id = g.id ";
        $sql .= "JOIN salle_cours AS sc ON c.id = sc.cours_id ";
        $sql .= "JOIN salle AS s ON sc.salle_id = s.id ";


        if (preg_match('/([A-Z][0-9]{3})/', $nom_fichier, $matches)) {
            $identifiant = $matches[1];
            $sql .= "WHERE CONCAT(batiment,num) = :identifiant ";
        } else {
            $identifiant = $nom_fichier;
            $sql .= "WHERE g.nom = :identifiant ";
        }

        $sql .= "AND date_deb >= :lundi ";
        $sql .= "AND date_deb < :dimanche";
        
        $lundi = $this->getDeb_semaine()->format('Y-m-d');
        $dimanche = $this->getFin_semaine()->format('Y-m-d');

        $stmt = $pdo->prepare($sql);
        $stmt->execute([
            ':identifiant' => $identifiant,
            ':lundi' => $lundi,
            ':dimanche' => $dimanche
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