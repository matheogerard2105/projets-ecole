import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

public class InventoryManagerTest {
    InventoryManager inventoryManager = new InventoryManager();
    

    @Test
    
    public void addStockTest() {
        inventoryManager.addStock("item1", 10);
        assertEquals(10, inventoryManager.getStock_Key("item1"));
        inventoryManager.addStock("item1", 5);
        assertEquals(15, inventoryManager.getStock_Key("item2"));
    }
    
    public void removeStockTest() {
        inventoryManager.addStock("item1", 10);
        inventoryManager.removeStock("item1", 5);
        assertEquals(5, inventoryManager.getStock_Key("item1"));
        inventoryManager.removeStock("item1", 10);
        assertEquals(0, inventoryManager.getStock_Key("item1"));
    }
    public void isStockLow() {
        inventoryManager.addStock("item1", 5);
        assertFalse(inventoryManager.isStockLow("item1"));
        inventoryManager.removeStock("item1", 5);
        assertTrue(inventoryManager.isStockLow("item1"));
    }
    
}
