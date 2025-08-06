package com.myapp;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.rendering.PDFRenderer;

public class PDFEditor extends JFrame {
    private JLabel statusLabel;
    private File currentFile;
    private JPanel thumbnailPanel;
    private JPanel pdfPanel;
    private JScrollPane pdfScrollPane;
    private JScrollPane thumbnailScrollPane;
    private double zoomFactor = 1.0;
    private List<BufferedImage> pdfPages = new ArrayList<>();

    public PDFEditor() {
        initializeUI();
    }

    private void initializeUI() {
        setTitle("PDF Editor");
        setSize(1000, 700);
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        JPanel mainPanel = new JPanel(new BorderLayout());
        JToolBar toolBar = new JToolBar();

        JButton openButton = new JButton("Open PDF");
        openButton.addActionListener(this::openFile);

        JButton saveButton = new JButton("Save PDF");
        saveButton.addActionListener(this::saveFile);

        JButton removePageButton = new JButton("Remove Page");
        removePageButton.addActionListener(this::removePage);

        JButton rotateButton = new JButton("Rotate");
        rotateButton.addActionListener(this::rotatePdf);

        JButton zoomInButton = new JButton("Zoom In");
        zoomInButton.addActionListener(e -> zoom(1.25));

        JButton zoomOutButton = new JButton("Zoom Out");
        zoomOutButton.addActionListener(e -> zoom(0.8));

        toolBar.add(openButton);
        toolBar.add(saveButton);
        toolBar.addSeparator();
        toolBar.add(removePageButton);
        toolBar.add(rotateButton);
        toolBar.add(zoomInButton);
        toolBar.add(zoomOutButton);

        statusLabel = new JLabel("No file loaded");
        JPanel statusPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        statusPanel.add(statusLabel);

        pdfPanel = new JPanel();
        pdfPanel.setLayout(new BoxLayout(pdfPanel, BoxLayout.Y_AXIS));
        pdfScrollPane = new JScrollPane(pdfPanel);

        thumbnailPanel = new JPanel();
        thumbnailPanel.setLayout(new BoxLayout(thumbnailPanel, BoxLayout.Y_AXIS));
        thumbnailScrollPane = new JScrollPane(thumbnailPanel);
        thumbnailScrollPane.setPreferredSize(new Dimension(120, 0));

        JSplitPane splitPane = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, thumbnailScrollPane, pdfScrollPane);
        splitPane.setDividerLocation(120);

        mainPanel.add(toolBar, BorderLayout.NORTH);
        mainPanel.add(splitPane, BorderLayout.CENTER);
        mainPanel.add(statusPanel, BorderLayout.SOUTH);

        add(mainPanel);
    }

    private void openFile(ActionEvent e) {
        JFileChooser fileChooser = new JFileChooser();
        fileChooser.setFileFilter(new javax.swing.filechooser.FileNameExtensionFilter("PDF Files", "pdf"));
        if (fileChooser.showOpenDialog(this) == JFileChooser.APPROVE_OPTION) {
            currentFile = fileChooser.getSelectedFile();
            statusLabel.setText("Loaded: " + currentFile.getName());
            renderPdfPages();
        }
    }

    private void renderPdfPages() {
        try (PDDocument document = PDDocument.load(currentFile)) {
            PDFRenderer renderer = new PDFRenderer(document);
            pdfPages.clear();
            pdfPanel.removeAll();
            thumbnailPanel.removeAll();

            for (int i = 0; i < document.getNumberOfPages(); i++) {
                BufferedImage image = renderer.renderImageWithDPI(i, (float) (100 * zoomFactor));
                pdfPages.add(image);

                ImageIcon icon = new ImageIcon(image);
                JLabel imgLabel = new JLabel(icon);
                pdfPanel.add(imgLabel);

                // Thumbnail
                BufferedImage thumbImage = renderer.renderImageWithDPI(i, 30);
                ImageIcon thumbIcon = new ImageIcon(thumbImage);
                JButton thumbButton = new JButton(thumbIcon);
                final int index = i;
                thumbButton.addActionListener(e -> scrollToPage(index));
                thumbnailPanel.add(thumbButton);
            }

            pdfPanel.revalidate();
            pdfPanel.repaint();
            thumbnailPanel.revalidate();
            thumbnailPanel.repaint();

        } catch (IOException ex) {
            JOptionPane.showMessageDialog(this, "Failed to load PDF", "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void scrollToPage(int index) {
        Component target = pdfPanel.getComponent(index);
        Rectangle bounds = target.getBounds();
        pdfScrollPane.getViewport().setViewPosition(bounds.getLocation());
    }

    private void zoom(double factor) {
        zoomFactor *= factor;
        if (currentFile != null) renderPdfPages();
    }

    private void saveFile(ActionEvent e) {
        if (currentFile != null) {
            JFileChooser fileChooser = new JFileChooser();
            fileChooser.setSelectedFile(currentFile);
            if (fileChooser.showSaveDialog(this) == JFileChooser.APPROVE_OPTION) {
                File newFile = fileChooser.getSelectedFile();
                statusLabel.setText("Saved to: " + newFile.getName());
            }
        } else {
            JOptionPane.showMessageDialog(this, "No file is currently open", "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void removePage(ActionEvent e) {
        if (currentFile != null) {
            String input = JOptionPane.showInputDialog(this, "Enter page number to remove:");
            if (input != null && !input.isEmpty()) {
                try {
                    int pageNumber = Integer.parseInt(input) - 1;
                    PDFOperations.removePage(currentFile, pageNumber);
                    statusLabel.setText("Page " + (pageNumber + 1) + " removed from " + currentFile.getName());
                    renderPdfPages();
                } catch (Exception ex) {
                    JOptionPane.showMessageDialog(this, "Invalid page number", "Error", JOptionPane.ERROR_MESSAGE);
                }
            }
        } else {
            JOptionPane.showMessageDialog(this, "No file is currently open", "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void rotatePdf(ActionEvent e) {
        if (currentFile != null) {
            String[] options = {"90°", "180°", "270°"};
            int rotation = JOptionPane.showOptionDialog(this, "Select rotation angle:", "Rotate PDF",
                    JOptionPane.DEFAULT_OPTION, JOptionPane.PLAIN_MESSAGE, null, options, options[0]);

            if (rotation != JOptionPane.CLOSED_OPTION) {
                int degrees = 90 * (rotation + 1);
                try {
                    PDFOperations.rotatePdf(currentFile, degrees);
                    statusLabel.setText("PDF rotated by " + degrees + "°");
                    renderPdfPages();
                } catch (IOException ex) {
                    JOptionPane.showMessageDialog(this, "Failed to rotate PDF", "Error", JOptionPane.ERROR_MESSAGE);
                }
            }
        } else {
            JOptionPane.showMessageDialog(this, "No file is currently open", "Error", JOptionPane.ERROR_MESSAGE);
        }
    }
}

