package com.uwords.domain.auth.failure;

public enum AuthFailureReason {
    HEADER("header"),
    SIGNATURE("signature"),
    CLAIMS("claims"),
    SESSION("session"),
    LEGACY_SESSION("legacy_session"),
    STORAGE("storage"),
    ACCOUNT("account");

    private final String value;

    AuthFailureReason(String value) {
        this.value = value;
    }

    public String value() {
        return value;
    }
}
