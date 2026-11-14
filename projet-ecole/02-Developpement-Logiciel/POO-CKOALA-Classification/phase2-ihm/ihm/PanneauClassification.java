package ihm;

import javax.swing.*;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;
import java.awt.*;
import java.util.*;
import java.util.List;
import src.*;
import org.graphstream.ui.swing_viewer.DefaultView;
import org.graphstream.ui.swing_viewer.SwingViewer;
import org.graphstream.ui.view.Viewer;

/**********************************************************************/
/* Interface permettant de traiter les différents                     */
/* types de champs de manière uniforme                 */
/**********************************************************************/
interface ComposantSaisie {
    /** @return La valeur saisie ou sélectionnée sous forme de chaîne. */
    String getValeur();
    /** @return Le composant Swing réel pour l'affichage. */
    JComponent getComposantGraphique();
}
/**********************************************************************/
/* Panneau principal gérant la saisie des caractéristiques, le calcul */
/* de compatibilité et l'affichage du graphe.                         */
/**********************************************************************/
public class PanneauClassification extends JPanel {
    
    // Constantes de mise en forme pour éviter les "Magic numbers" [cite: 42, 46, 49]
    private static final int ESPACEMENT_H = 10;
    private static final int ESPACEMENT_V = 5;
    private static final int HAUTEUR_GRAPHE = 400;
    private static final double POIDS_RESULTATS = 0.3;
    private static final double POIDS_PRINCIPAL = 0.4;
    private static final int COLONNES_TEXTE = 10;

    private final Typologie typologie;
    private final Map<String, ComposantSaisie> composantsEntree;
    private final Map<String, DomaineValeurs> toutesCaracteristiques;
    
    private JTextArea zoneResultat;
    private VisualiseurGraphe visualiseurGraphe;

    public PanneauClassification(Typologie typologie) {
        this.typologie = typologie;
        this.composantsEntree = new HashMap<>();
        this.toutesCaracteristiques = new TreeMap<>();
        
        // Initialisation des données
        collecterToutesCaracteristiques();

        setLayout(new BorderLayout(ESPACEMENT_H, ESPACEMENT_H));
        
        // --- Zone de gauche : Formulaire de saisie ---
        JPanel panneauGauche = new JPanel(new BorderLayout());
        JPanel conteneurEntree = new JPanel(new GridLayout(0, 2, ESPACEMENT_H, ESPACEMENT_V));
        construireChampsEntree(conteneurEntree); 
        panneauGauche.add(new JScrollPane(conteneurEntree), BorderLayout.CENTER);
        
        // --- Zone de droite : Résultats textuels ---
        zoneResultat = new JTextArea("Sélectionnez les caractéristiques pour classer.");
        zoneResultat.setEditable(false);
        zoneResultat.setBorder(BorderFactory.createTitledBorder("Résultats"));
        
        // --- Zone de droite : Rendu GraphStream ---
        JPanel panneauGraphe = new JPanel(new BorderLayout());
        panneauGraphe.setBorder(BorderFactory.createTitledBorder("Vue Hiérarchique"));
        panneauGraphe.setPreferredSize(new Dimension(0, HAUTEUR_GRAPHE));
        
        this.visualiseurGraphe = new VisualiseurGraphe(typologie);
        configurerGraphStream(panneauGraphe);

        // Organisation spatiale via des séparateurs redimensionnables
        JSplitPane separationDroite = new JSplitPane(JSplitPane.VERTICAL_SPLIT, new JScrollPane(zoneResultat), panneauGraphe);
        separationDroite.setResizeWeight(POIDS_RESULTATS);
        
        JSplitPane separationPrincipale = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, panneauGauche, separationDroite);
        separationPrincipale.setResizeWeight(POIDS_PRINCIPAL);
        
        add(separationPrincipale, BorderLayout.CENTER);
        
        // Premier calcul pour initialiser l'affichage
        classifier();
    }

    /**
     * Configure le moteur de rendu de GraphStream pour l'intégrer dans Swing.
     */
    private void configurerGraphStream(JPanel conteneur) {
        SwingViewer visionneuse = new SwingViewer(visualiseurGraphe.getGraphe(), Viewer.ThreadingModel.GRAPH_IN_GUI_THREAD);
        visionneuse.enableAutoLayout();
        DefaultView vue = (DefaultView) visionneuse.addDefaultView(false);
        conteneur.add(vue, BorderLayout.CENTER);
    }

    /**
     * Ecouteur interne pour déclencher la classification en temps réel
     * dès qu'un champ texte est modifié.
     */
    private class EcouteurClassification implements DocumentListener {
        @Override public void insertUpdate(DocumentEvent e) { classifier(); }
        @Override public void removeUpdate(DocumentEvent e) { classifier(); }
        @Override public void changedUpdate(DocumentEvent e) { classifier(); }
    }

    /**
     * Récupère les saisies, interroge le noyau fonctionnel et met à jour l'IHM.
     * Utilise des exceptions pour gérer les erreurs de saisie utilisateur[cite: 174, 180, 243].
     */
    private void classifier() {
        Observation observation = new Observation();
        try {
            // Parcours générique des composants sans test de type (pas de instanceof) [cite: 144, 170]
            for (Map.Entry<String, ComposantSaisie> entree : composantsEntree.entrySet()) {
                String nom = entree.getKey();
                String val = entree.getValue().getValeur().trim();
                
                if (val.isEmpty()) continue;

                // Conversion selon le type de domaine (Numérique vs Symbolique)
                if (toutesCaracteristiques.get(nom).isIntervalle()) {
                    observation.ajouter(nom, Double.parseDouble(val.replace(',', '.')));
                } else {
                    observation.ajouter(nom, val);
                }
            }
            
            // Appel au noyau fonctionnel
            List<Categorie> compatibles = typologie.classifier(observation);
            Set<String> nomsCompatibles = new HashSet<>();
            for (Categorie c : compatibles) nomsCompatibles.add(c.getNom());
            
            // Mise à jour visuelle du graphe et du texte
            visualiseurGraphe.mettreAJourVisuels(nomsCompatibles);
            
            if (compatibles.isEmpty()) {
                zoneResultat.setText("Aucune catégorie compatible.");
            } else {
                StringBuilder sb = new StringBuilder("Compatibles :\n");
                compatibles.forEach(c -> sb.append(" - ").append(c.getNom()).append("\n"));
                zoneResultat.setText(sb.toString());
            }
        } catch (NumberFormatException e) {
            // Message d'erreur spécifique en cas de mauvaise saisie numérique [cite: 181, 248, 251]
            zoneResultat.setText("Erreur : Veuillez entrer un nombre valide pour les caractéristiques numériques.");
        } catch (Exception e) {
            zoneResultat.setText("Saisie incomplète.");
        }
    }

    /**
     * Agrège toutes les caractéristiques de la typologie pour créer le formulaire.
     */
    private void collecterToutesCaracteristiques() {
        Map<String, Set<String>> symbolesAggreges = new HashMap<>();
        for (Categorie cat : typologie.getCategories()) {
            Map<String, DomaineValeurs> caracsHeredite = cat.getToutesLesCaracteristiques();
            for (Map.Entry<String, DomaineValeurs> entree : caracsHeredite.entrySet()) {
                String nom = entree.getKey();
                DomaineValeurs domaine = entree.getValue();
                if (domaine.isIntervalle()) {
                    if (!toutesCaracteristiques.containsKey(nom)) toutesCaracteristiques.put(nom, domaine);
                } else {
                    symbolesAggreges.putIfAbsent(nom, new TreeSet<>());
                    symbolesAggreges.get(nom).addAll(domaine.getElements());
                }
            }
        }
        symbolesAggreges.forEach((nom, elements) -> 
            toutesCaracteristiques.put(nom, new DomaineValeurs(elements)));
    }

    /**
     * Instancie les composants Swing selon le type de données (Intervalle -> JTextField, Choix -> JComboBox).
     */
    private void construireChampsEntree(JPanel conteneur) {
        for (String nomCarac : toutesCaracteristiques.keySet()) {
            DomaineValeurs domaine = toutesCaracteristiques.get(nomCarac);
            conteneur.add(new JLabel((domaine.isIntervalle() ? "" : "🔘 ") + nomCarac + " :"));

            if (domaine.isIntervalle()) {
                // Cas d'une valeur numérique
                final JTextField champ = new JTextField(COLONNES_TEXTE);
                champ.getDocument().addDocumentListener(new EcouteurClassification());
                composantsEntree.put(nomCarac, new ComposantSaisie() {
                    public String getValeur() { return champ.getText(); }
                    public JComponent getComposantGraphique() { return champ; }
                });
                conteneur.add(champ);
            } else {
                // Cas d'un choix prédéfini
                DefaultComboBoxModel<String> modele = new DefaultComboBoxModel<>();
                modele.addElement(""); // Option vide par défaut
                domaine.getElements().forEach(modele::addElement);
                final JComboBox<String> combo = new JComboBox<>(modele);
                combo.addActionListener(e -> classifier());
                composantsEntree.put(nomCarac, new ComposantSaisie() {
                    public String getValeur() { return (String) combo.getSelectedItem(); }
                    public JComponent getComposantGraphique() { return combo; }
                });
                conteneur.add(combo);
            }
        }
    }
}