package com.uwords.domain.common;

import java.util.Map;

public class ConflictException extends BaseDomainException {

    public ConflictException(String message) {
        super(message);
    }

    public ConflictException(String message, Map<String, Object> payload) {
        super(message, payload);
    }

    public ConflictException(String message, Map<String, Object> payload, boolean exposeToUser) {
        super(message, payload, exposeToUser);
    }

    @Override
    public ErrorCode code() {
        return ErrorCode.CONFLICT;
    }
}
