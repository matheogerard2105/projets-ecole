package ejb.sessions;

/** Exception levée lorsqu'un particulier existe déjà. */
public class ParticulierDejaCreeException extends Exception {

    public ParticulierDejaCreeException() {
    }

    public ParticulierDejaCreeException(String message) {
        super(message);
    }

}
