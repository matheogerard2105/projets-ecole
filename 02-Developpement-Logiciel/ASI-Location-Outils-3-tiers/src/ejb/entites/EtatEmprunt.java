package ejb.entites;

/** États possibles d'un emprunt. */
public enum EtatEmprunt {
    DEMANDE_EMPRUNT ("Demande emprunt"),
    DEMANDE_REFUSEE ("Demande refusée"),
    DEMANDE_ACCEPTEE ("Demande acceptée"),
    EQUIPEMENT_EMPRUNTE ("Equipement emprunté"),
    EQUIPEMENT_RETOURNE ("Equipement retourné");
    private String label;
    EtatEmprunt(String label) { this.label = label; }
    @Override
    public String toString() { return label; }
}
