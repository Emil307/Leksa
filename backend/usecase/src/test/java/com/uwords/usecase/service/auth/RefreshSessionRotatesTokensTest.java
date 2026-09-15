package com.uwords.usecase.service.auth;

import com.uwords.usecase.testing.statements.RefreshSessionStatements;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class RefreshSessionRotatesTokensTest {

    private RefreshSessionStatements statements;

    @BeforeEach
    void createStatements() {
        statements = new RefreshSessionStatements();
    }

    @Test
    void shouldAnswerWithTheSameSessionAndANewTokenPair() {
        statements.givenSignedInUserHoldsALiveSession();

        statements.whenClientRefreshesTokensWithThatSessionsRefreshToken();

        statements.assertResponseKeepsTheSessionIdentityAndCarriesANewPair();
        statements.assertAccessTokenIsSignedForTheSameUserAndSession();
    }

    @Test
    void shouldMintThePairAndThenWriteExactlyOneRotation() {
        statements.givenSignedInUserHoldsALiveSession();

        statements.whenClientRefreshesTokensWithThatSessionsRefreshToken();

        statements.assertPairIsMintedBeforeTheWrite();
        statements.assertExactlyOneConditionalRotationIsWritten();
    }

    @Test
    void shouldRotateTheExistingRowWithoutCreatingANewOne() {
        statements.givenSignedInUserHoldsALiveSession();

        statements.whenClientRefreshesTokensWithThatSessionsRefreshToken();

        statements.assertNoNewSessionRowIsCreated();
    }

    @Test
    void shouldMintTheRefreshedAccessTokenWithAFreshTokenId() {
        statements.givenSignedInUserHoldsALiveSession();

        statements.whenClientRefreshesTokensWithThatSessionsRefreshToken();

        statements.assertRefreshedAccessTokenCarriesAFreshTokenId();
    }
}
