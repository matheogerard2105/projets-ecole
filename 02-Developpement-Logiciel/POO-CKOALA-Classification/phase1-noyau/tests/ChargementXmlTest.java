package tests;
import java.io.File;
import src.ChargeurXML;
import src.Typologie;
import src.Categorie;

/***************************************************************/
/* Test de la classe ChargeurXML : vérifie le chargement       */
/* et la construction initiale de la typologie.                */
/***************************************************************/
public class ChargementXmlTest {

    public static void main(String[] args) {
        System.out.println("--- Test de Chargement XML ---");

        testChargement("arbres.xml");
        System.out.println("------------------------------");
        testChargement("nuages.xml");
        System.out.println("------------------------------");
        testChargementFichierManquant("fichier_qui_n_existe_pas.xml"); // NOUVEL APPEL
    }

    private static void testChargement(String nomFichier) {
        ChargeurXML chargeur = new ChargeurXML();
        File fichier = new File("data/" + nomFichier);

        System.out.println("Tentative de chargement de : " + nomFichier);

        try {
            Typologie typologie = chargeur.charger(fichier);
            System.out.println("Succès du chargement de la typologie " + nomFichier + ".");

            // Affichage de la typologie pour vérification visuelle (style toString() du prof)
            System.out.println(typologie);

            // Vérification simple d'une catégorie (exemple basé sur l'arborescence attendue)
            Categorie catTop = typologie.getCategorie("TOP");
            if (catTop != null) {
                System.out.println("Vérification : La catégorie 'TOP' est présente.");
            } else {
                 System.err.println("Erreur : La catégorie 'TOP' est absente après chargement.");
            }

        } catch (RuntimeException e) {
            System.err.println("Échec du chargement de la typologie " + nomFichier + " : " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static void testChargementFichierManquant(String nomFichier) {
        ChargeurXML chargeur = new ChargeurXML();
        File fichier = new File("data/" + nomFichier);

        System.out.println("Tentative de chargement de fichier manquant : " + nomFichier);

        try {
            // L'appel déclenche une IOException dans ChargeurXML qui est wrapée en RuntimeException
            chargeur.charger(fichier);
            System.err.println("Échec: Le chargement a réussi pour un fichier inexistant.");
        } catch (RuntimeException e) {
            // Ceci couvre le catch(Exception e) dans ChargeurXML.java
            System.out.println("Succès: L'erreur de chargement (fichier I/O) a été capturée par le test.");
        }
    }
}
