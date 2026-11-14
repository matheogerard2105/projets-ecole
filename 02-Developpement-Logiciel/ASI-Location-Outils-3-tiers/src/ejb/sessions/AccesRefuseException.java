package ejb.sessions;

/** Exception levée lorsque l'accès est refusé. */
public class AccesRefuseException extends Exception {
    public AccesRefuseException(String message) {
        super(message);
    }
}