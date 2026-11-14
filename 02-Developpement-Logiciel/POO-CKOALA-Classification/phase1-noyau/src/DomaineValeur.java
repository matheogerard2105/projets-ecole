package src;

public interface DomaineValeur<T> {
    
    boolean contient(T v);

    /**************************************************************************************************/
    /* Vérifie si le type de ce Domaine est compatible avec le type du domaine 'autre'.               */
    /* Par exemple, un DomaineNumerique doit renvoyer true si 'autre' est aussi un DomaineNumerique.  */
    /* C'est une vérification de la "nature" du domaine.                                              */
    /**************************************************************************************************/
    boolean estDeMemeNature(DomaineValeur<?> autre); 

    boolean estSousEnsembleDe(DomaineValeur<?> autre);

    default boolean estInclusDans(DomaineValeur<?> autre) {
        return estSousEnsembleDe(autre);
    }

    boolean estCompatible(String valeur);

    String toString();
}