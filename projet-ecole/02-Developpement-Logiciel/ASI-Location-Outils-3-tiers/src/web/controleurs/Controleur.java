package web.controleurs;

import java.io.IOException;
import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.ejb.EJB;

import ejb.entites.EtatEmprunt;
import ejb.sessions.ServiceSolidarToolRemote;
import ejb.sessions.AccesRefuseException;
import ejb.sessions.ActionNonAutoriseeException;
import ejb.sessions.DateInvalideException;
import ejb.sessions.EmpruntInexistantException;
import ejb.sessions.ParticulierInexistantException;

@WebServlet("/Controleur")
public class Controleur extends HttpServlet {
    private static final long serialVersionUID = 1L;

    @EJB
    private ServiceSolidarToolRemote service; 

    // Servlet de contrôle pour la modification d'état des emprunts

    public Controleur() {
        super();
    }
    // Gère l'affichage du formulaire initial
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
    
        request.setAttribute("listeEtats", EtatEmprunt.values());
        
        String maVue = "/vueForm.jsp"; 
        request.getRequestDispatcher(maVue).forward(request, response);
    }

    // Gère la soumission du formulaire de modification d'état
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        
        String email = request.getParameter("email");
        String codeEmpruntStr = request.getParameter("codeEmprunt");
        String nouvelEtatStr = request.getParameter("newEtat");

        try {
            int codeEmprunt = Integer.parseInt(codeEmpruntStr);
            EtatEmprunt etatVise = EtatEmprunt.valueOf(nouvelEtatStr);

            service.modifierEtatEmprunt(email, codeEmprunt, etatVise);

            request.setAttribute("messageResultat", "L'opération a été réalisée avec succès.");

        } catch (NumberFormatException e) {
            request.setAttribute("messageResultat", "ERREUR : Le code emprunt doit être un nombre entier.");
        } catch (ParticulierInexistantException | EmpruntInexistantException e) {
            request.setAttribute("messageResultat", "ERREUR DE DONNÉES : " + e.getMessage());
        } catch (AccesRefuseException e) {
            request.setAttribute("messageResultat", "SÉCURITÉ : " + e.getMessage());
        } catch (ActionNonAutoriseeException e) {
            request.setAttribute("messageResultat", "ACTION REFUSÉE : " + e.getMessage());
        } catch (DateInvalideException e) {
            request.setAttribute("messageResultat", "PROBLÈME DE DATE : " + e.getMessage());
        } catch (Exception e) {
            request.setAttribute("messageResultat", "ERREUR SYSTÈME : " + e.getMessage());
            e.printStackTrace(); 
        }

        request.setAttribute("emailUtilisateur", email);
        request.setAttribute("numEmprunt", codeEmpruntStr);
        request.setAttribute("etatVise", nouvelEtatStr);

        request.getRequestDispatcher("/resultatForm.jsp").forward(request, response);
    }
}