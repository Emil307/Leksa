package com.uwords.domain.auth.user;

public enum AuthProvider {
    EMAIL("email");

    private final String value;

    AuthProvider(String value) {
        this.value = value;
    }

    public String value() {
        return value;
    }
}
