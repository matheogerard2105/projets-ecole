package client;

import javax.naming.InitialContext;
import javax.naming.NamingException;
import ejb.sessions.ServiceSolidarToolRemote;
import ejb.entites.Equipement;
import java.util.Collection;
import java.sql.Date;

public class Main {
    /** Initialisation d'exemples de données via le service distant. */
    public static void main(String[] args) {
        try {
            InitialContext ctx = new InitialContext();
            System.out.println("Accès au service distant solidar_tool");

            String jndiName = "ejb:solidar_tool/solidar_toolSessions/ServiceSolidarToolBean!ejb.sessions.ServiceSolidarToolRemote";
            ServiceSolidarToolRemote proxy = (ServiceSolidarToolRemote) ctx.lookup(jndiName);

            // 1) Création de quelques particuliers
            System.out.println("\n[1/4] Création des particuliers...");
            proxy.creerParticulier("Bastien.Cazaux@polytech-lille.fr", "Polytech", 50.60773717826645, 3.1353520973453652);
            proxy.creerParticulier("Louis.Roussel@univ-lille.fr", "CRISTAL", 50.60709033783188, 3.13722964358617);
            proxy.creerParticulier("Olivier.Caron@univ-lille.fr", "Halle Vallin", 50.60993636922798, 3.1350302322755135);

            // 2) Ajout d'équipements proposés par ces particuliers
            System.out.println("[2/4] Ajout des équipements et attribution des +2 crédits...");
            proxy.proposerEquipement("Bastien.Cazaux@polytech-lille.fr", "vélo bleu ciel électrique", 2200.0, 1, true, false);
            proxy.proposerEquipement("Louis.Roussel@univ-lille.fr", "tondeuse électrique", 450.0, 3, true, true);
            proxy.proposerEquipement("Olivier.Caron@univ-lille.fr", "raquette orange", 120.0, 1, false, null);

            // 3) Recherche d'équipements proches d'un utilisateur (ici Louis)
            System.out.println("\n[3/4] Recherche d'équipements 'Sport' proches de Louis :");
            // Recherche dans un rayon donné (ici : 1)
            Collection<Equipement> proches = proxy.listerEquipementsProches("Louis.Roussel@univ-lille.fr", 1);

            // Récupération des codes (ID) pour créer des demandes d'emprunt
            int codeRaquette = -1;
            int codeVelo = -1;

            if (proches.isEmpty()) {
                System.out.println(" Aucun équipement trouvé à proximité.");
            } else {
                for (Equipement e : proches) {
                    System.out.println(" > ID: " + e.getCode() + " | Nom: " + e.getNom() + " | Valeur: " + e.getValeur() + "€");
                    if (e.getNom().contains("raquette")) codeRaquette = e.getCode();
                    if (e.getNom().contains("vélo")) codeVelo = e.getCode();
                }
            }

            // 4) Enregistrement des demandes d'emprunt
            System.out.println("\n[4/4] Enregistrement des demandes d'emprunts...");

            if (codeRaquette != -1) {
                // faireDemandeEmprunt(emailDemandeur, codeEquipement, dateDebut)
                proxy.faireDemandeEmprunt("Louis.Roussel@univ-lille.fr", codeRaquette, Date.valueOf("2026-04-15"));
                System.out.println(" - Demande créée : Louis -> Raquette Orange");
            }

            if (codeVelo != -1) {
                proxy.faireDemandeEmprunt("Olivier.Caron@univ-lille.fr", codeVelo, Date.valueOf("2026-04-20"));
                System.out.println(" - Demande créée : Olivier -> Vélo bleu ciel");
            }

            System.out.println("\n--- Initialisation de la base terminée avec succès ---");
            System.out.println("Base de données initialisée avec succès !");

        } catch (NamingException e1) {
            System.err.println(e1.getMessage());
        } catch (Exception e) {
            System.err.println("Erreur métier : " + e.getMessage());
            e.printStackTrace();
        }
    }
}