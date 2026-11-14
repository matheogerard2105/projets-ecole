package ejb.sessions;

/** Exception levée lorsqu'une catégorie demandée est introuvable. */
public class CategorieInexistanteException extends Exception {
    public CategorieInexistanteException() {
    }

    public CategorieInexistanteException(String message) {
        super(message);
    }

}
