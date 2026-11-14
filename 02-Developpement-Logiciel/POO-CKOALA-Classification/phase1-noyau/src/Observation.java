package src;
import java.util.Map;
import java.util.HashMap;
import java.util.Collections; // Ajout pour l'encapsulation

/**************************************************************************************************/
/* Représente une observation concrète réalisée sur un objet (ex: un arbre, un nuage).            */
/* Stocke les valeurs observées sous forme de paires (Intitulé de Caractéristique, Valeur String).*/
/**************************************************************************************************/
public class Observation {
    // Clé: intitulé de la caractéristique (String), Valeur: valeur observée (stockée en String pour flexibilité)
    private final Map<String, String> valeursObservees;

    /****************************************************************/
    /* Constructeur par défaut. Initialise la Map des observations. */
    /****************************************************************/
    public Observation() {
        this.valeursObservees = new HashMap<>();
    }

    /****************************************************************/
    /* Ajoute ou met à jour une observation.                        */
    /* intitule : L'intitulé de la caractéristique observée.        */
    /* valeur : La valeur observée (stockée en String).             */
    /****************************************************************/
    public void ajouterObservation(String intitule, String valeur) {
        if (intitule == null || valeur == null) {
            System.err.println("Avertissement: Tentative d'ajouter une observation avec une clé ou valeur nulle.");
            return ;
        }
        this.valeursObservees.put(intitule, valeur);
    }

    /*******************************************************************************************/
    /* Récupère la valeur observée pour un intitulé donné.                                     */
    /* intitule : L'intitulé de la caractéristique recherchée.                                 */
    /* return La valeur observée sous forme de String, ou null si l'observation n'existe pas.  */
    /*******************************************************************************************/
    public String getValeur(String intitule) {
        return valeursObservees.get(intitule);
    }

    /******************************************************************************/
    /* Retourne toutes les observations.                                          */
    /* return Une Map non modifiable des observations (Encapsulation respectée).  */
    /******************************************************************************/
    public Map<String,String> toutes() { 
        return Collections.unmodifiableMap(valeursObservees); 
    }

    // Exemple rapide
    public static Observation creerExemple() {
        Observation obs = new Observation();
        obs.ajouterObservation("forme", "conique");
        obs.ajouterObservation("taille du tronc", "2.4");
        obs.ajouterObservation("taille", "13.0");
        obs.ajouterObservation("ecorce", "lisse");
        return obs;
    }

    @Override
    public String toString() { return valeursObservees.toString(); }
}
