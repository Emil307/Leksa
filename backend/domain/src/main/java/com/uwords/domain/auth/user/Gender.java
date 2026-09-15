package com.uwords.domain.auth.user;

public enum Gender {
    MALE("male"),
    FEMALE("female");

    private final String value;

    Gender(String value) {
        this.value = value;
    }

    public String value() {
        return value;
    }
}
