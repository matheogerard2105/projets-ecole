package ihm;

import org.graphstream.graph.Graph;
import org.graphstream.graph.Node;
import org.graphstream.graph.implementations.SingleGraph;
import src.Categorie;
import src.Typologie;
import java.util.Set;

/**
 * Responsable de la création et de la mise à jour visuelle du graphe de typologie.
 */
public class VisualiseurGraphe {
    private Graph graphe;
    private final Typologie typologie;

    public VisualiseurGraphe(Typologie typologie) {
        this.typologie = typologie;
        // Obligatoire pour utiliser le moteur de rendu Swing de GraphStream 2.0
        System.setProperty("org.graphstream.ui", "swing");
        preparerGraphe();
    }

    /**
     * Construit les nœuds et les arêtes à partir de la typologie.
     */
    private void preparerGraphe() {
        graphe = new SingleGraph("Typologie");
        // Définition de la feuille de style CSS pour le graphe
        graphe.setAttribute("ui.stylesheet", 
            "node { size: 30px; fill-color: #777; text-size: 15px; }" +
            "node.compatible { fill-color: #2ecc71; size: 40px; }" +
            "edge { shape: cubic-curve; arrow-size: 10px, 5px; }");

        // Création des nœuds pour chaque catégorie
        for (Categorie cat : typologie.getCategories()) {
            Node n = graphe.addNode(cat.getNom());
            n.setAttribute("ui.label", cat.getNom());
        }

        // Création des liens de parenté (héritage)
        for (Categorie cat : typologie.getCategories()) {
            if (cat.getMere() != null) {
                graphe.addEdge(cat.getMere().getNom() + "-" + cat.getNom(), 
                             cat.getMere().getNom(), cat.getNom(), true);
            }
        }
    }

    /**
     * Change la classe CSS des nœuds compatibles pour les mettre en évidence.
     * @param nomsCompatibles Liste des noms de catégories résultant de la classification.
     */
    public void mettreAJourVisuels(Set<String> nomsCompatibles) {
        graphe.nodes().forEach(n -> 
            n.setAttribute("ui.class", nomsCompatibles.contains(n.getId()) ? "compatible" : ""));
    }
    
    /** @return L'objet GraphStream pour affichage. */
    public Graph getGraphe() { return graphe; }
}