package com.uwords.adapter.rest.dto.auth;

import java.util.UUID;

public record IssuedSessionDto(UUID id, String refreshToken, String accessToken) {

    @Override
    public String toString() {
        return "IssuedSessionDto(id=" + id + ", refreshToken=<redacted>, accessToken=<redacted>)";
    }
}
