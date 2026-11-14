package ejb.sessions;

import jakarta.ejb.Stateless;
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import ejb.entites.*;
import java.util.Collection;
import java.util.Date;

/** Implémentation EJB du service SolidarTool (opérations métier). */
@Stateless
public class ServiceSolidarToolBean implements ServiceSolidarToolLocal, ServiceSolidarToolRemote {

    @PersistenceContext(unitName="solidar_tool")
    private EntityManager em;

    @Override
    public void creerParticulier(String email, String adresse, double latitude, double longitude) {
        Particulier p = new Particulier();
        p.setEmail(email);
        p.setAdresse(adresse);
        p.setLatitude(latitude);
        p.setLongitude(longitude);
        p.setCredits(50); 
        em.persist(p);
    }

    @Override
    public Collection<Categorie> listerCategories() {
        return em.createQuery("SELECT c FROM Categorie c", Categorie.class).getResultList();
    }

    @Override
    public void proposerEquipement(String emailProprietaire, String nom, double valeur, int idCategorie, boolean estElectrique, Boolean estFilaire) 
            throws ParticulierInexistantException, CategorieInexistanteException, AccesRefuseException {

        Particulier p = em.find(Particulier.class, emailProprietaire);
        if (p == null) throw new ParticulierInexistantException(); 
        
        Categorie c = em.find(Categorie.class, idCategorie);
        if (c == null) throw new CategorieInexistanteException();

        Equipement e;

        if (estElectrique) {
            EquipementElectrique ee = new EquipementElectrique();
            ee.setEstFilaire(estFilaire);
            e = ee;
        } else {
            e = new EquipementNonElectrique();
        }

        e.setNom(nom);
        e.setValeur(valeur);
        e.setCategorie(c);
        e.setProprietaire(p);

        p.setCredits(p.getCredits() + 2);

        em.persist(e);
    }

    @Override
    public Collection<Equipement> listerEquipementsProches(String emailDemandeur, int idCategorie) 
        throws ParticulierInexistantException, CategorieInexistanteException {

        Particulier demandeur = em.find(Particulier.class, emailDemandeur);
        Collection<Equipement> tous = em.createQuery("SELECT e FROM Equipement e WHERE e.categorie.id = :catId AND e.proprietaire.email != :email", Equipement.class)
        .setParameter("catId", idCategorie)
        .setParameter("email", emailDemandeur)
        .getResultList();

        return tous.stream().filter(e -> Utils.calculerDistance(demandeur.getLatitude(), demandeur.getLongitude(), e.getProprietaire().getLatitude(), e.getProprietaire().getLongitude()) <= 5.0).collect(java.util.stream.Collectors.toList());
    }

    @Override
    public void faireDemandeEmprunt(String emailEmprunteur, int codeEquipement, Date date) 
            throws ParticulierInexistantException, EquipementInexistantException, DateInvalideException, AccesRefuseException {
        Particulier emprunteur = em.find(Particulier.class, emailEmprunteur);
        Equipement equip = em.find(Equipement.class, codeEquipement);

        if (emprunteur == null) throw new ParticulierInexistantException();
        if (equip == null) throw new EquipementInexistantException();

        Emprunt emp = new Emprunt();
        emp.setEmprunteur(emprunteur);
        emp.setEquipement(equip);
        emp.setDateEmprunt(date);
        emp.setEtat(EtatEmprunt.DEMANDE_EMPRUNT);

        em.persist(emp);
    }

    @Override
    public void modifierEtatEmprunt(String emailDemandeur, int codeEmprunt, EtatEmprunt nouvelEtat) 
            throws ParticulierInexistantException, EmpruntInexistantException, 
                DateInvalideException, AccesRefuseException, ActionNonAutoriseeException {

        Emprunt emp = em.find(Emprunt.class, codeEmprunt);
        if (emp == null) throw new EmpruntInexistantException("Emprunt n°" + codeEmprunt + " inconnu.");

        Particulier loueur = emp.getEquipement().getProprietaire();
        Particulier emprunteur = emp.getEmprunteur();

        if (!emailDemandeur.equals(loueur.getEmail())) {
            throw new AccesRefuseException("Seul le loueur peut modifier l'état de cet emprunt.");
        }

        if (nouvelEtat == EtatEmprunt.EQUIPEMENT_RETOURNE && emp.getEtat() != EtatEmprunt.EQUIPEMENT_EMPRUNTE) {
            throw new ActionNonAutoriseeException("Impossible de marquer comme retourné : l'objet n'est pas encore déclaré comme emprunté.");
        }

        java.sql.Date de = new java.sql.Date(emp.getDateEmprunt().getTime());
        java.sql.Date dj = Utils.today;

        if (nouvelEtat == EtatEmprunt.DEMANDE_ACCEPTEE) {
            if (!Utils.isBefore(dj, de)) throw new DateInvalideException("Date dépassée.");
            loueur.setCredits(loueur.getCredits() - 1);
            emp.setEtat(nouvelEtat);
        } 
        else if (nouvelEtat == EtatEmprunt.EQUIPEMENT_EMPRUNTE) {
            if (!Utils.isEqual(dj, de)) throw new DateInvalideException("Le retrait se fait le jour J.");
            loueur.setCredits(loueur.getCredits() + 2);
            emp.setEtat(nouvelEtat);
        } 
        else if (nouvelEtat == EtatEmprunt.EQUIPEMENT_RETOURNE) {
            emprunteur.setCredits(emprunteur.getCredits() + 1);
            emp.setEtat(nouvelEtat);
            this.finaliserEmprunt(emailDemandeur, codeEmprunt);
        }
        
        else if (nouvelEtat == EtatEmprunt.DEMANDE_REFUSEE) {
            if (!Utils.isBefore(dj, de)) {
                throw new DateInvalideException("Impossible de refuser : la date est déjà passée.");
            }
            emp.setEtat(nouvelEtat);
        }      
        else {
            throw new RuntimeException("Transition d'état non gérée.");
        }
    }

    @Override
    public void finaliserEmprunt(String emailDemandeur, int codeEmprunt) 
            throws ParticulierInexistantException, EmpruntInexistantException, AccesRefuseException {
        
        // 1. Recherche de l'emprunt
        Emprunt emp = em.find(Emprunt.class, codeEmprunt);
        if (emp == null) {
            throw new EmpruntInexistantException("L'emprunt n°" + codeEmprunt + " n'existe pas.");
        }

        Particulier loueur = emp.getEquipement().getProprietaire();
        if (!loueur.getEmail().equals(emailDemandeur)) {
            throw new AccesRefuseException("Sécurité : L'utilisateur " + emailDemandeur 
                + " n'est pas le propriétaire de l'objet et ne peut pas finaliser cet emprunt.");
        }

        if (emp.getEtat() == EtatEmprunt.EQUIPEMENT_RETOURNE) {
            Particulier emprunteur = emp.getEmprunteur();
            Equipement eq = emp.getEquipement();
            
            int cout = 2; // Base
            if (eq.getValeur() > 100) cout++;
            if (eq instanceof EquipementElectrique) {
                cout++;
                if (!((EquipementElectrique) eq).isEstFilaire()) cout++;
            }
            
            emprunteur.setCredits(Math.max(0, emprunteur.getCredits() - cout));
            System.out.println("[FINALISATION] Coût de " + cout + " appliqué à " + emprunteur.getEmail());
        }

        em.remove(emp);
        System.out.println("[FINALISATION] Emprunt " + codeEmprunt + " supprimé.");
    }
}