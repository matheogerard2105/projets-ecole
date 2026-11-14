package ejb.sessions;

/** Exception levée lorsqu'un équipement est introuvable. */
public class EquipementInexistantException extends Exception {
    public EquipementInexistantException() {
    }
    
    public EquipementInexistantException(String message) {
        super(message);
    }

}
