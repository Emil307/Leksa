package com.uwords.application;

import com.uwords.application.testing.statements.SigningSecretStatements;
import org.junit.jupiter.api.Test;

class SigningSecretBootTest {

    @Test
    void shouldRefuseToBootWithoutASigningSecret() {
        SigningSecretStatements statements = new SigningSecretStatements();
        statements.givenABlankSigningSecret();

        statements.whenBuildingTheApplicationIsAttempted();

        statements.assertBootRefusedTheBlankSigningSecret();
    }
}
