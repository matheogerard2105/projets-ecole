package src;
import java.util.*;

public class DomaineEnum implements DomaineValeur<String> {
    private final Set<String> symboles;

    public DomaineEnum(Collection<String> symboles) {
        if (symboles == null || symboles.isEmpty())
            throw new IllegalArgumentException("Erreur: Le domaine énumératif ne peut pas être vide.");
        this.symboles = new HashSet<>(symboles);
    }

    public Collection<String> getSymboles() { 
        return Collections.unmodifiableSet(symboles); 
    }

    @Override
    public boolean contient(String v) { 
        return v != null && symboles.contains(v); 
    }

    /*********************************************************************************/
    /* Vérifie si l'autre domaine est de type DomaineEnum en utilisant le try/catch. */
    /* (Implémentation requise par l'interface)                                      */
    /*********************************************************************************/
    @Override
    public boolean estDeMemeNature(DomaineValeur<?> autre) {
        try {
            // Si le cast réussit, 'autre' est de la même nature
            DomaineEnum d = (DomaineEnum) autre;
            return true;
        } catch (ClassCastException e) {
            return false;
        }
    }

    @Override
    public boolean estSousEnsembleDe(DomaineValeur<?> autre) {
        try {
            DomaineEnum d = (DomaineEnum) autre;
            // Vérifie si TOUS les symboles de ce domaine (fille) sont présents dans l'autre (mère).
            return d.symboles.containsAll(this.symboles);
        } catch (ClassCastException e) {
            return false;
        }
    }

    @Override
    public boolean estCompatible(String valeur) { 
        return contient(valeur); 
    }

    @Override
    public String toString() { 
         return symboles.toString(); 
    }
}