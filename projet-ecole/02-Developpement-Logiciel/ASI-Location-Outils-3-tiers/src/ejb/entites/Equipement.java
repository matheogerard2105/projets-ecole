package ejb.entites;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Collection;

/** Représente un équipement (entité JPA). */
@Entity
@Inheritance(strategy = InheritanceType.JOINED)
public abstract class Equipement implements Serializable {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int code;
    private String nom;
    private double valeur;

    @ManyToOne
    @JoinColumn(name = "categorie_id")
    private Categorie categorie;

    @ManyToOne
    @JoinColumn(name = "particulier_email")
    private Particulier proprietaire;

    @OneToMany(mappedBy = "equipement")
    private Collection<Emprunt> emprunts;

    public Equipement() {}

    public int getCode() { return this.code; }
    public String getNom() { return this.nom; }
    public double getValeur() { return this.valeur; }

    public void setCode(int newcode) { this.code = newcode; }
    public void setNom(String newnom) { this.nom = newnom; }
    public void setValeur(double newvaleur) { this.valeur = newvaleur; }

    public void setCategorie(Categorie categorie) { this.categorie = categorie; }
    public Categorie getCategorie() { return categorie; }

    public void setProprietaire(Particulier proprietaire) { this.proprietaire = proprietaire; }
    public Particulier getProprietaire() { return proprietaire; }
}