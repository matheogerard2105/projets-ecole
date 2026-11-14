package src;
import javax.xml.parsers.*;
import org.w3c.dom.*;
import java.io.File;
import java.util.*;

/**************************************************************************************/
/* Classe ChargeurXML                                                                 */
/* ------------------                                                                 */
/* Permet de charger un fichier XML (ex: arbres.xml ou nuages.xml)                    */
/* et de construire en mémoire la typologie correspondante :                          */
/* - les catégories                                                                   */
/* - les caractéristiques et leurs domaines de valeurs                                */
/*                                                                                    */
/* Cette classe repose sur le modèle DOM (Document Object Model).                     */
/* Elle respecte la séparation des préoccupations : elle ne fait que le parsing XML.  */
/**************************************************************************************/
public class ChargeurXML {
    
    // Constante pour le nom de la catégorie racine (bonne pratique : élimination du "Magic String")
    private static final String NOM_CATEGORIE_RACINE = "TOP"; // Respecte MAJUSCULES_AVEC_UNDERSCORES

    /************************************************************************/
    /* Charge une typologie complète depuis un fichier XML.                 */
    /* @param fichier le fichier XML contenant la hiérarchie de catégories. */
    /* @return un objet Typologie entièrement construit.                    */
    /************************************************************************/
    public Typologie charger(File fichier) {
        try {
            // 1. Configuration du parseur DOM
            DocumentBuilderFactory fabrique = DocumentBuilderFactory.newInstance();
            // Pour être plus robuste : ignorer les commentaires et espaces (bonne pratique).
            fabrique.setIgnoringComments(true);
            DocumentBuilder constructeur = fabrique.newDocumentBuilder();

            // 2. Lecture et normalisation du document
            Document doc = constructeur.parse(fichier);
            doc.getDocumentElement().normalize();

            // 3. Création de la typologie vide
            Typologie typologie = new Typologie();

            // 4. Lecture des balises <categorie>
            NodeList listeCategories = doc.getElementsByTagName("categorie");

            for (int i = 0; i < listeCategories.getLength(); i++) {
                Element eCat = (Element) listeCategories.item(i);

                String nom = getText(eCat, "nom");
                String nomMere = getOptionalText(eCat, "mere");
                
                // Convention : Utilisation de la constante
                if (nomMere == null || nomMere.equalsIgnoreCase(NOM_CATEGORIE_RACINE)) {
                    nomMere = NOM_CATEGORIE_RACINE; 
                }

                // Création de l'objet catégorie
                Categorie categorie = new Categorie(nom, nomMere);

                // Lecture des caractéristiques
                NodeList listeCaracs = eCat.getElementsByTagName("caracteristique");
                for (int j = 0; j < listeCaracs.getLength(); j++) {
                    Element eCar = (Element) listeCaracs.item(j);
                    String intitule = getText(eCar, "intitule");

                    DomaineValeur<?> domaine;

                    // --- Cas 1 : ensemble de valeurs discrètes (DomaineEnum) ---
                    if (eCar.getElementsByTagName("ensemble").getLength() > 0) {
                        Element ensemble = (Element) eCar.getElementsByTagName("ensemble").item(0);
                        NodeList elements = ensemble.getElementsByTagName("element");

                        List<String> symboles = new ArrayList<>();
                        for (int k = 0; k < elements.getLength(); k++) {
                            Node node = elements.item(k);
                            // S'assurer que le noeud est bien un élément (bonne pratique)
                            if (node.getNodeType() == Node.ELEMENT_NODE) {
                                symboles.add(node.getTextContent().trim());
                            }
                        }
                        if (symboles.isEmpty()) { 
                            throw new IllegalArgumentException("Erreur: La balise <ensemble> est vide pour la caractéristique : " + intitule);
                        }
                        domaine = new DomaineEnum(symboles);
                    }
                    // --- Cas 2 : intervalle numérique (DomaineNumerique) ---
                    else if (eCar.getElementsByTagName("intervalle").getLength() > 0) {
                        Element intervalle = (Element) eCar.getElementsByTagName("intervalle").item(0);
                        
                        // Utilisation de la méthode utilitaire pour extraire les bornes
                        double inf = Double.parseDouble(getText(intervalle, "inf"));
                        double sup = Double.parseDouble(getText(intervalle, "sup"));
                        domaine = new DomaineNumerique(inf, sup);
                    }
                    else {
                        throw new IllegalArgumentException("Erreur: Caractéristique '" + intitule + "' sans domaine de valeurs (<ensemble> ou <intervalle>) spécifié.");
                    }

                    // Création et ajout de la caractéristique
                    Caracteristique carac = new Caracteristique(intitule, domaine);
                    categorie.ajouterCaracteristique(carac);
                }

                // Ajout de la catégorie dans la typologie
                typologie.ajouterCategorie(categorie);
            }

            // 5. Construction de la hiérarchie (liens mère/fille)
            typologie.construireHierarchie();

            // 6. Vérification de cohérence globale
            if (!typologie.verifierCoherenceGlobale()) {
                System.err.println("Vérification terminée : incohérence(s) détectée(s) dans la typologie. Voir les détails ci-dessus.");
            }

            return typologie;
        }
        // Gestion des exceptions (Messages d’erreur clairs & Gestion correcte)
        catch (ParserConfigurationException e) {
            throw new RuntimeException("Erreur de configuration: Problème de configuration du parseur DOM.", e);
        }
        catch (Exception e) {
            // Gestion générique pour SAXException (lecture du fichier), IOException, NumberFormatException...
            throw new RuntimeException("Erreur critique lors du chargement du fichier XML " + fichier.getName() + " : " + e.getMessage(), e);
        }
    }

    // ---------------------------------------------------------------------
    // Méthodes utilitaires
    // ---------------------------------------------------------------------

    /****************************************************************/
    /* Récupère le texte d’un élément XML obligatoire.              */
    /* @param parent L'élément parent.                              */
    /* @param tag Le nom de la balise obligatoire.                  */
    /* @return Le contenu texte de la balise.                       */
    /* @throws IllegalArgumentException si la balise est manquante. */
    /****************************************************************/
    private static String getText(Element parent, String tag) {
        NodeList list = parent.getElementsByTagName(tag);
        if (list.getLength() == 0) {
            throw new IllegalArgumentException("Erreur XML : Balise <" + tag + "> manquante dans l'élément <" + parent.getTagName() + ">");
        }
        return list.item(0).getTextContent().trim();
    }

    /****************************************************/
    /* Récupère le texte d’un élément XML optionnel.    */
    /* Renvoie null si la balise n’existe pas.          */
    /* @param parent L'élément parent.                  */
    /* @param tag Le nom de la balise optionnelle.      */
    /* @return Le contenu texte de la balise ou null.   */
    /****************************************************/
    
    private static String getOptionalText(Element parent, String tag) {
        NodeList list = parent.getElementsByTagName(tag);
        // Utilisation du ternaire pour la concision (style du prof)
        return (list.getLength() == 0) ? null : list.item(0).getTextContent().trim();
    }
}