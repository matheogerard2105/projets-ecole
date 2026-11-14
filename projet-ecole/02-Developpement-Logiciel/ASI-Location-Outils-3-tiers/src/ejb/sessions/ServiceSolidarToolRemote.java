package ejb.sessions;

import java.util.Collection;
import java.util.Date;

import ejb.entites.*;
import jakarta.ejb.Remote;

/** Remote API du service SolidarTool. */
@Remote
public interface ServiceSolidarToolRemote extends ServiceSolidarTool {
    void creerParticulier(String email, String adresse, double latitude, double longitude) 
        throws ParticulierDejaCreeException ;

    Collection<Categorie> listerCategories();

    void proposerEquipement(String emailProprietaire, String nom, double valeur, int idCategorie, boolean estElectrique, Boolean estFilaire) 
        throws ParticulierInexistantException, CategorieInexistanteException, AccesRefuseException;

    Collection<Equipement> listerEquipementsProches(String emailDemandeur, int idCategorie) 
        throws ParticulierInexistantException, CategorieInexistanteException;
        
    void faireDemandeEmprunt(String emailEmprunteur, int codeEquipement, Date date) 
        throws ParticulierInexistantException, EquipementInexistantException, DateInvalideException, AccesRefuseException;

    void finaliserEmprunt(String emailDemandeur, int codeEmprunt) 
        throws ParticulierInexistantException, EmpruntInexistantException, AccesRefuseException;
}
