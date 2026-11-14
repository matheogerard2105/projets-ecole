package src;
import java.util.Map;
import java.util.HashMap;
import java.util.Collections;

/***************************************************************************************/
/* Représente une catégorie dans la typologie hiérarchique (ex: 'Conifère', 'Cirrus'). */
/* Gère les caractéristiques définies localement et l'héritage de la hiérarchie mère.  */
/* Respecte l'Encapsulation, le Nommage et la Responsabilité Unique.                   */
/***************************************************************************************/
public class Categorie {
    private final String nom;     // Nom unique de la catégorie (String).
    private final String nomMere; // Nom de la catégorie mère (String), 'TOP' pour la racine.
    private Categorie mere;       // Référence vers l'objet Categorie mère pour la traversée de l'arbre.
    private final Map<String, Caracteristique> caracteristiques; // Caractéristiques définies LOCALEMENT (non héritées), indexées par intitulé.

    /*************************************************/
    /* Constructeur.                                 */
    /* nom : Le nom unique de la catégorie.          */
    /* nomMere : Le nom de sa catégorie mère.        */
    /*************************************************/
    public Categorie(String nom, String nomMere) {
        if (nom == null || nom.trim().isEmpty()) {
            throw new IllegalArgumentException("Le nom de la catégorie ne doit pas être vide.");
        }
        this.nom = nom;
        this.nomMere = nomMere;
        this.caracteristiques = new HashMap<>();
    }

    public String getNom() { 
        return nom; 
    }

    public String getNomMere() { 
        return nomMere; 
    }

    public Categorie getMere() { 
        return mere; 
    }
    
    /******************************************************************************************/
    /* Définit la référence vers l'objet mère. Utilisé par Typologie.construireHierarchie().  */
    /* mere : La référence vers la catégorie mère.                                            */
    /******************************************************************************************/
    public void setMere(Categorie mere) { 
        this.mere = mere; 
    }

    /******************************************************************************************/
    /* Ajoute une caractéristique définie localement à cette catégorie.                       */
    /* carac : La caractéristique à ajouter.                                                  */
    /******************************************************************************************/
    public void ajouterCaracteristique(Caracteristique carac) {
        // Évite l'effet de bord: l'appelant fournit l'objet Caracteristique, la Map interne est modifiée.
        if (carac != null) {
             this.caracteristiques.put(carac.getIntitule(), carac);
        }
    }

    /******************************************************************************************/
    /* Retourne la Map des caractéristiques définies localement.                              */
    /* return Une vue non modifiable des caractéristiques LOCALES (Encapsulation respectée).  */
    /******************************************************************************************/
    public Map<String, Caracteristique> getCaracteristiques() {
        return Collections.unmodifiableMap(caracteristiques);
    }

    /*****************************************************************************************************/
    /* Vérifie si les domaines des caractéristiques définies localement sont                             */
    /* inclus dans les domaines des caractéristiques héritées de la mère.                                */
    /* return true si la règle de cohérence (domaine fille inclus dans domaine mère)                     */
    /* est respectée, false sinon.                                                                       */
    /*****************************************************************************************************/
    public boolean verifierCoherenceHeritage() {
        if (mere == null || "TOP".equalsIgnoreCase(nomMere)) {
            // La catégorie TOP ou une catégorie sans mère n'a rien à vérifier.
            return true;
        }
        
        // Obtient TOUTES les caractéristiques effectives de la MÈRE (héritées + locales de la mère)
        Map<String, Caracteristique> caracsMeres = mere.getCaracteristiquesHeritees();

        // Parcourir UNIQUEMENT les caractéristiques définies LOCALEMENT (celles qui écrasent potentiellement)
        for (Map.Entry<String, Caracteristique> entry : caracteristiques.entrySet()) {
            String intitule = entry.getKey();
            Caracteristique caracFille = entry.getValue();

            // S'assurer que la caractéristique existe chez la mère ou ses ancêtres
            if (caracsMeres.containsKey(intitule)) {
                Caracteristique caracMere = caracsMeres.get(intitule);
                
                // Si le domaine de la fille n'est pas inclus dans le domaine de la mère, il y a incohérence.
                if (!caracFille.getDomaine().estInclusDans(caracMere.getDomaine())) {
                    System.err.println("ERREUR d'HÉRITAGE pour " + nom + " (" + intitule + ") : domaine fille non inclus dans celui de la mère.");
                    return false;
                }
            }
            // Si la caractéristique est définie localement mais n'existe pas chez la mère ou les ancêtres,
            // elle est considérée comme une nouvelle caractéristique et n'est pas sujette à cette vérification.
        }
        return true;
    }

    /*******************************************************************************************************/
    /* Calcule l'ensemble des caractéristiques effectives pour cette catégorie (héritage par écrasement).  */
    /* @return Une Map contenant toutes les caractéristiques effectives (locales + héritées).              */
    /*******************************************************************************************************/
    public Map<String, Caracteristique> getCaracteristiquesHeritees() {
        // 1. Démarrer avec les caractéristiques locales (elles sont prioritaires)
        Map<String, Caracteristique> caracs = new HashMap<>(this.caracteristiques);
        Categorie current = this.mere;
        
        // 2. Remonter dans la hiérarchie pour ajouter les caractéristiques non définies localement
        while (current != null) {
            // Ajouter les caracs de l'ancêtre SEULEMENT si elles ne sont PAS déjà dans 'caracs' (putIfAbsent)
            // Évite l'effet de bord: crée une nouvelle Map à chaque appel.
            current.caracteristiques.forEach(caracs::putIfAbsent);
            current = current.mere;
        }

        // Retourner la Map contenant les caractéristiques effectives.
        // NOTE : On ne retourne pas Collections.unmodifiableMap ici car cette Map est souvent utilisée
        // pour la lecture seule (classement), mais les implémentations précédentes du prof la retournaient 
        // comme une nouvelle Map modifiable pour la simplicité (car elle est jetable après utilisation).
        // Si elle doit être modifiable par la suite, le retour d'un nouvel HashMap est la bonne pratique OCP.
        return caracs;
    }
}