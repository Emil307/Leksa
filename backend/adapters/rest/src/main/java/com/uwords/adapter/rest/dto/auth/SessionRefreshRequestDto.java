package com.uwords.adapter.rest.dto.auth;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.uwords.usecase.service.auth.RefreshSessionRequest;

@JsonIgnoreProperties(ignoreUnknown = true)
public record SessionRefreshRequestDto(Object refreshToken) {

    public RefreshSessionRequest toUsecaseRequest() {
        String presentedToken = refreshToken instanceof String token ? token : "";
        return new RefreshSessionRequest(presentedToken);
    }

    @Override
    public String toString() {
        return "SessionRefreshRequestDto(refreshToken=<redacted>)";
    }
}
