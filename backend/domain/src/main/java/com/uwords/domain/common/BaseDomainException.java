package com.uwords.domain.common;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

public class BaseDomainException extends RuntimeException {

    private final transient Map<String, Object> payload;
    private final boolean exposeToUser;

    public BaseDomainException(String message) {
        this(message, null, true);
    }

    public BaseDomainException(String message, Map<String, Object> payload) {
        this(message, payload, true);
    }

    public BaseDomainException(String message, Map<String, Object> payload, boolean exposeToUser) {
        super(message);
        this.payload = payload == null
                ? Map.of()
                : Collections.unmodifiableMap(new LinkedHashMap<>(payload));
        this.exposeToUser = exposeToUser;
    }

    public ErrorCode code() {
        return ErrorCode.VALIDATION_FAILED;
    }

    public Map<String, Object> payload() {
        return payload;
    }

    public boolean exposeToUser() {
        return exposeToUser;
    }
}
