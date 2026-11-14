package src;    
import java.util.Map;
import java.util.HashMap;
import java.util.Set;
import java.util.HashSet;
import java.util.Collections;

/*******************************************************************************/
/* Classe centrale gérant l'ensemble de la typologie CKOALA.                   */
/* Contient toutes les catégories et les fonctionnalités de classification.    */
/* Respecte l'Encapsulation et la Responsabilité Unique.                       */
 /******************************************************************************/
public class Typologie {
    
    // Constante pour le nom de la catégorie racine (bonne pratique : élimination du "Magic String")
    private static final String NOM_CATEGORIE_RACINE = "TOP"; 

    private final Map<String, Categorie> categories;

/* Constructeur. Initialise la Map des catégories. */
    public Typologie() { 
        this.categories = new HashMap<>(); 
    }

    /****************************************/
    /* Ajoute une catégorie à la typologie. */
    /* cat :  La catégorie à ajouter.       */
    /****************************************/ 
    public void ajouterCategorie(Categorie cat) {
        this.categories.put(cat.getNom(), cat);
    }

    public Categorie getCategorie(String nom) { 
        return categories.get(nom); 
    }
    
    /***************************************************/
    /* Retourne une vue non modifiable des catégories. */
    /* return La Map des catégories.                   */
    /***************************************************/ 

    public Map<String, Categorie> getCategories() {
        return Collections.unmodifiableMap(categories);
    }

    /********************************************************************************/
    /* Connecte chaque catégorie à sa mère.                                         */
    /* Cherche la catégorie mère par son nom et établit la référence Categorie mere.*/
    /********************************************************************************/ 
    public void construireHierarchie() {
        for (Categorie cat : categories.values()) {
            // Utilisation de la constante
            if (cat.getNomMere() != null && !NOM_CATEGORIE_RACINE.equals(cat.getNomMere())) {
                Categorie mere = categories.get(cat.getNomMere());
                if (mere != null) {
                    cat.setMere(mere);
                } else {
                    System.err.println("Erreur: Catégorie mère '" + cat.getNomMere() + "' non trouvée pour " + cat.getNom());
                }
            }
        }
    }

    /**********************************************************************************************/
    /* Vérifie la cohérence de toute la typologie après construction.                             */
    /* return true si toutes les catégories respectent la règle d'inclusion des domaines hérités. */
    /**********************************************************************************************/
    public boolean verifierCoherenceGlobale() {
        boolean estCoherent = true;
        for (Categorie cat : categories.values()) {
            if (!cat.verifierCoherenceHeritage()) {
                estCoherent = false;
            }
        }
        return estCoherent;
    }

    /*******************************************************************************************************/
    /* Classe une observation : renvoie les noms des catégories compatibles.                               */
    /* Règle : l'observation doit contenir au moins toutes les caractéristiques effectives de la catégorie,*/
    /* et chaque valeur doit appartenir au domaine requis.                                                 */
    /* @param observation L'observation à classer.                                                         */
    /* @return L'ensemble des noms des catégories compatibles.                                             */
    /*******************************************************************************************************/
    public Set<String> classerObservation(Observation observation) {
        Set<String> categoriesCompatibles = new HashSet<>();

        for (Categorie cat : categories.values()) {
            // Utilisation de la constante
            if (NOM_CATEGORIE_RACINE.equals(cat.getNom())) continue; // ignorer la racine nominale

            boolean compatible = true;
            Map<String, Caracteristique> caracsRequises = cat.getCaracteristiquesHeritees();

            for (Map.Entry<String, Caracteristique> entry : caracsRequises.entrySet()) {
                String intitule = entry.getKey();
                Caracteristique caracRequise = entry.getValue();

                String valeurObservee = observation.getValeur(intitule);
                
                if (valeurObservee == null || !caracRequise.getDomaine().estCompatible(valeurObservee)) {
                    compatible = false;
                    break;
                }
            }
            if (compatible) categoriesCompatibles.add(cat.getNom());
        }
        return categoriesCompatibles;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder("Typologie CKOALA:\n");
        for (Categorie cat : categories.values()) {
            sb.append("- ").append(cat.getNom());
            if (cat.getMere() != null) sb.append(" (Mère: ").append(cat.getMere().getNom()).append(")");
            else sb.append(" (Racine)");
            sb.append("\n");
            
            // Utilisation d'une lambda pour l'affichage des caractéristiques héritées
            cat.getCaracteristiquesHeritees().forEach((k, v) -> sb.append("  ").append(v).append("\n"));
        }
        return sb.toString();
    }
}