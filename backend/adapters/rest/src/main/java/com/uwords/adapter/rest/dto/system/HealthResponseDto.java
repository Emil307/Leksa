package com.uwords.adapter.rest.dto.system;

public record HealthResponseDto(String status, String database) {

    private static final String UP = "UP";
    private static final String DOWN = "DOWN";

    public static HealthResponseDto of(boolean ready) {
        String state = ready ? UP : DOWN;
        return new HealthResponseDto(state, state);
    }
}
