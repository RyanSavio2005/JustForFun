package com.myapp;
import javax.swing.*;
public class Main {
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            try {
                UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
                new PDFEditor().setVisible(true);
            } catch (Exception e) {
                e.printStackTrace();
            }
        });
    }
}