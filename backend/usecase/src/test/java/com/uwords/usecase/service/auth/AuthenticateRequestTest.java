package com.uwords.usecase.service.auth;

import com.uwords.usecase.testing.fakes.FakeAccessTokenDecoder;
import com.uwords.usecase.testing.fakes.FakeActiveSessionRepository;
import com.uwords.usecase.testing.fakes.FakeUserRepository;
import com.uwords.usecase.testing.fakes.FixedClock;
import com.uwords.usecase.testing.statements.AuthData;
import com.uwords.usecase.testing.statements.AuthStatements;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class AuthenticateRequestTest {

    private AuthStatements statements;

    @BeforeEach
    void createStatements() {
        statements = new AuthStatements(
                new FakeAccessTokenDecoder(),
                new FakeActiveSessionRepository(),
                new FakeUserRepository(),
                new FixedClock(AuthData.NOW));
    }

    @Test
    void shouldIdentifyTheCallerBehindALiveSession() {
        statements.givenActiveSessionAndValidToken();

        statements.whenTheRequestIsAuthenticated();

        statements.assertCallerIsTheTokenOwner();
    }

    @Test
    void shouldRefuseWhenTheAuthorizationHeaderIsAbsent() {
        statements.givenNoAuthorizationHeader();

        statements.whenAuthenticationIsAttempted();

        statements.assertAuthenticationRefusedAsHeader();
    }

    @Test
    void shouldRefuseWhenTheAuthorizationSchemeIsNotBearer() {
        statements.givenAuthorizationHeaderOfAnotherScheme();

        statements.whenAuthenticationIsAttempted();

        statements.assertAuthenticationRefusedAsHeader();
    }

    @Test
    void shouldRefuseWhenTheDecoderRejectsTheToken() {
        statements.givenTokenTheDecoderRejects();

        statements.whenAuthenticationIsAttempted();

        statements.assertAuthenticationRefusedAsSignature();
    }

    @Test
    void shouldRefuseWhenARequiredClaimIsMissing() {
        statements.givenTokenWithoutEveryRequiredClaim();

        statements.whenAuthenticationIsAttempted();

        statements.assertAuthenticationRefusedAsClaims();
    }

    @Test
    void shouldRefuseWhenTheTokenLifetimeHasElapsed() {
        statements.givenActiveSessionAndValidToken();
        statements.givenTheTokenLifetimeHasElapsed();

        statements.whenAuthenticationIsAttempted();

        statements.assertAuthenticationRefusedAsSession();
    }

    @Test
    void shouldRefuseWhenTheSessionNeverExisted() {
        statements.givenSessionThatNeverExisted();

        statements.whenAuthenticationIsAttempted();

        statements.assertAuthenticationRefusedAsSession();
    }

    @Test
    void shouldRefuseWhenTheSessionBelongsToAnotherUser() {
        statements.givenSessionOwnedByAnotherUser();

        statements.whenAuthenticationIsAttempted();

        statements.assertAuthenticationRefusedAsSession();
    }

    @Test
    void shouldRefuseWhenTheSessionLifetimeHasElapsed() {
        statements.givenSessionWhoseLifetimeHasElapsed();

        statements.whenAuthenticationIsAttempted();

        statements.assertAuthenticationRefusedAsSession();
    }

    @Test
    void shouldRefuseWhenTheSessionRowHasNoLifetime() {
        statements.givenSessionRowWithoutARecordedLifetime();

        statements.whenAuthenticationIsAttempted();

        statements.assertAuthenticationRefusedAsLegacySession();
    }

    @Test
    void shouldRefuseWhenSessionStorageIsUnreachable() {
        statements.givenActiveSessionAndValidToken();
        statements.givenSessionStorageIsUnreachable();

        statements.whenAuthenticationIsAttempted();

        statements.assertAuthenticationRefusedAsStorage();
    }
}
