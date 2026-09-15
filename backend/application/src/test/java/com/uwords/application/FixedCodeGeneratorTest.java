package com.uwords.application;

import com.uwords.application.testing.statements.FixedCodeGeneratorStatements;
import org.junit.jupiter.api.Test;

class FixedCodeGeneratorTest {

    private final FixedCodeGeneratorStatements statements = new FixedCodeGeneratorStatements();

    @Test
    void shouldAlwaysIssueTheConfiguredCode() {
        statements.givenTheFixedCode("111111");

        statements.whenACodeOfLengthIsGenerated(6);
        statements.whenACodeOfLengthIsGenerated(6);

        statements.assertEveryIssuedCodeIs("111111");
    }

    @Test
    void shouldRefuseALengthThatDoesNotMatchTheConfiguredCode() {
        statements.givenTheFixedCode("111111");

        statements.assertGeneratingLengthIsRefused(4);
    }

    @Test
    void shouldPickTheFixedGeneratorOnlyWhenACodeIsConfigured() {
        statements.assertConfiguredGeneratorIsFixedFor("111111");
        statements.assertConfiguredGeneratorIsSecureFor("");
    }
}
