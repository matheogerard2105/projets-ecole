package ejb.sessions;

/** Exception levée lorsque la date fournie est invalide. */
public class DateInvalideException extends Exception {
    public DateInvalideException() {
    }
    
    public DateInvalideException(String message) {
        super(message);
    }

}
