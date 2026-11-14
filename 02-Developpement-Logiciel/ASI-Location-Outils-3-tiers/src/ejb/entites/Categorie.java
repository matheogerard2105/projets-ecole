package ejb.entites;

import jakarta.persistence.*;
import java.io.Serializable;

/** Catégorie d'équipement (entité JPA). */
@Entity
public class Categorie implements Serializable {

    private static final long serialVersionUID = 1L;

    // Identifiant auto-généré de la catégorie
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;
    private String nom;

    public Categorie() {}

    public Categorie(String nom) { this.nom = nom; }

    public int getId() { return id; }

    public String getNom() { return nom; }

    public void setNom(String nom) { this.nom = nom; }
}