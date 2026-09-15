package com.uwords.application;

import com.uwords.application.testing.statements.SecurityTokenStatements;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SecurityTokenTest {

    private SecurityTokenStatements statements;

    @BeforeEach
    void createStatements() {
        statements = new SecurityTokenStatements();
    }

    @Test
    void shouldSignTheClaimsWithTheConfiguredSecret() {
        statements.givenClaimsForAUserSession();

        statements.whenTheAccessTokenIsIssued();

        statements.assertTheTokenCarriesTheSubjectSessionAndExpiry();
    }

    @Test
    void shouldCarryTheTokenIdAndTheApiAudienceAsTheOnlyOtherClaims() {
        statements.givenClaimsForAUserSession();

        statements.whenTheAccessTokenIsIssued();

        statements.assertTheTokenCarriesTheTokenIdAndTheApiAudience();
    }

    @Test
    void shouldIssueDifferentTokensForDifferentTokenIds() {
        statements.givenTwoClaimSetsDifferingOnlyByTokenId();

        statements.whenBothAccessTokensAreIssued();

        statements.assertTheAccessTokensDiffer();
    }

    @Test
    void shouldIssueATokenTheApiGuardAccepts() {
        statements.givenClaimsForAUserSession();
        statements.whenTheAccessTokenIsIssued();

        statements.whenTheIssuedTokenIsPresentedToTheGuard();

        statements.assertTheGuardReadsTheIssuedClaims();
    }

    @Test
    void shouldNotVerifyWithAForeignSecret() {
        statements.givenClaimsForAUserSession();
        statements.whenTheAccessTokenIsIssued();

        statements.whenTheTokenIsVerifiedWithAnotherSecret();

        statements.assertTheVerificationIsRefusedAsABadSignature();
    }

    @Test
    void shouldGenerateAnOpaqueToken() {
        statements.whenTwoRefreshTokensAreGenerated();

        statements.assertTheRefreshTokensAreOpaque();
    }

    @Test
    void shouldNeverRepeatAGeneratedToken() {
        statements.whenTwoRefreshTokensAreGenerated();

        statements.assertTheRefreshTokensDiffer();
    }
}
