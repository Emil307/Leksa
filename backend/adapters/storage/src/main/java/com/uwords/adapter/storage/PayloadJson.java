package com.uwords.adapter.storage;

import java.util.Map;
import java.util.stream.Collectors;

public final class PayloadJson {

    private static final String NULL_LITERAL = "null";
    private static final String ENTRY_SEPARATOR = ",";
    private static final String KEY_SEPARATOR = ":";
    private static final char QUOTE = '"';
    private static final char ESCAPE = '\\';
    private static final char LAST_CONTROL_CHARACTER = 0x1F;

    private PayloadJson() {
    }

    public static String write(Map<String, ?> payload) {
        return payload.entrySet().stream()
                .map(entry -> quote(entry.getKey()) + KEY_SEPARATOR + writeValue(entry.getValue()))
                .collect(Collectors.joining(ENTRY_SEPARATOR, "{", "}"));
    }

    private static String writeValue(Object value) {
        return switch (value) {
            case null -> NULL_LITERAL;
            case Map<?, ?> nested -> writeNested(nested);
            case Number number -> number.toString();
            case Boolean flag -> flag.toString();
            default -> quote(value.toString());
        };
    }

    private static String writeNested(Map<?, ?> nested) {
        return nested.entrySet().stream()
                .map(entry -> quote(entry.getKey().toString()) + KEY_SEPARATOR + writeValue(entry.getValue()))
                .collect(Collectors.joining(ENTRY_SEPARATOR, "{", "}"));
    }

    private static String quote(String raw) {
        StringBuilder quoted = new StringBuilder().append(QUOTE);
        for (int index = 0; index < raw.length(); index++) {
            appendCharacter(quoted, raw.charAt(index));
        }
        return quoted.append(QUOTE).toString();
    }

    private static void appendCharacter(StringBuilder quoted, char character) {
        switch (character) {
            case QUOTE, ESCAPE -> quoted.append(ESCAPE).append(character);
            case '\n' -> quoted.append("\\n");
            case '\r' -> quoted.append("\\r");
            case '\t' -> quoted.append("\\t");
            default -> appendPlainCharacter(quoted, character);
        }
    }

    private static void appendPlainCharacter(StringBuilder quoted, char character) {
        if (character <= LAST_CONTROL_CHARACTER) {
            quoted.append(String.format("\\u%04x", (int) character));
            return;
        }
        quoted.append(character);
    }
}
