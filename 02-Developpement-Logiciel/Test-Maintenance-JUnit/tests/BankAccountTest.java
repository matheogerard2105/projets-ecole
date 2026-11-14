import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

public class BankAccountTest {

    private BankAccount accountTest = new BankAccount(100);
    @Test
    public void depositTest() {
        assertEquals(100, accountTest.getBalance());
        accountTest.deposit(50);
        assertEquals(150, accountTest.getBalance());
        // accountTest.deposit(-200); // This should throw an IllegalArgumentException
        // accountTest.withdraw(200); // This should throw an IllegalArgumentException
        assertThrows(IllegalStateException.class, () -> accountTest.withdraw(200));
        assertThrows(IllegalArgumentException.class, () -> accountTest.deposit(-200));
        assertThrows(IllegalArgumentException.class, () -> accountTest.withdraw(-200));

        }
    
}
