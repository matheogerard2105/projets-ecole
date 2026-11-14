package src;

/***************************************************************************************************/
/* Représente une propriété mesurable dans une typologie (ex: 'forme', 'taille du tronc').         */
/* Chaque caractéristique est associée à un domaine de valeurs qui définit les valeurs acceptables.*/
/* Conception : Respecte l'Encapsulation (champs privés et finaux) et la Responsabilité Unique.    */
/***************************************************************************************************/
public class Caracteristique {
    // Le nom unique de la caractéristique (ex: "ecorce", "altitude").
    private final String intitule; 
    
    // Le domaine de valeurs possible pour cette caractéristique (DomaineNumerique ou DomaineEnum).
    private final DomaineValeur<?> domaine;

    /************************************************************************************/
    /* Constructeur.                                                                    */
    /* intitule : Le nom explicite et significatif de la caractéristique.               */
    /* domaine : Le domaine de valeurs qui limite les observations acceptables.         */
    /************************************************************************************/
    public Caracteristique(String intitule, DomaineValeur<?> domaine) {
        // vérification basique de nullité, si l'intitulé est essentiel.
        if (intitule == null || intitule.trim().isEmpty()) {
            throw new IllegalArgumentException("L'intitulé de la caractéristique ne doit pas être vide.");
        }
        this.intitule = intitule;
        this.domaine = domaine;
    }

    /**********************************************/
    /* Retourne l'intitulé de la caractéristique. */
    /* return Le nom de la caractéristique.       */
    /**********************************************/
    public String getIntitule() { 
        return intitule; 
    }
    
    /**********************************************************************/
    /* Retourne le domaine de valeurs associé à cette caractéristique.    */
    /* return Le DomaineValeur (DomaineNumerique ou DomaineEnum).         */
    /**********************************************************************/
    public DomaineValeur<?> getDomaine() { 
        return domaine; 
    }

    /*************************************************************************************************/
    /* Fournit une description lisible de la caractéristique et de son domaine.                      */
    /* return L'intitulé suivi de la description du domaine (ex: "altitude : [6000.0 ; 13000.0]").   */
    /*************************************************************************************************/
    @Override
    public String toString() {
        return intitule + " : " + domaine.toString();
    }
}