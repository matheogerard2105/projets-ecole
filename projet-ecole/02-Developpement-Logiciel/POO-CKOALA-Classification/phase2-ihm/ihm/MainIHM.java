package ihm;

import javax.swing.SwingUtilities;


public class MainIHM {
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            new CkoalaApp();
        });
    }
}