package ejb.entites ;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Collection;

/** Particulier (utilisateur) du système. */
@Entity
public class Particulier implements Serializable {
    @Id private String email;
    private String adresse;
    private double latitude;
    private double longitude;
    private int credits;

    @OneToMany(mappedBy = "proprietaire")
    private Collection<Equipement> mesEquipements;

    @OneToMany(mappedBy = "emprunteur")
    private Collection<Emprunt> mesDemandes;

    public Particulier() {}

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public String getAdresse() { return adresse; }
    public void setAdresse(String adresse) { this.adresse = adresse; }
    public Double getLatitude() { return latitude; }
    public void setLatitude(Double latitude) { this.latitude = latitude; }
    public Double getLongitude() { return longitude; }
    public void setLongitude(Double longitude) { this.longitude = longitude; }
    public int getCredits() { return credits; }
    public void setCredits(int credits) { this.credits = credits; }

    public Collection<Equipement> getMesEquipements() { return mesEquipements; }
    public void setMesEquipements(Collection<Equipement> mesEquipements) { this.mesEquipements = mesEquipements; }

    public Collection<Emprunt> getMesDemandes() { return mesDemandes; }
    public void setMesDemandes(Collection<Emprunt> mesDemandes) { this.mesDemandes = mesDemandes; }

}
