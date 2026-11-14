package client;




import javax.naming.InitialContext;
import javax.naming.NamingException;



public class Main2 {

  /**
   * Programme minimal d'exemple : accès au service distant.
   */
  public static void main(String[] args) {
    if (args.length != 3) {
      System.err.println("Erreur 3 paramètres attendus: email, no emprunt et nouvel état");
      return ;
    }
    try {
      // Crée le contexte JNDI (utilisé ici uniquement pour vérifier l'accès)
      new InitialContext();
      System.out.println("Accès au service distant");
    } catch (NamingException e1) {
      System.out.println(e1.getMessage());
    }
  }
}
