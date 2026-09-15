package com.uwords.domain.common;

import java.util.Map;

public class UnauthorizedException extends BaseDomainException {

    public UnauthorizedException(String message) {
        super(message);
    }

    public UnauthorizedException(String message, Map<String, Object> payload) {
        super(message, payload);
    }

    public UnauthorizedException(String message, Map<String, Object> payload, boolean exposeToUser) {
        super(message, payload, exposeToUser);
    }

    @Override
    public ErrorCode code() {
        return ErrorCode.UNAUTHORIZED;
    }
}
