package com.uwords.application;

import com.uwords.application.testing.statements.CodeGeneratorStatements;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class CodeGeneratorTest {

    private CodeGeneratorStatements statements;

    @BeforeEach
    void createStatements() {
        statements = new CodeGeneratorStatements();
    }

    @Test
    void shouldGenerateADigitStringOfTheRequestedLength() {
        statements.whenACodeOfTheRequestedLengthIsGenerated();

        statements.assertTheCodeIsADigitStringOfTheRequestedLength();
    }

    @Test
    void shouldKeepLeadingZerosInTheGeneratedCode() {
        statements.givenTheRandomSourceYieldsALeadingZero();

        statements.whenACodeOfTheRequestedLengthIsGenerated();

        statements.assertTheCodeKeepsItsLeadingZeros();
        statements.assertTheCodeIsADigitStringOfTheRequestedLength();
    }
}
