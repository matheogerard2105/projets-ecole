package ejb.sessions;

/** Exception levée lorsqu'un emprunt n'existe pas. */
public class EmpruntInexistantException extends Exception {
    public EmpruntInexistantException() {
    }
    
    public EmpruntInexistantException(String message) {
        super(message);
    }

}
