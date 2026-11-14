package ejb.sessions;

/** Exception levée lorsqu'une action n'est pas autorisée. */
public class ActionNonAutoriseeException extends Exception {
    public ActionNonAutoriseeException(String message) {
        super(message);
    }
}