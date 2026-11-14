package tests;

import src.Categorie;
import src.Caracteristique;
import src.DomaineNumerique;
import src.DomaineEnum;

/*****************************************************/
/* Test de l'héritage et de l'inclusion des domaines,*/
/* testé en mémoire pour une isolation complète.     */
/****************************************************/
public class HerediteInclusionTest {

    public static void main(String[] args) {
        System.out.println("--- Test d'Héritage et Cohérence des Domaines (Isolation) ---");
        
        testCasInclusionValide();
        System.out.println("-------------------------------------------------------------");
        testCasInclusionInvalide();
        System.out.println("-------------------------------------------------------------");
        testCasInclusionDifferenteNature();
        System.out.println("-------------------------------------------------------------");
        testCasNuagesEnumValide();
        System.out.println("-------------------------------------------------------------");
        testCasNuagesNumeriqueInvalide();
        System.out.println("-------------------------------------------------------------");
        testCasHeritageEcrasement();
        System.out.println("-------------------------------------------------------------");
        testCasMereAbsente();
    }

    /*****************************************************************************************************/
    /* Cas 1 : Domaine Fille est bien inclus dans le Domaine Mère (Numérique et Enum). (Succès attendu)  */
    /*****************************************************************************************************/
    private static void testCasInclusionValide() {
        System.out.println("Vérification 1 : Cas d'inclusion valide (Animal -> Mammifere).");

        // --- Mère (Plus général) ---
        Categorie mere = new Categorie("Animal", "TOP");
        // Taille (Mère) : [0.0 ; 100.0]
        DomaineNumerique dnMere = new DomaineNumerique(0.0, 100.0);
        mere.ajouterCaracteristique(new Caracteristique("taille", dnMere));
        // Poil (Mère) : {long, court, ras}
        DomaineEnum deMere = new DomaineEnum(java.util.Arrays.asList("long", "court", "ras"));
        mere.ajouterCaracteristique(new Caracteristique("poil", deMere));
        
        // --- Fille (Plus spécifique) ---
        Categorie fille = new Categorie("Mammifere", "Animal");
        // Taille (Fille) : [0.0 ; 10.0] -> INCLUS dans [0.0 ; 100.0]
        DomaineNumerique dnFille = new DomaineNumerique(0.0, 10.0);
        fille.ajouterCaracteristique(new Caracteristique("taille", dnFille));
        // Poil (Fille) : {long, court} -> INCLUS dans {long, court, ras}
        DomaineEnum deFille = new DomaineEnum(java.util.Arrays.asList("long", "court"));
        fille.ajouterCaracteristique(new Caracteristique("poil", deFille));

        // Construction du lien pour le test
        fille.setMere(mere);

        if (fille.verifierCoherenceHeritage()) {
            System.out.println("Succès : La cohérence d'héritage est OK.");
        } else {
            System.err.println("Échec : La cohérence d'héritage est FAUSSE (Erreur inattendue).");
        }
    }
    
    /**************************************************************************************************************************/
    /* Cas 2 : Domaine Fille n'est PAS inclus dans le Domaine Mère (Numérique, borne supérieure trop haute). (Échec attendu)  */
    /**************************************************************************************************************************/
    private static void testCasInclusionInvalide() {
        System.out.println("Vérification 2 : Cas d'inclusion invalide (Oiseau -> Passereau).");

        // --- Mère (Plus général) ---
        Categorie mere = new Categorie("Oiseau", "TOP");
        // Envergure (Mère) : [0.1 ; 5.0]
        DomaineNumerique dnMere = new DomaineNumerique(0.1, 5.0);
        mere.ajouterCaracteristique(new Caracteristique("envergure", dnMere));
        
        // --- Fille (Plus spécifique) ---
        Categorie fille = new Categorie("Passereau", "Oiseau");
        // Envergure (Fille) : [4.0 ; 10.0] -> NON INCLUS (10.0 > 5.0)
        DomaineNumerique dnFille = new DomaineNumerique(4.0, 10.0);
        fille.ajouterCaracteristique(new Caracteristique("envergure", dnFille));

        // Construction du lien
        fille.setMere(mere);

        if (!fille.verifierCoherenceHeritage()) {
            System.out.println("Succès : L'incohérence d'héritage a été DÉTECTÉE.");
        } else {
            System.err.println("Échec : L'incohérence n'a PAS été détectée (Résultat FAUX).");
        }
    }
    
    /***************************************************************************************************************/
    /* Cas 3 : La fille tente d'écraser un DomaineNumérique avec un DomaineEnum. (Échec attendu, nature différente)*/
    /***************************************************************************************************************/
    private static void testCasInclusionDifferenteNature() {
        System.out.println("Vérification 3 : Cas d'écrasement avec domaine de nature différente.");

        // --- Mère ---
        Categorie mere = new Categorie("Plante", "TOP");
        // Hauteur (Mère) : [0.0 ; 10.0] (Numérique)
        DomaineNumerique dnMere = new DomaineNumerique(0.0, 10.0);
        mere.ajouterCaracteristique(new Caracteristique("hauteur", dnMere));
        
        // --- Fille ---
        Categorie fille = new Categorie("Fleur", "Plante");
        // Hauteur (Fille) : {bas, moyen, haut} (Énumération)
        DomaineEnum deFille = new DomaineEnum(java.util.Arrays.asList("bas", "moyen", "haut"));
        fille.ajouterCaracteristique(new Caracteristique("hauteur", deFille));

        // Construction du lien
        fille.setMere(mere);

        if (!fille.verifierCoherenceHeritage()) {
             System.out.println("Succès : L'incohérence (nature différente) a été DÉTECTÉE.");
        } else {
            System.err.println("Échec : La vérification est passée (Résultat FAUX).");
        }
    }
    
    /*****************************************************************************************************/
    /* Cas 4 : Domaine Fille est bien inclus dans le Domaine Mère (Nuages, Enum). (Succès attendu)       */
    /* Teste l'inclusion dans un domaine Enum (carac 'forme').                                           */
    /*****************************************************************************************************/
    private static void testCasNuagesEnumValide() {
        System.out.println("Vérification 4 : Cas d'inclusion valide (Nuage Haut -> Cirrus).");

        // --- Mère (Nuage Haut) ---
        Categorie mere = new Categorie("NuageHaut", "TOP");
        // Forme (Mère) : {fibreuse, lamellaire, cirriforme}
        DomaineEnum deMere = new DomaineEnum(java.util.Arrays.asList("fibreuse", "lamellaire", "cirriforme", "globulaire"));
        mere.ajouterCaracteristique(new Caracteristique("forme", deMere));
        
        // --- Fille (Cirrus) ---
        Categorie fille = new Categorie("Cirrus", "NuageHaut");
        // Forme (Fille) : {fibreuse, cirriforme} -> INCLUS
        DomaineEnum deFille = new DomaineEnum(java.util.Arrays.asList("fibreuse", "cirriforme"));
        fille.ajouterCaracteristique(new Caracteristique("forme", deFille));

        // Construction du lien
        fille.setMere(mere);

        if (fille.verifierCoherenceHeritage()) {
            System.out.println("Succès : La cohérence d'héritage (Enum) est OK.");
        } else {
            System.err.println("Échec : La cohérence d'héritage (Enum) est FAUSSE (Erreur inattendue).");
        }
    }
    
    /*****************************************************************************************************/
    /* Cas 5 : Domaine Fille n'est PAS inclus dans le Domaine Mère (Nuages, Numérique). (Échec attendu)  */
    /* Teste l'inclusion dans un domaine Numérique (carac 'altitude').                                   */
    /*****************************************************************************************************/
    private static void testCasNuagesNumeriqueInvalide() {
        System.out.println("Vérification 5 : Cas d'inclusion invalide (Nuage Haut, trop bas).");

        // --- Mère (Nuage Haut) ---
        Categorie mere = new Categorie("NuageHaut", "TOP");
        // Altitude (Mère) : [6000.0 ; 13000.0]
        DomaineNumerique dnMere = new DomaineNumerique(6000.0, 13000.0);
        mere.ajouterCaracteristique(new Caracteristique("altitude", dnMere));
        
        // --- Fille (Cirrus) ---
        Categorie fille = new Categorie("Cirrus", "NuageHaut");
        // Altitude (Fille) : [5000.0 ; 12000.0] -> NON INCLUS (5000.0 < 6000.0)
        DomaineNumerique dnFille = new DomaineNumerique(5000.0, 12000.0);
        fille.ajouterCaracteristique(new Caracteristique("altitude", dnFille));

        // Construction du lien
        fille.setMere(mere);

        if (!fille.verifierCoherenceHeritage()) {
            System.out.println("Succès : L'incohérence d'héritage (Altitude min. trop basse) a été DÉTECTÉE.");
        } else {
            System.err.println("Échec : L'incohérence n'a PAS été détectée (Résultat FAUX).");
        }
    }
    /*****************************************************************************************************/
    /* Cas 6 : Test de l'héritage par écrasement des caractéristiques (couvre putIfAbsent).             */
    /*****************************************************************************************************/
    private static void testCasHeritageEcrasement() {
        System.out.println("Vérification 6 : Test d'héritage par écrasement.");

        // --- Grand-Mère ---
        Categorie gm = new Categorie("GM", "TOP");
        DomaineNumerique dnGM = new DomaineNumerique(0.0, 100.0);
        gm.ajouterCaracteristique(new Caracteristique("taille", dnGM)); // taille = [0, 100]

        // --- Mère ---
        Categorie mere = new Categorie("Mere", "GM");
        mere.setMere(gm);
        // Ajout d'une nouvelle carac non définie chez GM
        DomaineEnum deMere = new DomaineEnum(java.util.Arrays.asList("vert", "bleu"));
        mere.ajouterCaracteristique(new Caracteristique("couleur", deMere));
        // Écrase 'taille' avec une borne inférieure plus élevée (valide)
        DomaineNumerique dnMere = new DomaineNumerique(10.0, 90.0);
        mere.ajouterCaracteristique(new Caracteristique("taille", dnMere)); // taille = [10, 90]

        // --- Fille ---
        Categorie fille = new Categorie("Fille", "Mere");
        fille.setMere(mere);

        // Caractéristiques héritées de la Fille
        java.util.Map<String, Caracteristique> heritees = fille.getCaracteristiquesHeritees();

        // Vérification de la taille (doit être l'écrasement de la Mère : [10, 90])
        double tailleInf = ((DomaineNumerique) heritees.get("taille").getDomaine()).getInf();

        if (heritees.size() == 2 && tailleInf == 10.0) {
            System.out.println("Succès : L'héritage par écrasement et l'ajout de carac ont fonctionné. (Taille min: " + tailleInf + ")");
        } else {
            System.err.println("Échec : Le nombre de caractéristiques héritées ou la valeur écrasée est incorrecte.");
        }
    }

    /*****************************************************************************************************/
    /* Cas 7 : Test de l'absence de la catégorie mère (couvre System.err.println dans Typologie).        */
    /*****************************************************************************************************/
    private static void testCasMereAbsente() {
        System.out.println("Vérification 7 : Test de Mère absente (simule Typologie.construireHierarchie).");

        // Création d'une catégorie qui référence une mère "Inexistante"
        Categorie fille = new Categorie("Orphelin", "Inexistante");
        // On ne peut pas tester directement l'absence car setMere est appelé dans Typologie.construireHierarchie
        // L'important est que l'absence de 'mere' ne cause pas d'erreur lors de l'appel à getCaracteristiquesHeritees()
        // ou verifierCoherenceHeritage() lorsque 'mere' est null.

        // L'absence de setMere(mere) pour une mère inexistante fait que mere reste null.
        if (fille.getMere() == null && fille.verifierCoherenceHeritage()) {
             System.out.println("Succès : L'absence de mère (null) est gérée correctement.");
        } else {
             System.err.println("Échec : La gestion de mere=null est incorrecte.");
        }
    }
}
