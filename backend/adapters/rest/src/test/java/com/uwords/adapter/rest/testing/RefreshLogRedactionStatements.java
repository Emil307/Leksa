package com.uwords.adapter.rest.testing;

import ch.qos.logback.classic.Level;
import ch.qos.logback.classic.Logger;
import ch.qos.logback.classic.spi.ILoggingEvent;
import ch.qos.logback.classic.spi.IThrowableProxy;
import ch.qos.logback.core.read.ListAppender;
import com.uwords.adapter.rest.controller.AuthTokenController;
import com.uwords.adapter.rest.error.GlobalExceptionHandler;
import com.uwords.domain.auth.failure.AuthFailureReason;
import com.uwords.domain.auth.failure.Unauthorized;
import com.uwords.domain.auth.session.RefreshToken;
import com.uwords.domain.common.ValidationException;
import com.uwords.usecase.service.auth.RefreshSessionTokensService;
import java.util.List;
import org.slf4j.LoggerFactory;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

public class RefreshLogRedactionStatements {

    private static final String REFRESH_PATH = "/api/v1/auth/token/refresh";
    private static final String SENTINEL = "SENTINEL-refresh-token-9f2c";
    private static final String WELL_FORMED_BODY = "{\"refreshToken\":\"" + SENTINEL + "\"}";
    private static final String TRUNCATED_BODY = "{\"refreshToken\":\"" + SENTINEL;

    private final RefreshSessionTokensService service = mock(RefreshSessionTokensService.class);
    private final MockMvc mockMvc = MockMvcBuilders
            .standaloneSetup(new AuthTokenController(service))
            .setControllerAdvice(new GlobalExceptionHandler())
            .build();

    private String body = WELL_FORMED_BODY;
    private MvcResult result;
    private List<ILoggingEvent> events = List.of();

    public void givenTheUsecaseRefusesTheTokenAsInvalid() {
        when(service.refresh(any())).thenThrow(new ValidationException(RefreshToken.TOKEN_INVALID_MESSAGE));
    }

    public void givenTheUsecaseRefusesTheSession() {
        when(service.refresh(any())).thenThrow(Unauthorized.of(AuthFailureReason.SESSION));
    }

    public void givenTheBodyIsTruncatedAfterTheToken() {
        body = TRUNCATED_BODY;
    }

    public void whenTheClientRefreshesWhileAllLogsAreCaptured() throws Exception {
        Logger root = (Logger) LoggerFactory.getLogger(Logger.ROOT_LOGGER_NAME);
        Level previous = root.getLevel();
        ListAppender<ILoggingEvent> appender = new ListAppender<>();
        appender.start();
        root.setLevel(Level.TRACE);
        root.addAppender(appender);
        try {
            result = mockMvc.perform(MockMvcRequestBuilders.post(REFRESH_PATH)
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(body)).andReturn();
        } finally {
            root.detachAppender(appender);
            root.setLevel(previous);
        }
        events = List.copyOf(appender.list);
    }

    public void assertTheRefusalWasAnsweredWith(int httpStatus) {
        assertThat(result.getResponse().getStatus()).isEqualTo(httpStatus);
    }

    public void assertNoLogLineCarriesTheToken() {
        assertThat(events).isNotEmpty();
        for (ILoggingEvent event : events) {
            assertThat(event.getFormattedMessage()).doesNotContain(SENTINEL);
            assertThat(renderedThrowable(event.getThrowableProxy())).doesNotContain(SENTINEL);
        }
    }

    private static String renderedThrowable(IThrowableProxy proxy) {
        if (proxy == null) {
            return "";
        }
        return proxy.getClassName() + ": " + proxy.getMessage() + renderedThrowable(proxy.getCause());
    }
}
