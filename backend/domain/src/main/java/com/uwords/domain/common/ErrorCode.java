package com.uwords.domain.common;

public enum ErrorCode {
    VALIDATION_FAILED("VALIDATION_FAILED"),
    NOT_FOUND("NOT_FOUND"),
    CONFLICT("CONFLICT"),
    UNAUTHORIZED("UNAUTHORIZED"),
    FORBIDDEN("FORBIDDEN"),
    UNAVAILABLE("UNAVAILABLE");

    private final String value;

    ErrorCode(String value) {
        this.value = value;
    }

    public String value() {
        return value;
    }
}
