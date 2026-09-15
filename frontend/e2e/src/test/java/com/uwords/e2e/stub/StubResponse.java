package com.uwords.e2e.stub;

import java.util.LinkedHashMap;
import java.util.Map;

public record StubResponse(int status, String body) {

    public static StubResponse ok(Map<String, Object> payload) {
        return new StubResponse(200, Json.write(payload));
    }

    public static StubResponse error(int status, String code, String message, Map<String, Object> payload) {
        Map<String, Object> envelope = new LinkedHashMap<>();
        envelope.put("code", code);
        envelope.put("message", message);
        envelope.put("payload", new LinkedHashMap<>(payload));
        return new StubResponse(status, Json.write(envelope));
    }
}
