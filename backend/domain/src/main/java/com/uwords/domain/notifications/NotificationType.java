package com.uwords.domain.notifications;

public enum NotificationType {
    EMAIL("EMAIL");

    private final String value;

    NotificationType(String value) {
        this.value = value;
    }

    public String value() {
        return value;
    }
}
