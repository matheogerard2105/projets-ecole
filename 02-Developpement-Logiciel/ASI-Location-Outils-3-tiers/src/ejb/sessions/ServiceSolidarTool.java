package ejb.sessions;
import ejb.entites.*;

/** Interface des opérations du service SolidarTool. */
public interface ServiceSolidarTool {

    void modifierEtatEmprunt(String emailDemandeur, int codeEmprunt, EtatEmprunt nouvelEtat) 
        throws ParticulierInexistantException, EmpruntInexistantException, DateInvalideException, AccesRefuseException, ActionNonAutoriseeException;
}