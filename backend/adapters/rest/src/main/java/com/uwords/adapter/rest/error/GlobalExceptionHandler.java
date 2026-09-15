package com.uwords.adapter.rest.error;

import com.uwords.domain.common.BaseDomainException;
import com.uwords.domain.common.ErrorCode;
import com.uwords.domain.common.UnauthorizedException;
import jakarta.servlet.http.HttpServletRequest;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.HttpMediaTypeNotSupportedException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GlobalExceptionHandler {

    public static final String UNAUTHORIZED_CODE = "UNAUTHORIZED";
    public static final String UNAUTHORIZED_MESSAGE = "Unauthorized";
    public static final String HIDDEN_MESSAGE = "Request could not be processed";
    public static final String INTERNAL_MESSAGE = "Internal Server Error";

    private static final String REASON_FIELD = "reason";
    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(UnauthorizedException.class)
    public ResponseEntity<ErrorEnvelope> handleUnauthorized(
            UnauthorizedException refusal, HttpServletRequest request) {
        log.info("Auth refused on {}: {}", request.getRequestURI(), refusal.payload().get(REASON_FIELD));
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                .body(new ErrorEnvelope(UNAUTHORIZED_CODE, UNAUTHORIZED_MESSAGE, null));
    }

    @ExceptionHandler(BaseDomainException.class)
    public ResponseEntity<ErrorEnvelope> handleDomainException(
            BaseDomainException failure, HttpServletRequest request) {
        ErrorCode code = failure.code();
        log.info("Domain error {} on {}: {}", code.value(), request.getRequestURI(), failure.getMessage());
        return ResponseEntity.status(ErrorStatus.of(code)).body(envelopeOf(failure));
    }

    @ExceptionHandler({HttpMessageNotReadableException.class, HttpMediaTypeNotSupportedException.class})
    public ResponseEntity<ErrorEnvelope> handleUnreadableRequest(Exception failure, HttpServletRequest request) {
        log.info("Unreadable request on {}: {}", request.getRequestURI(), failure.getMessage());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(new ErrorEnvelope(ErrorCode.VALIDATION_FAILED.value(), HIDDEN_MESSAGE, Map.of()));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<String> handleUnexpected(Exception failure, HttpServletRequest request) {
        log.error("Unhandled failure on {}", request.getRequestURI(), failure);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .contentType(MediaType.TEXT_PLAIN)
                .body(INTERNAL_MESSAGE);
    }

    private static ErrorEnvelope envelopeOf(BaseDomainException failure) {
        return new ErrorEnvelope(
                failure.code().value(),
                failure.exposeToUser() ? failure.getMessage() : HIDDEN_MESSAGE,
                failure.exposeToUser() ? failure.payload() : Map.of());
    }
}
