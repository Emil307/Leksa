package com.uwords.adapter.rest.error;

import java.util.Map;

public record ErrorEnvelope(String code, String message, Map<String, Object> payload) {
}
