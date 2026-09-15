package com.uwords.adapter.cache;

import java.util.LinkedHashMap;
import java.util.Map;

public final class FlatJson {

    public static final String OBJECT_START = "{";
    public static final String OBJECT_END = "}";
    public static final String FIELD_SEPARATOR = ", ";
    public static final String NAME_SEPARATOR = ": ";

    private static final int LAST_ASCII_CHARACTER = 0x7E;
    private static final int FIRST_PRINTABLE_CHARACTER = 0x20;

    private FlatJson() {
    }

    public static String quoted(String value) {
        StringBuilder quoted = new StringBuilder("\"");
        for (int index = 0; index < value.length(); index++) {
            appendEscaped(quoted, value.charAt(index));
        }
        return quoted.append('"').toString();
    }

    public static Map<String, String> fields(String raw) {
        Map<String, String> fields = new LinkedHashMap<>();
        int index = skipBlanks(raw, raw.indexOf('{') + 1);
        while (index < raw.length() && raw.charAt(index) != '}') {
            StringBuilder name = new StringBuilder();
            index = skipBlanks(raw, readString(raw, index, name));
            index = skipBlanks(raw, index + 1);
            StringBuilder value = new StringBuilder();
            index = raw.charAt(index) == '"' ? readString(raw, index, value) : readLiteral(raw, index, value);
            fields.put(name.toString(), value.toString());
            index = skipBlanks(raw, index);
            if (index < raw.length() && raw.charAt(index) == ',') {
                index = skipBlanks(raw, index + 1);
            }
        }
        return fields;
    }

    private static void appendEscaped(StringBuilder quoted, char character) {
        switch (character) {
            case '"' -> quoted.append("\\\"");
            case '\\' -> quoted.append("\\\\");
            case '\n' -> quoted.append("\\n");
            case '\r' -> quoted.append("\\r");
            case '\t' -> quoted.append("\\t");
            case '\b' -> quoted.append("\\b");
            case '\f' -> quoted.append("\\f");
            default -> appendPlain(quoted, character);
        }
    }

    private static void appendPlain(StringBuilder quoted, char character) {
        if (character < FIRST_PRINTABLE_CHARACTER || character > LAST_ASCII_CHARACTER) {
            quoted.append(String.format("\\u%04x", (int) character));
            return;
        }
        quoted.append(character);
    }

    private static int skipBlanks(String raw, int start) {
        int index = start;
        while (index < raw.length() && Character.isWhitespace(raw.charAt(index))) {
            index++;
        }
        return index;
    }

    private static int readLiteral(String raw, int start, StringBuilder target) {
        int index = start;
        while (index < raw.length() && raw.charAt(index) != ',' && raw.charAt(index) != '}') {
            target.append(raw.charAt(index));
            index++;
        }
        return index;
    }

    private static int readString(String raw, int start, StringBuilder target) {
        int index = start + 1;
        while (raw.charAt(index) != '"') {
            if (raw.charAt(index) != '\\') {
                target.append(raw.charAt(index));
                index++;
                continue;
            }
            index = readEscape(raw, index + 1, target);
        }
        return index + 1;
    }

    private static int readEscape(String raw, int start, StringBuilder target) {
        char marker = raw.charAt(start);
        switch (marker) {
            case 'n' -> target.append('\n');
            case 'r' -> target.append('\r');
            case 't' -> target.append('\t');
            case 'b' -> target.append('\b');
            case 'f' -> target.append('\f');
            case 'u' -> target.append((char) Integer.parseInt(raw.substring(start + 1, start + 5), 16));
            default -> target.append(marker);
        }
        return marker == 'u' ? start + 5 : start + 1;
    }
}
