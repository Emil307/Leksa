package com.uwords.domain.common;

import java.util.Map;

public class NotFoundException extends BaseDomainException {

    public NotFoundException(String message) {
        super(message);
    }

    public NotFoundException(String message, Map<String, Object> payload) {
        super(message, payload);
    }

    public NotFoundException(String message, Map<String, Object> payload, boolean exposeToUser) {
        super(message, payload, exposeToUser);
    }

    @Override
    public ErrorCode code() {
        return ErrorCode.NOT_FOUND;
    }
}
