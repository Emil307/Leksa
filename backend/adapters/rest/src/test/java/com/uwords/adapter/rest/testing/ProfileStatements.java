package com.uwords.adapter.rest.testing;

import com.uwords.adapter.rest.controller.ProfileController;
import com.uwords.adapter.rest.error.GlobalExceptionHandler;
import com.uwords.adapter.rest.security.AccessTokenInterceptor;
import com.uwords.adapter.rest.security.AuthenticatedCallerArgumentResolver;
import com.uwords.domain.auth.failure.AuthFailureReason;
import com.uwords.domain.auth.failure.Unauthorized;
import com.uwords.domain.auth.user.User;
import com.uwords.usecase.AuthenticatedCaller;
import com.uwords.usecase.service.auth.AuthenticateRequestService;
import com.uwords.usecase.service.profile.ReadUserProfileService;
import java.util.LinkedHashMap;
import java.util.Map;
import org.mockito.ArgumentCaptor;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultActions;
import org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import static com.uwords.adapter.rest.testing.ProfileData.CALLER;
import static com.uwords.adapter.rest.testing.ProfileData.FULL_PROFILE_BODY;
import static com.uwords.adapter.rest.testing.ProfileData.FULL_USER;
import static com.uwords.adapter.rest.testing.ProfileData.OTHER_USER_ID;
import static com.uwords.adapter.rest.testing.ProfileData.PROFILE_PATH;
import static com.uwords.adapter.rest.testing.ProfileData.SPARSE_PROFILE_BODY;
import static com.uwords.adapter.rest.testing.ProfileData.SPARSE_USER;
import static com.uwords.adapter.rest.testing.ProfileData.UNAUTHORIZED_BODY;
import static com.uwords.adapter.rest.testing.ProfileData.VALID_HEADER;
import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

public class ProfileStatements {

    private static final String AUTHORIZATION_HEADER = "Authorization";
    private static final String FOREIGN_IDENTIFIER_PARAMETER = "userId";

    private final AuthenticateRequestService authenticateService = mock(AuthenticateRequestService.class);
    private final ReadUserProfileService profileService = mock(ReadUserProfileService.class);
    private final Map<String, String> parameters = new LinkedHashMap<>();

    private String header = VALID_HEADER;
    private ResultActions response;

    public ProfileStatements() {
        when(authenticateService.authenticate(any())).thenReturn(CALLER);
    }

    public void givenAccountWithEveryFieldFilled() {
        when(profileService.read(any())).thenReturn(FULL_USER);
    }

    public void givenAccountWithOnlyTheRequiredColumns() {
        when(profileService.read(any())).thenReturn(SPARSE_USER);
    }

    public void givenNoAuthorizationHeader() {
        header = null;
    }

    public void givenAForeignUserIdInTheQuery() {
        parameters.put(FOREIGN_IDENTIFIER_PARAMETER, OTHER_USER_ID.toString());
    }

    public void givenTheGuardRefusesTheRequest() {
        when(authenticateService.authenticate(any()))
                .thenThrow(Unauthorized.of(AuthFailureReason.SESSION));
    }

    public void whenTheProfileIsRequested() throws Exception {
        MockHttpServletRequestBuilder request = MockMvcRequestBuilders.get(PROFILE_PATH);
        parameters.forEach(request::param);
        if (header != null) {
            request.header(AUTHORIZATION_HEADER, header);
        }
        response = buildMockMvc().perform(request);
    }

    public void assertAnsweredTheWholeAccountAtTheBodyRoot() throws Exception {
        assertAnswered(200, FULL_PROFILE_BODY);
    }

    public void assertAnsweredTheAccountWithUnsetColumnsAsJsonNulls() throws Exception {
        assertAnswered(200, SPARSE_PROFILE_BODY);
    }

    public void assertTheRawAuthorizationHeaderReachedTheGuard() throws Exception {
        response.andExpect(status().isOk());
        assertThat(receivedHeader()).isEqualTo(VALID_HEADER);
    }

    public void assertTheAbsentAuthorizationHeaderReachedTheGuardAsNull() throws Exception {
        response.andExpect(status().isOk());
        assertThat(receivedHeader()).isNull();
    }

    public void assertAnsweredTheAuthenticatedCallersAccountOnly() throws Exception {
        assertAnswered(200, FULL_PROFILE_BODY);
        ArgumentCaptor<AuthenticatedCaller> captor = ArgumentCaptor.forClass(AuthenticatedCaller.class);
        verify(profileService).read(captor.capture());
        assertThat(captor.getValue()).isEqualTo(CALLER);
    }

    public void assertAnsweredTheUniform401WithoutReadingAnyAccount() throws Exception {
        assertAnswered(401, UNAUTHORIZED_BODY);
        verifyNoInteractions(profileService);
    }

    private MockMvc buildMockMvc() {
        return MockMvcBuilders.standaloneSetup(new ProfileController(profileService))
                .addInterceptors(new AccessTokenInterceptor(authenticateService))
                .setCustomArgumentResolvers(new AuthenticatedCallerArgumentResolver())
                .setControllerAdvice(new GlobalExceptionHandler())
                .build();
    }

    private void assertAnswered(int httpStatus, String body) throws Exception {
        response.andExpect(status().is(httpStatus)).andExpect(content().json(body, true));
    }

    private String receivedHeader() {
        ArgumentCaptor<String> captor = ArgumentCaptor.forClass(String.class);
        verify(authenticateService).authenticate(captor.capture());
        return captor.getValue();
    }
}
