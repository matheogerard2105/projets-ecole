package tests;
import java.io.File;
import java.util.Set;
import src.ChargeurXML;
import src.Typologie;
import src.Observation;

/***************************************************************/
/* Test de la classification sur la typologie des arbres.      */
/***************************************************************/
public class ClassificationArbresTest {

    public static void main(String[] args) {
        System.out.println("--- Test de Classification des ARBRES ---");
        
        ChargeurXML chargeur = new ChargeurXML();
        Typologie typologie = null;

        try {
            typologie = chargeur.charger(new File("data/arbres.xml"));
            System.out.println("Typologie Arbres chargée.");
            
            // Observation 1 : Correspondante à l'exemple dans Main.java
            Observation o1 = new Observation();
            o1.ajouterObservation("forme", "conique");
            o1.ajouterObservation("taille du tronc", "1.0");
            o1.ajouterObservation("ecorce", "ecailles");
            o1.ajouterObservation("aiguilles", "brosse");
            testerObservation(typologie, o1, "Observation Conifère attendue (ex: Pin)");

            // Observation 2 : Une observation qui ne correspond à rien ou à une catégorie générale
            Observation o2 = new Observation();
            o2.ajouterObservation("couleur", "bleu"); // Caractéristique inconnue
            o2.ajouterObservation("forme", "globulaire");
            testerObservation(typologie, o2, "Observation ne correspondant à rien de spécifique");

            // Observation 3 : Une observation qui devrait correspondre à une catégorie Mère
            // (Nécessite de connaître la structure de arbres.xml)
            Observation o3 = Observation.creerExemple(); // Utilisation de la méthode exemple
            testerObservation(typologie, o3, "Observation d'exemple prédéfini (ex: Arbre Général)");

        } catch (RuntimeException e) {
            System.err.println("Échec de l'initialisation pour les tests d'arbres.");
            e.printStackTrace();
        }
    }

    private static void testerObservation(Typologie typologie, Observation observation, String description) {
        System.out.println("\n-> Cas de Test : " + description);
        System.out.println("   Observation : " + observation);
        
        Set<String> categories = typologie.classerObservation(observation);
        
        if (categories.isEmpty()) {
            System.out.println("Résultat : Aucune catégorie compatible.");
        } else {
            System.out.println("Résultat : Catégories compatibles : " + categories);
        }
    }
}