package com.uwords.adapter.cache.testing.fakes;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public final class EnvFile {

    public static final String LOCATION = "infrastructure/.env";
    public static final String ASSIGNMENT = "=";
    public static final String COMMENT_START = "#";

    private static final Map<String, String> VALUES = read();

    private EnvFile() {
    }

    public static String value(String name, String fallback) {
        return VALUES.getOrDefault(name, fallback);
    }

    public static int number(String name, int fallback) {
        return Integer.parseInt(value(name, String.valueOf(fallback)));
    }

    private static Map<String, String> read() {
        Map<String, String> values = new HashMap<>();
        Path location = locate();
        if (location == null) {
            return values;
        }
        for (String line : lines(location)) {
            collect(values, line.strip());
        }
        return values;
    }

    private static void collect(Map<String, String> values, String line) {
        int separator = line.indexOf(ASSIGNMENT);
        if (line.startsWith(COMMENT_START) || separator <= 0) {
            return;
        }
        values.put(line.substring(0, separator).strip(), line.substring(separator + 1).strip());
    }

    private static List<String> lines(Path location) {
        try {
            return Files.readAllLines(location, StandardCharsets.UTF_8);
        } catch (IOException failure) {
            throw new UncheckedIOException(failure);
        }
    }

    private static Path locate() {
        Path directory = Paths.get(System.getProperty("user.dir")).toAbsolutePath();
        while (directory != null) {
            Path candidate = directory.resolve(LOCATION);
            if (Files.exists(candidate)) {
                return candidate;
            }
            directory = directory.getParent();
        }
        return null;
    }
}
