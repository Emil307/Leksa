package com.uwords.adapter.rest.testing;

import ch.qos.logback.classic.Level;
import ch.qos.logback.classic.Logger;
import ch.qos.logback.classic.spi.ILoggingEvent;
import ch.qos.logback.core.read.ListAppender;
import com.uwords.adapter.rest.error.GlobalExceptionHandler;
import com.uwords.domain.auth.failure.AuthFailureReason;
import com.uwords.domain.auth.failure.Unauthorized;
import com.uwords.domain.common.ConflictException;
import com.uwords.domain.common.NotFoundException;
import java.util.List;
import java.util.Map;
import org.slf4j.LoggerFactory;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import static com.uwords.adapter.rest.testing.BoomController.BOOM_PATH;
import static com.uwords.adapter.rest.testing.ProfileData.UNAUTHORIZED_BODY;
import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

public class ExceptionHandlerStatements {

    private static final String NOT_FOUND_MESSAGE = "word not found";
    private static final String INTERNAL_MESSAGE = "internal detail";
    private static final Map<String, Object> FAILURE_PAYLOAD = Map.of("id", "42");
    private static final AuthFailureReason LOGGED_REASON = AuthFailureReason.LEGACY_SESSION;

    private static final String NOT_FOUND_ENVELOPE = """
            {"code":"NOT_FOUND","message":"word not found","payload":{"id":"42"}}""";
    private static final String HIDDEN_CONFLICT_ENVELOPE = """
            {"code":"CONFLICT","message":"Request could not be processed","payload":{}}""";

    private RuntimeException failure;
    private MvcResult result;
    private List<String> logMessages = List.of();

    public void givenTheRouteRaisesANotFoundCarryingAPayload() {
        failure = new NotFoundException(NOT_FOUND_MESSAGE, FAILURE_PAYLOAD);
    }

    public void givenTheRouteRaisesAConflictHiddenFromTheUser() {
        failure = new ConflictException(INTERNAL_MESSAGE, FAILURE_PAYLOAD, false);
    }

    public void givenTheRouteRefusesASessionRowWithoutARecordedLifetime() {
        failure = Unauthorized.of(LOGGED_REASON);
    }

    public void whenTheRouteIsCalled() throws Exception {
        result = call(failure);
    }

    public void whenTheRouteIsCalledWhileLogsAreCaptured() throws Exception {
        Logger logger = (Logger) LoggerFactory.getLogger(GlobalExceptionHandler.class);
        ListAppender<ILoggingEvent> appender = new ListAppender<>();
        appender.start();
        logger.setLevel(Level.INFO);
        logger.addAppender(appender);
        try {
            result = call(failure);
        } finally {
            logger.detachAppender(appender);
        }
        logMessages = appender.list.stream().map(ILoggingEvent::getFormattedMessage).toList();
    }

    public void assertAnswered404WithTheCodeMessageAndPayload() throws Exception {
        assertAnswered(404, NOT_FOUND_ENVELOPE);
    }

    public void assertAnswered409WithoutTheInternalMessageOrPayload() throws Exception {
        assertAnswered(409, HIDDEN_CONFLICT_ENVELOPE);
    }

    public void assertEveryRefusalReasonAnswersTheUniform401() throws Exception {
        for (AuthFailureReason reason : AuthFailureReason.values()) {
            result = call(Unauthorized.of(reason));
            assertAnswered(401, UNAUTHORIZED_BODY);
        }
    }

    public void assertTheReasonIsLoggedAndAbsentFromTheResponse() throws Exception {
        assertThat(body()).doesNotContain(LOGGED_REASON.value());
        assertThat(logMessages)
                .containsExactly("Auth refused on " + BOOM_PATH + ": " + LOGGED_REASON.value());
    }

    private void assertAnswered(int httpStatus, String expected) throws Exception {
        assertThat(result.getResponse().getStatus()).isEqualTo(httpStatus);
        status().is(httpStatus).match(result);
        content().json(expected, true).match(result);
    }

    private String body() throws Exception {
        return result.getResponse().getContentAsString();
    }

    private MvcResult call(RuntimeException raised) throws Exception {
        MockMvc mockMvc = MockMvcBuilders.standaloneSetup(new BoomController(raised))
                .setControllerAdvice(new GlobalExceptionHandler())
                .build();
        return mockMvc.perform(MockMvcRequestBuilders.get(BOOM_PATH)).andReturn();
    }
}
