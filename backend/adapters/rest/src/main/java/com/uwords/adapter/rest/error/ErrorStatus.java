package com.uwords.adapter.rest.error;

import com.uwords.domain.common.ErrorCode;
import org.springframework.http.HttpStatus;

public final class ErrorStatus {

    private ErrorStatus() {
    }

    public static HttpStatus of(ErrorCode code) {
        return switch (code) {
            case VALIDATION_FAILED -> HttpStatus.BAD_REQUEST;
            case UNAUTHORIZED -> HttpStatus.UNAUTHORIZED;
            case FORBIDDEN -> HttpStatus.FORBIDDEN;
            case NOT_FOUND -> HttpStatus.NOT_FOUND;
            case CONFLICT -> HttpStatus.CONFLICT;
            case UNAVAILABLE -> HttpStatus.SERVICE_UNAVAILABLE;
        };
    }
}
