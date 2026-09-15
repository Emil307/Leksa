package com.uwords.adapter.rest.testing;

import com.uwords.adapter.rest.controller.AuthTokenController;
import com.uwords.adapter.rest.error.GlobalExceptionHandler;
import com.uwords.usecase.service.auth.RefreshSessionRequest;
import com.uwords.usecase.service.auth.RefreshSessionTokensService;
import com.uwords.usecase.service.auth.RotatedSessionTokens;
import java.util.UUID;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultActions;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

public class RefreshSessionStatements {

    private static final String REFRESH_PATH = "/api/v1/auth/token/refresh";
    private static final String PRESENTED_REFRESH_TOKEN = "0a1b2c3d4e5f60718293a4b5c6d7e8f9";
    private static final String ROTATED_REFRESH_TOKEN = "f9e8d7c6b5a49382716059f4e3d2c1b0";
    private static final String ROTATED_ACCESS_TOKEN = "rotated.payload.signature";
    private static final RefreshSessionRequest EXPECTED_REQUEST =
            new RefreshSessionRequest(PRESENTED_REFRESH_TOKEN);

    private static final RotatedSessionTokens ROTATED_SESSION = new RotatedSessionTokens(
            UUID.fromString("12121212-3434-5656-7878-909090909090"),
            ROTATED_REFRESH_TOKEN,
            ROTATED_ACCESS_TOKEN);

    private static final String EXPECTED_RESPONSE = """
            {"session":{"id":"12121212-3434-5656-7878-909090909090",
                        "refreshToken":"f9e8d7c6b5a49382716059f4e3d2c1b0",
                        "accessToken":"rotated.payload.signature"}}""";

    private static final String REFRESH_BODY = """
            {"refreshToken":"0a1b2c3d4e5f60718293a4b5c6d7e8f9"}""";

    private final RefreshSessionTokensService service = mock(RefreshSessionTokensService.class);
    private final MockMvc mockMvc = MockMvcBuilders
            .standaloneSetup(new AuthTokenController(service))
            .setControllerAdvice(new GlobalExceptionHandler())
            .build();

    private ResultActions response;

    public void givenUsecaseRotatesTheSession() {
        when(service.refresh(eq(EXPECTED_REQUEST))).thenReturn(ROTATED_SESSION);
    }

    public void whenClientRefreshesTheTokens() throws Exception {
        response = mockMvc.perform(MockMvcRequestBuilders.post(REFRESH_PATH)
                .contentType(MediaType.APPLICATION_JSON)
                .content(REFRESH_BODY));
    }

    public void assertRotatedSessionIsAnsweredWithOnlyItsOwnFields() throws Exception {
        response.andExpect(status().isOk()).andExpect(content().json(EXPECTED_RESPONSE, true));
    }

    public void assertUsecaseReceivedTheTranslatedRequest() {
        verify(service).refresh(eq(EXPECTED_REQUEST));
    }
}
