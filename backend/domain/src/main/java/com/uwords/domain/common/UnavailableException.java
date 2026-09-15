package com.uwords.domain.common;

import java.util.Map;

public class UnavailableException extends BaseDomainException {

    public UnavailableException(String message) {
        super(message);
    }

    public UnavailableException(String message, Map<String, Object> payload) {
        super(message, payload);
    }

    public UnavailableException(String message, Map<String, Object> payload, boolean exposeToUser) {
        super(message, payload, exposeToUser);
    }

    @Override
    public ErrorCode code() {
        return ErrorCode.UNAVAILABLE;
    }
}
