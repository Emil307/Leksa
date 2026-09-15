package com.uwords.application;

import com.uwords.application.testing.statements.AccessTokenDecoderStatements;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class JwtAccessTokenDecoderTest {

    private AccessTokenDecoderStatements statements;

    @BeforeEach
    void createStatements() {
        statements = new AccessTokenDecoderStatements();
    }

    @Test
    void shouldReturnEveryClaimOfACorrectlySignedToken() {
        statements.givenCorrectlySignedTokenCarryingAnUnknownClaim();

        statements.whenTheTokenIsDecoded();

        statements.assertDecodedClaimsAreTheSignedOnes();
    }

    @Test
    void shouldReturnTheClaimsOfATokenWhoseExpiryHasAlreadyPassed() {
        statements.givenCorrectlySignedTokenWhoseExpiryHasPassed();

        statements.whenTheTokenIsDecoded();

        statements.assertDecodedClaimsAreTheSignedOnes();
    }

    @Test
    void shouldReturnTheClaimsOfATokenAddressedToAnotherAudience() {
        statements.givenCorrectlySignedTokenAddressedToAnotherAudience();

        statements.whenTheTokenIsDecoded();

        statements.assertDecodedClaimsAreTheSignedOnes();
    }

    @Test
    void shouldRefuseATokenSignedWithAnotherSecret() {
        statements.givenTokenSignedWithAnotherSecret();

        statements.whenDecodingIsAttempted();

        statements.assertDecodingRefusedAsSignature();
    }

    @Test
    void shouldRefuseATokenWhoseSignatureWasTamperedWith() {
        statements.givenTokenWhoseSignatureWasTamperedWith();

        statements.whenDecodingIsAttempted();

        statements.assertDecodingRefusedAsSignature();
    }

    @Test
    void shouldRefuseATokenDeclaringAnotherAlgorithm() {
        statements.givenTokenDeclaringAnotherAlgorithm();

        statements.whenDecodingIsAttempted();

        statements.assertDecodingRefusedAsSignature();
    }

    @Test
    void shouldRefuseAnUnsignedToken() {
        statements.givenUnsignedToken();

        statements.whenDecodingIsAttempted();

        statements.assertDecodingRefusedAsSignature();
    }

    @Test
    void shouldRefuseAStructurallyMalformedToken() {
        statements.givenStructurallyMalformedToken();

        statements.whenDecodingIsAttempted();

        statements.assertDecodingRefusedAsSignature();
    }
}
