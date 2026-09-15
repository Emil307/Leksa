package com.uwords.adapter.rest.testing;

import com.uwords.adapter.rest.controller.AuthChallengeStartController;
import com.uwords.adapter.rest.error.GlobalExceptionHandler;
import com.uwords.domain.common.ConflictException;
import com.uwords.domain.common.UnavailableException;
import com.uwords.domain.common.ValidationException;
import com.uwords.usecase.service.auth.StartAuthChallengeService;
import com.uwords.usecase.service.auth.StartChallengeRequest;
import java.util.Map;
import org.mockito.ArgumentCaptor;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultActions;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import static com.uwords.adapter.rest.testing.StartChallengeData.CONFLICT_ENVELOPE;
import static com.uwords.adapter.rest.testing.StartChallengeData.CONFLICT_MESSAGE;
import static com.uwords.adapter.rest.testing.StartChallengeData.EMPTY_BODY;
import static com.uwords.adapter.rest.testing.StartChallengeData.EMPTY_FIELDS_BODY;
import static com.uwords.adapter.rest.testing.StartChallengeData.EMPTY_USECASE_REQUEST;
import static com.uwords.adapter.rest.testing.StartChallengeData.EXPECTED_RESPONSE;
import static com.uwords.adapter.rest.testing.StartChallengeData.EXPECTED_USECASE_REQUEST;
import static com.uwords.adapter.rest.testing.StartChallengeData.NULL_FIELDS_BODY;
import static com.uwords.adapter.rest.testing.StartChallengeData.READY_BODY;
import static com.uwords.adapter.rest.testing.StartChallengeData.RETRY_AFTER_SECONDS;
import static com.uwords.adapter.rest.testing.StartChallengeData.SERVER_OWNED_BODY;
import static com.uwords.adapter.rest.testing.StartChallengeData.START_PATH;
import static com.uwords.adapter.rest.testing.StartChallengeData.STARTED_CHALLENGE;
import static com.uwords.adapter.rest.testing.StartChallengeData.UNAVAILABLE_DETAIL;
import static com.uwords.adapter.rest.testing.StartChallengeData.UNAVAILABLE_ENVELOPE;
import static com.uwords.adapter.rest.testing.StartChallengeData.VALIDATION_ENVELOPE;
import static com.uwords.adapter.rest.testing.StartChallengeData.VALIDATION_MESSAGE;
import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

public class StartChallengeStatements {

    private final StartAuthChallengeService service = mock(StartAuthChallengeService.class);
    private final MockMvc mockMvc = MockMvcBuilders
            .standaloneSetup(new AuthChallengeStartController(service))
            .setControllerAdvice(new GlobalExceptionHandler())
            .build();

    private ResultActions response;

    public void givenUsecaseStartsTheChallenge() {
        when(service.start(any())).thenReturn(STARTED_CHALLENGE);
    }

    public void givenUsecaseRejectsTheCredentialAndType() {
        when(service.start(any())).thenThrow(new ValidationException(VALIDATION_MESSAGE));
    }

    public void givenUsecaseIsCoolingDown() {
        when(service.start(any())).thenThrow(new ConflictException(
                CONFLICT_MESSAGE, Map.of("retryAfterSeconds", RETRY_AFTER_SECONDS)));
    }

    public void givenUsecaseCannotAcceptTheChallenge() {
        when(service.start(any())).thenThrow(new UnavailableException(UNAVAILABLE_DETAIL, Map.of(), false));
    }

    public void whenClientRequestsACode() throws Exception {
        post(READY_BODY);
    }

    public void whenClientRequestsACodeWithServerOwnedFields() throws Exception {
        post(SERVER_OWNED_BODY);
    }

    public void whenClientSendsABodyWithoutEmailAndType() throws Exception {
        post(EMPTY_BODY);
    }

    public void whenClientSendsNullEmailAndType() throws Exception {
        post(NULL_FIELDS_BODY);
    }

    public void whenClientSendsEmptyEmailAndType() throws Exception {
        post(EMPTY_FIELDS_BODY);
    }

    public void assertChallengeIsAnsweredWithOnlyItsOwnFields() throws Exception {
        assertAnswered(200, EXPECTED_RESPONSE);
    }

    public void assertUsecaseReceivedTheTranslatedRequest() {
        assertThat(received()).isEqualTo(EXPECTED_USECASE_REQUEST);
    }

    public void assertUsecaseReceivedAnEmptyCredentialAndType() {
        assertThat(received()).isEqualTo(EMPTY_USECASE_REQUEST);
    }

    public void assertRequestIsRefusedAsInvalid() throws Exception {
        assertAnswered(400, VALIDATION_ENVELOPE);
    }

    public void assertRequestIsRefusedAsCoolingDown() throws Exception {
        assertAnswered(409, CONFLICT_ENVELOPE);
    }

    public void assertRequestIsRefusedAsUnavailable() throws Exception {
        assertAnswered(503, UNAVAILABLE_ENVELOPE);
    }

    private void post(String body) throws Exception {
        response = mockMvc.perform(MockMvcRequestBuilders.post(START_PATH)
                .contentType(MediaType.APPLICATION_JSON)
                .content(body));
    }

    private void assertAnswered(int httpStatus, String body) throws Exception {
        response.andExpect(status().is(httpStatus)).andExpect(content().json(body, true));
    }

    private StartChallengeRequest received() {
        ArgumentCaptor<StartChallengeRequest> captor = ArgumentCaptor.forClass(StartChallengeRequest.class);
        verify(service).start(captor.capture());
        return captor.getValue();
    }
}
