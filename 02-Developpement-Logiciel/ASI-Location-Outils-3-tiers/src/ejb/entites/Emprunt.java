package ejb.entites;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Date;

/** Emprunt d'équipement (entité JPA). */
@Entity
public class Emprunt implements Serializable {

    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;

    @Temporal(TemporalType.DATE)
    private Date dateEmprunt;

    @Enumerated(EnumType.STRING)
    private EtatEmprunt etat;

    @ManyToOne
    @JoinColumn(name = "equipement_code")
    private Equipement equipement;

    @ManyToOne
    @JoinColumn(name = "emprunteur_email")
    private Particulier emprunteur;

    public Emprunt() {}

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public Date getDateEmprunt() { return dateEmprunt; }
    public void setDateEmprunt(Date dateEmprunt) { this.dateEmprunt = dateEmprunt; }

    public EtatEmprunt getEtat() { return etat; }
    public void setEtat(EtatEmprunt etat) { this.etat = etat; }

    public Equipement getEquipement() { return equipement; }
    public void setEquipement(Equipement equipement) { this.equipement = equipement; }

    public Particulier getEmprunteur() { return emprunteur; }
    public void setEmprunteur(Particulier emprunteur) { this.emprunteur = emprunteur; }
}
