package src;

public class DomaineNumerique implements DomaineValeur<Double> {
    private final double inf, sup;

    public DomaineNumerique(double inf, double sup) {
        if (inf > sup){
            throw new IllegalArgumentException("Bornes invalides : inf > sup");
        }
        this.inf = inf; 
        this.sup = sup;
    }

    public double getInf() { 
        return inf; 
    }

    public double getSup() { 
        return sup;
    }

    @Override
    public boolean contient(Double v) { 
        return v != null && v >= inf && v <= sup; 
    }

    /***************************************************************************************/
    /* Vérifie si l'autre domaine est de type DomaineNumerique en utilisant un cast forcé. */                              
    /***************************************************************************************/
    @Override
    public boolean estDeMemeNature(DomaineValeur<?> autre) {
        try {
            // Si le cast réussit, 'autre' est bien de type DomaineNumerique
            DomaineNumerique d = (DomaineNumerique) autre;
            return true;
        } catch (ClassCastException e) {
            return false;
        }
    }
    
    /******************************************************************/
    /* Vérifie si ce domaine est un sous-ensemble du domaine 'autre'. */           
    /******************************************************************/ 
    @Override
    public boolean estSousEnsembleDe(DomaineValeur<?> autre) {
        try {
            // Tenter le cast vers le type attendu (DomaineNumerique)
            DomaineNumerique d = (DomaineNumerique) autre;
            
            // Si le cast réussit, vérifier la logique d'inclusion
            return this.inf >= d.inf && this.sup <= d.sup;
        } catch (ClassCastException e) {
            // Si le cast échoue (ce n'est pas un DomaineNumerique), alors ce n'est pas un sous-ensemble.
            return false;
        }
    }
    
    @Override
    public boolean estCompatible(String valeur) {
        if (valeur == null){
            return false;
        }
        try {
            double x = Double.parseDouble(valeur.trim().replace(',', '.'));
            return contient(x);
        } catch (NumberFormatException e) {
            return false;
        }
    }

    @Override
    public String toString() { 
        return "[" + inf + " ; " + sup + "]"; 
    }

}