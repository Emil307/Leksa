package com.uwords.adapter.rest.testing;

import com.uwords.adapter.rest.controller.AuthChallengeVerifyController;
import com.uwords.adapter.rest.error.GlobalExceptionHandler;
import com.uwords.usecase.service.auth.VerifiedSession;
import com.uwords.usecase.service.auth.VerifyAuthChallengeService;
import com.uwords.usecase.service.auth.VerifyChallengeRequest;
import java.util.UUID;
import org.mockito.ArgumentCaptor;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultActions;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

public class VerifyChallengeStatements {

    private static final String VERIFY_PATH = "/api/v1/auth/challenge/verify";
    private static final String CHALLENGE_ID = "11111111-2222-3333-4444-555555555555";
    private static final String CODE = "123456";
    private static final String REFRESH_TOKEN = "5f0b1c2d3e4f50617283949506a7b8c9";
    private static final String ACCESS_TOKEN = "header.payload.signature";

    private static final VerifiedSession VERIFIED_SESSION = new VerifiedSession(
            UUID.fromString("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"),
            UUID.fromString("12121212-3434-5656-7878-909090909090"),
            REFRESH_TOKEN,
            ACCESS_TOKEN);

    private static final String EXPECTED_RESPONSE = """
            {"user":{"id":"aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"},
             "session":{"id":"12121212-3434-5656-7878-909090909090",
                        "refreshToken":"5f0b1c2d3e4f50617283949506a7b8c9",
                        "accessToken":"header.payload.signature"}}""";

    private static final String READY_BODY = """
            {"challengeId":"11111111-2222-3333-4444-555555555555","code":"123456"}""";

    private static final String UNKNOWN_FIELDS_BODY = """
            {"challengeId":"11111111-2222-3333-4444-555555555555",
             "code":"123456",
             "userId":"77777777-7777-7777-7777-777777777777",
             "sessionId":"88888888-8888-8888-8888-888888888888",
             "accessToken":"forged.access.token",
             "refreshToken":"forged-refresh-token",
             "attemptsLeft":99,
             "createdUser":true}""";

    private final VerifyAuthChallengeService service = mock(VerifyAuthChallengeService.class);
    private final MockMvc mockMvc = MockMvcBuilders
            .standaloneSetup(new AuthChallengeVerifyController(service))
            .setControllerAdvice(new GlobalExceptionHandler())
            .build();

    private ResultActions response;

    public void givenUsecaseVerifiesTheCode() {
        when(service.verify(any())).thenReturn(VERIFIED_SESSION);
    }

    public void whenClientSubmitsTheCode() throws Exception {
        post(READY_BODY);
    }

    public void whenClientSubmitsTheCodeWithUnknownFields() throws Exception {
        post(UNKNOWN_FIELDS_BODY);
    }

    public void assertSessionIsAnsweredWithOnlyItsOwnFields() throws Exception {
        response.andExpect(status().isOk()).andExpect(content().json(EXPECTED_RESPONSE, true));
    }

    public void assertUsecaseReceivedTheTranslatedRequest() {
        ArgumentCaptor<VerifyChallengeRequest> captor = ArgumentCaptor.forClass(VerifyChallengeRequest.class);
        verify(service).verify(captor.capture());
        assertThat(captor.getValue()).isEqualTo(new VerifyChallengeRequest(CHALLENGE_ID, CODE));
    }

    private void post(String body) throws Exception {
        response = mockMvc.perform(MockMvcRequestBuilders.post(VERIFY_PATH)
                .contentType(MediaType.APPLICATION_JSON)
                .content(body));
    }
}
