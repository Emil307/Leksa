package com.uwords.usecase.testing.statements;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.catchThrowable;

import com.uwords.domain.auth.failure.AuthFailureReason;
import com.uwords.domain.auth.failure.Unauthorized;
import com.uwords.domain.auth.user.User;
import com.uwords.domain.common.UnauthorizedException;
import com.uwords.usecase.AuthenticatedCaller;
import com.uwords.usecase.testing.fakes.FakeAccessTokenDecoder;
import com.uwords.usecase.testing.fakes.FakeActiveSessionRepository;
import com.uwords.usecase.testing.fakes.FakeUserRepository;
import com.uwords.usecase.testing.fakes.FixedClock;
import java.util.Map;
import org.assertj.core.api.ThrowableAssert.ThrowingCallable;

public class AuthStatements extends AuthArrangements {

    private static final String REASON_KEY = "reason";

    private User profileRead;
    private UnauthorizedException failure;

    public AuthStatements(
            FakeAccessTokenDecoder decoder,
            FakeActiveSessionRepository sessions,
            FakeUserRepository users,
            FixedClock clock) {
        super(decoder, sessions, users, clock);
    }

    public void whenTheRequestIsAuthenticated() {
        caller = authentication.authenticate(header);
    }

    public void whenTheOwnProfileIsRead() {
        whenTheRequestIsAuthenticated();
        profileRead = profile.read(caller);
    }

    public void whenAuthenticationIsAttempted() {
        capture(() -> authentication.authenticate(header));
    }

    public void whenTheOwnProfileReadIsAttempted() {
        whenTheRequestIsAuthenticated();
        capture(() -> profile.read(caller));
    }

    public void assertCallerIsTheTokenOwner() {
        assertThat(caller).isEqualTo(new AuthenticatedCaller(AuthData.USER_ID, AuthData.SESSION_ID));
    }

    public void assertProfileIsTheWholeStoredAccount() {
        assertThat(profileRead).isEqualTo(AuthData.STORED_USER);
    }

    public void assertAuthenticationRefusedAsHeader() {
        assertUniformRefusal(AuthFailureReason.HEADER);
    }

    public void assertAuthenticationRefusedAsSignature() {
        assertUniformRefusal(AuthFailureReason.SIGNATURE);
    }

    public void assertAuthenticationRefusedAsClaims() {
        assertUniformRefusal(AuthFailureReason.CLAIMS);
    }

    public void assertAuthenticationRefusedAsSession() {
        assertUniformRefusal(AuthFailureReason.SESSION);
    }

    public void assertAuthenticationRefusedAsLegacySession() {
        assertUniformRefusal(AuthFailureReason.LEGACY_SESSION);
    }

    public void assertAuthenticationRefusedAsStorage() {
        assertUniformRefusal(AuthFailureReason.STORAGE);
    }

    public void assertProfileRefusedAsAccount() {
        assertUniformRefusal(AuthFailureReason.ACCOUNT);
    }

    public void assertProfileRefusedAsStorage() {
        assertUniformRefusal(AuthFailureReason.STORAGE);
    }

    private void capture(ThrowingCallable attempt) {
        Throwable thrown = catchThrowable(attempt);
        assertThat(thrown).isInstanceOf(UnauthorizedException.class);
        failure = (UnauthorizedException) thrown;
    }

    private void assertUniformRefusal(AuthFailureReason reason) {
        assertThat(failure.getMessage()).isEqualTo(Unauthorized.UNAUTHORIZED_MESSAGE);
        assertThat(failure.payload()).isEqualTo(Map.of(REASON_KEY, reason.value()));
        assertThat(failure.exposeToUser()).isFalse();
    }
}
