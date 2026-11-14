package ejb.entites;

import jakarta.persistence.Entity;

/** Equipement électrique. */
@Entity
public class EquipementElectrique extends Equipement {
    private boolean estFilaire;

    public EquipementElectrique() { super(); }
    public boolean isEstFilaire() { return estFilaire; }
    public void setEstFilaire(boolean estFilaire) { this.estFilaire = estFilaire; }
}