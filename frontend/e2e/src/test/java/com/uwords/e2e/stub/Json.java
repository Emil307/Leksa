package com.uwords.e2e.stub;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class Json {

    private final String text;
    private int pos;

    private Json(String text) {
        this.text = text;
    }

    @SuppressWarnings("unchecked")
    public static Map<String, Object> parseObject(String text) {
        Json json = new Json(text);
        Object value = json.readValue();
        json.skipWhitespace();
        if (json.pos != text.length() || !(value instanceof Map)) {
            throw new IllegalArgumentException("Expected a JSON object: " + text);
        }
        return (Map<String, Object>) value;
    }

    public static String write(Map<String, Object> object) {
        StringBuilder out = new StringBuilder("{");
        String separator = "";
        for (Map.Entry<String, Object> entry : object.entrySet()) {
            out.append(separator).append(quote(entry.getKey())).append(':').append(writeValue(entry.getValue()));
            separator = ",";
        }
        return out.append('}').toString();
    }

    @SuppressWarnings("unchecked")
    private static String writeValue(Object value) {
        if (value == null) {
            return "null";
        }
        if (value instanceof String string) {
            return quote(string);
        }
        if (value instanceof Map) {
            return write((Map<String, Object>) value);
        }
        return String.valueOf(value);
    }

    private static String quote(String value) {
        StringBuilder out = new StringBuilder("\"");
        for (char c : value.toCharArray()) {
            switch (c) {
                case '"' -> out.append("\\\"");
                case '\\' -> out.append("\\\\");
                case '\n' -> out.append("\\n");
                case '\r' -> out.append("\\r");
                case '\t' -> out.append("\\t");
                default -> out.append(c);
            }
        }
        return out.append('"').toString();
    }

    private Object readValue() {
        skipWhitespace();
        char c = peek();
        if (c == '{') {
            return readObject();
        }
        if (c == '[') {
            return readArray();
        }
        if (c == '"') {
            return readString();
        }
        if (text.startsWith("true", pos)) {
            pos += 4;
            return Boolean.TRUE;
        }
        if (text.startsWith("false", pos)) {
            pos += 5;
            return Boolean.FALSE;
        }
        if (text.startsWith("null", pos)) {
            pos += 4;
            return null;
        }
        return readNumber();
    }

    private Map<String, Object> readObject() {
        Map<String, Object> object = new LinkedHashMap<>();
        expect('{');
        skipWhitespace();
        if (peek() == '}') {
            pos++;
            return object;
        }
        while (true) {
            skipWhitespace();
            String key = readString();
            skipWhitespace();
            expect(':');
            object.put(key, readValue());
            skipWhitespace();
            if (peek() == ',') {
                pos++;
                continue;
            }
            expect('}');
            return object;
        }
    }

    private List<Object> readArray() {
        List<Object> array = new ArrayList<>();
        expect('[');
        skipWhitespace();
        if (peek() == ']') {
            pos++;
            return array;
        }
        while (true) {
            array.add(readValue());
            skipWhitespace();
            if (peek() == ',') {
                pos++;
                continue;
            }
            expect(']');
            return array;
        }
    }

    private String readString() {
        expect('"');
        StringBuilder out = new StringBuilder();
        while (peek() != '"') {
            char c = text.charAt(pos++);
            if (c == '\\') {
                char escaped = text.charAt(pos++);
                switch (escaped) {
                    case 'n' -> out.append('\n');
                    case 'r' -> out.append('\r');
                    case 't' -> out.append('\t');
                    case 'u' -> {
                        out.append((char) Integer.parseInt(text.substring(pos, pos + 4), 16));
                        pos += 4;
                    }
                    default -> out.append(escaped);
                }
            } else {
                out.append(c);
            }
        }
        pos++;
        return out.toString();
    }

    private Number readNumber() {
        int start = pos;
        while (pos < text.length() && "+-0123456789.eE".indexOf(text.charAt(pos)) >= 0) {
            pos++;
        }
        String literal = text.substring(start, pos);
        if (literal.isEmpty()) {
            throw new IllegalArgumentException("Unexpected token at " + start + " in " + text);
        }
        if (literal.contains(".") || literal.contains("e") || literal.contains("E")) {
            return Double.parseDouble(literal);
        }
        return Long.parseLong(literal);
    }

    private void skipWhitespace() {
        while (pos < text.length() && Character.isWhitespace(text.charAt(pos))) {
            pos++;
        }
    }

    private char peek() {
        if (pos >= text.length()) {
            throw new IllegalArgumentException("Unexpected end of JSON: " + text);
        }
        return text.charAt(pos);
    }

    private void expect(char c) {
        if (peek() != c) {
            throw new IllegalArgumentException("Expected '" + c + "' at " + pos + " in " + text);
        }
        pos++;
    }
}
