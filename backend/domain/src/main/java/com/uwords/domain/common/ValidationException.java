package com.uwords.domain.common;

import java.util.Map;

public class ValidationException extends BaseDomainException {

    public ValidationException(String message) {
        super(message);
    }

    public ValidationException(String message, Map<String, Object> payload) {
        super(message, payload);
    }

    public ValidationException(String message, Map<String, Object> payload, boolean exposeToUser) {
        super(message, payload, exposeToUser);
    }

    @Override
    public ErrorCode code() {
        return ErrorCode.VALIDATION_FAILED;
    }
}
