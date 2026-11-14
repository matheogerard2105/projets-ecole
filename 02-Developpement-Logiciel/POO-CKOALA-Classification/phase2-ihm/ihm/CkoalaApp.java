package ihm;

import javax.swing.*;
import java.awt.*;
import java.io.File;
import src.Typologie;

/**********************************************************************/
/* Fenêtre principale de l'application.                               */
/* Gère le chargement des typologies et l'affichage des panneaux.     */
/**********************************************************************/
public class CkoalaApp extends JFrame {
    // Constantes de dimensions pour la fenêtre
    private static final int LARGEUR_DEFAUT = 1000;
    private static final int HAUTEUR_DEFAUT = 700;
    
    private Typologie typologie; // noyau fonctionnel
    private PanneauClassification panneauClassification; // panneau qui s'affichera
    public CkoalaApp() {
        setTitle("CKOALA - Assistant de Classification");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        creerBarreMenu();
        // Message d'accueil avant chargement
        add(new JLabel("Veuillez charger une typologie via le menu 'Fichier'.", SwingConstants.CENTER), BorderLayout.CENTER);
        
        setSize(LARGEUR_DEFAUT, HAUTEUR_DEFAUT);
        setLocationRelativeTo(null); // Centrage sur l'écran
        setVisible(true);
    }
    
    //Construit le menu pour le chargement de fichiers. */
    private void creerBarreMenu() {
        JMenuBar barreMenu = new JMenuBar();
        JMenu menuFichier = new JMenu("Fichier");
        JMenuItem itemCharger = new JMenuItem("Charger Typologie XML...");
        
        itemCharger.addActionListener(e -> chargerTypologie());
        menuFichier.add(itemCharger);
        barreMenu.add(menuFichier);
        setJMenuBar(barreMenu);
    }
    
    /**
     * Ouvre une boîte de dialogue pour sélectionner un fichier XML.
     * En cas d'erreur de chargement (XML mal formé, etc.), une alerte est affichée[cite: 235, 243, 249].
     */
    private void chargerTypologie() {
        JFileChooser selecteurFichier = new JFileChooser(new File(".")); 
        if (selecteurFichier.showOpenDialog(this) == JFileChooser.APPROVE_OPTION) {
            File fichier = selecteurFichier.getSelectedFile();
            try {
                // Création et chargement de la typologie via le noyau
                Typologie nouvelleTypologie = new Typologie(fichier.getName().replace(".xml", "")); 
                nouvelleTypologie.chargerDepuisXML(fichier.getAbsolutePath());
                
                this.typologie = nouvelleTypologie;
                
                // Remplacement de l'interface d'accueil par l'interface de classification
                getContentPane().removeAll();
                panneauClassification = new PanneauClassification(typologie);
                add(panneauClassification, BorderLayout.CENTER);
                
                setTitle("CKOALA - " + typologie.getNom() + " chargé.");
                revalidate();
                repaint();
                
            } catch (Exception ex) {
                // Affichage d'un message d'erreur clair à l'utilisateur [cite: 181, 186]
                JOptionPane.showMessageDialog(this, 
                    "Erreur lors du chargement du fichier XML : " + ex.getMessage(), 
                    "Erreur de Chargement", 
                    JOptionPane.ERROR_MESSAGE);
            }
        }
    }
}