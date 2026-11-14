import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

public class UserTest {
    @Test
    public void IsValidTest() {
        User user = new User("testuser", "password123");
        assertTrue(user.changePassword("password123", "password1234"));
        assertTrue(user.isValid(), "Username and password should be valid");

    }
    
}
