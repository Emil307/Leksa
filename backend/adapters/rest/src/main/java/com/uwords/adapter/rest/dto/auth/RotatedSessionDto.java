package com.uwords.adapter.rest.dto.auth;

import java.util.UUID;

public record RotatedSessionDto(UUID id, String refreshToken, String accessToken) {

    @Override
    public String toString() {
        return "RotatedSessionDto(id=" + id + ", refreshToken=<redacted>, accessToken=<redacted>)";
    }
}
