// InventoryManager.java
import java.util.HashMap;
import java.util.Map;

public class InventoryManager {

    private Map<String, Integer> stockLevels = new HashMap<>();
    private static final int REORDER_THRESHOLD = 5;

    public InventoryManager() {
        // Initial stock levels (could be read from a database in a real-world
        //    scenario)
        stockLevels.put("item1", 10);
        stockLevels.put("item2", 3);
        stockLevels.put("item3", 7);
    }

    // Adds stock to the inventory
    public void addStock(String item, int quantity) {
        if (quantity < 0) {
            System.out.println("Invalid quantity. Cannot add stock.");
            return;
        }
        int currentStock = stockLevels.getOrDefault(item, 0);
        stockLevels.put(item, currentStock + quantity);
    }
    public int getStock_Key(String item){
        return this.stockLevels.get(item);
    }

    // Reduces stock for a particular item
    public void removeStock(String item, int quantity) {
        if (!stockLevels.containsKey(item) || quantity < 0) {
            System.out.println("Invalid operation. Item not found or quantity invalid.");
            return;
        }
        int currentStock = stockLevels.get(item);
        if (currentStock < quantity) {
            System.out.println("Not enough stock to remove. Operation aborted.");
            return;
        }
        stockLevels.put(item, currentStock - quantity);
    }

    // Checks stock level for an item
    public boolean isStockLow(String item) {
        if (!stockLevels.containsKey(item)) {
            System.out.println("Item not found in stock.");
            return false;
        }
        return stockLevels.get(item) <= REORDER_THRESHOLD;
    }

    // Places an order for an item if stock is low
    public void placeOrderIfNeeded(String item) {
        if (isStockLow(item)) {
            System.out.println("Stock is low for " + item + ". Placing order.");
            // Simulate order placement
            addStock(item, 10); // Reorder quantity of 10
        }
    }

    // Displays current stock levels (for demonstration purposes)
    public void displayStock() {
        for (Map.Entry<String, Integer> entry : stockLevels.entrySet()) {
            System.out.println("Item: " + entry.getKey() + ", Stock: " +
            entry.getValue());
        }
    }
}