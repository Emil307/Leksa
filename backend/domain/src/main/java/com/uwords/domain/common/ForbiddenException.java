package com.uwords.domain.common;

import java.util.Map;

public class ForbiddenException extends BaseDomainException {

    public ForbiddenException(String message) {
        super(message);
    }

    public ForbiddenException(String message, Map<String, Object> payload) {
        super(message, payload);
    }

    public ForbiddenException(String message, Map<String, Object> payload, boolean exposeToUser) {
        super(message, payload, exposeToUser);
    }

    @Override
    public ErrorCode code() {
        return ErrorCode.FORBIDDEN;
    }
}
