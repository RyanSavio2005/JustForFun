package com.myapp;
import java.io.File;
import javax.swing.filechooser.FileFilter;

public class FileUtils {
    public static File getFileWithExtension(File file, String extension) {
        if (!file.getName().toLowerCase().endsWith("." + extension.toLowerCase())) {
            return new File(file.getParent(), file.getName() + "." + extension);
        }
        return file;
    }

    public static class FileExtensionFilter extends FileFilter {
        private final String extension;
        private final String description;

        public FileExtensionFilter(String extension, String description) {
            this.extension = extension.toLowerCase();
            this.description = description;
        }

        @Override
        public boolean accept(File f) {
            return f.isDirectory() || f.getName().toLowerCase().endsWith("." + extension);
        }

        @Override
        public String getDescription() {
            return description + " (*." + extension + ")";
        }
    }
}
