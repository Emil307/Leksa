package com.uwords.usecase.testing.statements;

import com.uwords.domain.auth.session.ActiveSession;
import com.uwords.domain.auth.session.BearerCredential;
import com.uwords.domain.auth.session.VerifiedAccessToken;
import com.uwords.usecase.AuthenticatedCaller;
import com.uwords.usecase.service.auth.AuthenticateRequestService;
import com.uwords.usecase.service.profile.ReadUserProfileService;
import com.uwords.usecase.testing.fakes.FakeAccessTokenDecoder;
import com.uwords.usecase.testing.fakes.FakeActiveSessionRepository;
import com.uwords.usecase.testing.fakes.FakeUserRepository;
import com.uwords.usecase.testing.fakes.FixedClock;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

public class AuthArrangements {

    protected final FakeAccessTokenDecoder decoder;
    protected final FakeActiveSessionRepository sessions;
    protected final FakeUserRepository users;
    protected final FixedClock clock;
    protected final AuthenticateRequestService authentication;
    protected final ReadUserProfileService profile;

    protected String header;
    protected AuthenticatedCaller caller;

    public AuthArrangements(
            FakeAccessTokenDecoder decoder,
            FakeActiveSessionRepository sessions,
            FakeUserRepository users,
            FixedClock clock) {
        this.decoder = decoder;
        this.sessions = sessions;
        this.users = users;
        this.clock = clock;
        this.authentication = new AuthenticateRequestService(decoder, sessions, clock);
        this.profile = new ReadUserProfileService(users);
    }

    public void givenActiveSessionAndValidToken() {
        registerToken(AuthData.VALID_TOKEN, AuthData.SESSION_ID, AuthData.USER_ID);
        registerSession(AuthData.SESSION_ID, AuthData.USER_ID, AuthData.SESSION_EXPIRES_AT);
        present(AuthData.VALID_TOKEN);
    }

    public void givenStoredAccountWithEveryFieldFilled() {
        users.users.put(AuthData.USER_ID, AuthData.STORED_USER);
    }

    public void givenSignedInCallerWithAStoredAccount() {
        givenActiveSessionAndValidToken();
        givenStoredAccountWithEveryFieldFilled();
    }

    public void givenNoAuthorizationHeader() {
        header = null;
    }

    public void givenAuthorizationHeaderOfAnotherScheme() {
        header = AuthData.OTHER_SCHEME + " " + AuthData.VALID_TOKEN;
    }

    public void givenTokenTheDecoderRejects() {
        present(AuthData.FORGED_TOKEN);
    }

    public void givenTokenWithoutEveryRequiredClaim() {
        Map<String, Object> claims = new LinkedHashMap<>();
        claims.put(VerifiedAccessToken.SUBJECT_CLAIM, AuthData.USER_ID.toString());
        claims.put(VerifiedAccessToken.SESSION_CLAIM, AuthData.SESSION_ID.toString());
        claims.put(VerifiedAccessToken.EXPIRY_CLAIM, AuthData.TOKEN_EXPIRES_AT.getEpochSecond());
        decoder.claims.put(AuthData.INCOMPLETE_TOKEN, claims);
        registerSession(AuthData.SESSION_ID, AuthData.USER_ID, AuthData.SESSION_EXPIRES_AT);
        present(AuthData.INCOMPLETE_TOKEN);
    }

    public void givenTheTokenLifetimeHasElapsed() {
        clock.set(AuthData.TOKEN_EXPIRES_AT);
    }

    public void givenSessionThatNeverExisted() {
        registerToken(AuthData.UNKNOWN_SESSION_TOKEN, AuthData.UNKNOWN_SESSION_ID, AuthData.USER_ID);
        present(AuthData.UNKNOWN_SESSION_TOKEN);
    }

    public void givenSessionOwnedByAnotherUser() {
        registerToken(AuthData.FOREIGN_SESSION_TOKEN, AuthData.FOREIGN_SESSION_ID, AuthData.USER_ID);
        registerSession(AuthData.FOREIGN_SESSION_ID, AuthData.OTHER_USER_ID, AuthData.SESSION_EXPIRES_AT);
        present(AuthData.FOREIGN_SESSION_TOKEN);
    }

    public void givenSessionWhoseLifetimeHasElapsed() {
        registerToken(AuthData.SHORT_SESSION_TOKEN, AuthData.SHORT_SESSION_ID, AuthData.USER_ID);
        registerSession(
                AuthData.SHORT_SESSION_ID, AuthData.USER_ID, AuthData.SHORT_SESSION_EXPIRES_AT);
        present(AuthData.SHORT_SESSION_TOKEN);
        clock.set(AuthData.SHORT_SESSION_EXPIRES_AT);
    }

    public void givenSessionRowWithoutARecordedLifetime() {
        registerToken(AuthData.LEGACY_SESSION_TOKEN, AuthData.LEGACY_SESSION_ID, AuthData.USER_ID);
        sessions.legacyIds.add(AuthData.LEGACY_SESSION_ID);
        present(AuthData.LEGACY_SESSION_TOKEN);
    }

    public void givenSessionStorageIsUnreachable() {
        sessions.unavailable = true;
    }

    public void givenAccountStorageIsUnreachable() {
        users.unavailable = true;
    }

    public void givenAccountRowIsAbsent() {
        users.users.clear();
    }

    private void registerToken(String token, UUID sessionId, UUID userId) {
        Map<String, Object> claims = new LinkedHashMap<>();
        claims.put(VerifiedAccessToken.SUBJECT_CLAIM, userId.toString());
        claims.put(VerifiedAccessToken.SESSION_CLAIM, sessionId.toString());
        claims.put(VerifiedAccessToken.TOKEN_ID_CLAIM, AuthData.TOKEN_ID.toString());
        claims.put(VerifiedAccessToken.EXPIRY_CLAIM, AuthData.TOKEN_EXPIRES_AT.getEpochSecond());
        claims.put(VerifiedAccessToken.AUDIENCE_CLAIM, VerifiedAccessToken.API_AUDIENCE);
        decoder.claims.put(token, claims);
    }

    private void registerSession(UUID sessionId, UUID userId, Instant expiresAt) {
        sessions.sessions.put(sessionId, new ActiveSession(sessionId, userId, expiresAt));
    }

    private void present(String token) {
        header = BearerCredential.BEARER_SCHEME + " " + token;
    }
}
