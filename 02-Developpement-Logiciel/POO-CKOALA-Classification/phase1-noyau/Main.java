import java.io.File;
import src.*;

public class Main {
    public static void main(String[] args) {
        ChargeurXML chargeur = new ChargeurXML();
        Typologie typologie = chargeur.charger(new File("data/arbres.xml"));

        Observation o = new Observation();
        o.ajouterObservation("forme", "conique");
        o.ajouterObservation("taille du tronc", "1.0");
        o.ajouterObservation("ecorce", "ecailles");
        o.ajouterObservation("aiguilles", "brosse");

        System.out.println("Typologie chargée avec succès !");
        System.out.println("Observation : " + o);
        System.out.println("Catégories compatibles : " + typologie.classerObservation(o));
    }
}
