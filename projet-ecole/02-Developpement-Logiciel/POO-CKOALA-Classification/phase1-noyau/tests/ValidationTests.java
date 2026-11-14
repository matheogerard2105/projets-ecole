package tests;

import src.Categorie;
import src.DomaineEnum;
import src.DomaineNumerique;
import src.Observation;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;

/************************************************************/
/* Teste les validations (constructeurs, nullité) des objets */
/* pour couvrir tous les chemins d'exceptions.              */
/************************************************************/
public class ValidationTests {

    public static void main(String[] args) {
        System.out.println("--- Test des Validations et Exceptions ---");
        testCategorieExceptions();
        testDomaineNumeriqueExceptions();
        testDomaineEnumExceptions();
        testObservationNulls();
    }

    // Teste la validation du constructeur de Categorie
    private static void testCategorieExceptions() {
        System.out.println("\n-> Test Categorie (nom invalide)");
        try {
            new Categorie(null, "Mère");
            System.err.println("Échec: Exception non levée pour nom null.");
        } catch (IllegalArgumentException e) {
            System.out.println("Succès: Exception levée pour nom null. Msg: " + e.getMessage());
        }

        try {
            new Categorie(" ", "Mère");
            System.err.println("Échec: Exception non levée pour nom vide.");
        } catch (IllegalArgumentException e) {
            System.out.println("Succès: Exception levée pour nom vide. Msg: " + e.getMessage());
        }
    }
    // Teste la validation du constructeur de DomaineNumerique et les cas limites
    private static void testDomaineNumeriqueExceptions() {
        System.out.println("\n-> Test DomaineNumerique (bornes invalides & limites)");

        // ... (Test inf > sup existant) ...
        try {
            // inf > sup doit lancer une exception
            new DomaineNumerique(10.0, 5.0);
            System.err.println("Échec: Exception non levée pour inf > sup.");
        } catch (IllegalArgumentException e) {
            System.out.println("Succès: Exception levée pour inf > sup. Msg: " + e.getMessage());
        }

        // --- Tests des cas limites et de format ---
        DomaineNumerique dn = new DomaineNumerique(5.0, 10.0);

        // 1. Tests de nullité/format invalide (existants)
        if (!dn.contient(null)) {
            System.out.println("Succès: contient(null) retourne false.");
        }
        if (!dn.estCompatible(null)) {
            System.out.println("Succès: estCompatible(null) retourne false.");
        }
        if (!dn.estCompatible("pas_un_nombre")) {
            System.out.println("Succès: estCompatible(String non numérique) retourne false.");
        }

        // 2. Tests des limites (Boundary conditions)
        if (dn.contient(5.0) && dn.contient(10.0)) { // Bornes incluses (v >= inf && v <= sup)
             System.out.println("Succès: Bornes 5.0 et 10.0 sont incluses.");
        }
        if (!dn.contient(4.999) && !dn.contient(10.001)) { // Valeurs juste à l'extérieur
             System.out.println("Succès: Valeurs 4.999 et 10.001 sont exclues.");
        }

        // 3. Test de compatibilité format (couvre le replace(',', '.'))
        if (dn.estCompatible("7,5")) {
            System.out.println("Succès: estCompatible(7,5) est inclus.");
        } else {
             System.err.println("Échec: estCompatible(7,5) est exclu (problème de format).");
        }
    }

// ... (reste des méthodes existantes) ...
    // Teste la validation du constructeur de DomaineEnum
    private static void testDomaineEnumExceptions() {
        System.out.println("\n-> Test DomaineEnum (symboles vides)");
        try {
            // Liste vide doit lancer une exception
            new DomaineEnum(new ArrayList<>());
            System.err.println("Échec: Exception non levée pour symboles vides.");
        } catch (IllegalArgumentException e) {
            System.out.println("Succès: Exception levée pour symboles vides. Msg: " + e.getMessage());
        }

        try {
            // Liste null doit lancer une exception
            new DomaineEnum(null);
            System.err.println("Échec: Exception non levée pour symboles null.");
        } catch (IllegalArgumentException e) {
            System.out.println("Succès: Exception levée pour symboles null. Msg: " + e.getMessage());
        }

        // Couvre le cas de nullité dans contient()
        DomaineEnum de = new DomaineEnum(Arrays.asList("A", "B"));
        if (!de.contient(null)) {
            System.out.println("Succès: contient(null) retourne false.");
        }
    }

    // Teste la gestion des nulls dans Observation
    private static void testObservationNulls() {
        System.out.println("\n-> Test Observation (ajout de null)");
        Observation o = new Observation();

        // Ces appels couvrent les instructions System.err.println et le 'return' dans ajouterObservation
        o.ajouterObservation(null, "valeur");
        o.ajouterObservation("intitule", null);
        o.ajouterObservation(null, null);

        System.out.println("Succès: ajoutObservation avec null a été exécuté (vérifier System.err).");

        // Couvre également la ligne de garde dans Categorie.ajouterCaracteristique(null)
        Categorie cat = new Categorie("Test", "TOP");
        cat.ajouterCaracteristique(null);
        System.out.println("Succès: Categorie.ajouterCaracteristique(null) a été exécuté.");
    }
}
