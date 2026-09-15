package com.uwords.adapter.storage.testing;

import com.uwords.domain.common.BaseDomainException;
import com.uwords.domain.common.ErrorCode;
import java.util.Map;

public record FailureShape(ErrorCode code, String message, Map<String, Object> payload, boolean exposeToUser) {

    public static FailureShape of(Throwable thrown) {
        BaseDomainException failure = (BaseDomainException) thrown;
        return new FailureShape(failure.code(), failure.getMessage(), failure.payload(), failure.exposeToUser());
    }
}
