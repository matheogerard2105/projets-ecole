package ejb.sessions;

/** Exception levée lorsqu'un particulier est introuvable. */
public class ParticulierInexistantException extends Exception {
    public ParticulierInexistantException() {
    }
        
    public ParticulierInexistantException(String message) {
        super(message);
    }
}
