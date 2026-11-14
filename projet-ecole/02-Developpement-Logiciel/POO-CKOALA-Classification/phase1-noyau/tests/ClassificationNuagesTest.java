package tests;

import java.io.File;
import java.util.Set;
import src.ChargeurXML;
import src.Typologie;
import src.Observation;

/***************************************************************/
/* Test de la classification sur la typologie des nuages.      */
/***************************************************************/
public class ClassificationNuagesTest {

    public static void main(String[] args) {
        System.out.println("--- Test de Classification des NUAGES ---");

        ChargeurXML chargeur = new ChargeurXML();
        Typologie typologie = null;

        try {
            typologie = chargeur.charger(new File("data/nuages.xml"));
            System.out.println("Typologie Nuages chargée.");

            // Observation 1 : Un nuage de haute altitude (ex: Cirrus)
            Observation o1 = new Observation();
            o1.ajouterObservation("altitude", "10000.0"); // Doit être dans un DomaineNumerique
            o1.ajouterObservation("forme", "fibreuse");
            o1.ajouterObservation("couleur", "blanc");
            testerObservation(typologie, o1, "Observation Nuage Haute Altitude (ex: Cirrus)");

            // Observation 2 : Un nuage de basse altitude et de pluie (ex: Nimbostratus)
            Observation o2 = new Observation();
            o2.ajouterObservation("altitude", "500.0");
            o2.ajouterObservation("forme", "informe");
            o2.ajouterObservation("pluie", "oui");
            testerObservation(typologie, o2, "Observation Nuage de Pluie (ex: Nimbostratus)");

            // Observation 3 : Une observation avec une valeur en dehors des domaines
            Observation o3 = new Observation();
            o3.ajouterObservation("altitude", "15000.0"); // Trop haut?
            o3.ajouterObservation("forme", "rond");
            testerObservation(typologie, o3, "Observation en dehors des domaines valides");

            // Observation 4 : Une observation incomplète (cible le branche 'valeurObservee == null' dans Typologie)
            Observation o4 = new Observation();
            // Laisse "forme" ou "pluie" non observée, forçant la vérification NULL si la catégorie les requiert.
            o4.ajouterObservation("altitude", "8000.0");
            testerObservation(typologie, o4, "Observation Incomplète (carac. requise manquante)");

        } catch (RuntimeException e) {
            System.err.println("Échec de l'initialisation pour les tests de nuages.");
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
