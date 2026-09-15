package com.uwords.domain.notifications;

public enum OutboxStatus {
    ACTIVE("ACTIVE"),
    PROCESS("PROCESS"),
    COMPLETED("COMPLETED"),
    FAILED("FAILED");

    private final String value;

    OutboxStatus(String value) {
        this.value = value;
    }

    public String value() {
        return value;
    }

    public boolean isTerminal() {
        return this == COMPLETED || this == FAILED;
    }
}
