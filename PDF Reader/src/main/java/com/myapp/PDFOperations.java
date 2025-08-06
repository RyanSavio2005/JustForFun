package com.myapp;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.rendering.PDFRenderer;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;

public class PDFOperations {

    // Removes the specified page from the PDF (0-based index)
    public static void removePage(File pdfFile, int pageNumber) throws IOException {
        try (PDDocument document = PDDocument.load(pdfFile)) {
            if (pageNumber >= 0 && pageNumber < document.getNumberOfPages()) {
                document.removePage(pageNumber);
                document.save(pdfFile);
            }
        }
    }

    // Rotates all pages in the PDF by the specified degrees (e.g., 90, 180, 270)
    public static void rotatePdf(File pdfFile, int degrees) throws IOException {
        try (PDDocument document = PDDocument.load(pdfFile)) {
            for (PDPage page : document.getPages()) {
                int currentRotation = page.getRotation();
                page.setRotation((currentRotation + degrees) % 360);
            }
            document.save(pdfFile);
        }
    }

    // Compresses the PDF by saving it again (no advanced compression; works for minor size reduction)
    public static void compressPdf(File inputFile, File outputFile) throws IOException {
        try (PDDocument document = PDDocument.load(inputFile)) {
            document.setAllSecurityToBeRemoved(true);
            document.save(outputFile);
        }
    }

    // Converts all pages of a PDF to JPG images and saves them to a directory
    public static int convertToJpg(File inputFile, File outputDir) throws IOException {
        try (PDDocument document = PDDocument.load(inputFile)) {
            PDFRenderer renderer = new PDFRenderer(document);
            int pageCount = document.getNumberOfPages();

            for (int i = 0; i < pageCount; i++) {
                BufferedImage image = renderer.renderImageWithDPI(i, 150); // 150 DPI for medium quality
                File outputFile = new File(outputDir, "page_" + (i + 1) + ".jpg");
                ImageIO.write(image, "jpg", outputFile);
            }

            return pageCount;
        }
    }

    // Saves the current document to another file
    public static void savePdf(File inputFile, File outputFile) throws IOException {
        try (PDDocument document = PDDocument.load(inputFile)) {
            document.save(outputFile);
        }
    }

    // Stub for unsupported Word conversion
    public static void convertToWord(File inputPdf, File outputDocx) {
        throw new UnsupportedOperationException("Conversion to Word is not supported with PDFBox.");
    }
}
