package com.uwords.application.testing.statements;

import static org.assertj.core.api.Assertions.assertThat;

import com.uwords.application.system.SecureNumericCodeGenerator;
import com.uwords.application.testing.ScriptedDigits;
import java.util.List;

public class CodeGeneratorStatements {

    private static final int REQUESTED_LENGTH = 6;
    private static final List<Integer> LEADING_ZERO_DIGITS = List.of(0, 0, 4, 3, 2, 1);
    private static final String EXPECTED_LEADING_ZERO_CODE = "004321";
    private static final String DIGITS_ONLY = "\\d+";

    private SecureNumericCodeGenerator generator = new SecureNumericCodeGenerator();
    private String generated;

    public void givenTheRandomSourceYieldsALeadingZero() {
        generator = new SecureNumericCodeGenerator(new ScriptedDigits(LEADING_ZERO_DIGITS));
    }

    public void whenACodeOfTheRequestedLengthIsGenerated() {
        generated = generator.generate(REQUESTED_LENGTH);
    }

    public void assertTheCodeIsADigitStringOfTheRequestedLength() {
        assertThat(generated).hasSize(REQUESTED_LENGTH).matches(DIGITS_ONLY);
    }

    public void assertTheCodeKeepsItsLeadingZeros() {
        assertThat(generated).isEqualTo(EXPECTED_LEADING_ZERO_CODE);
    }
}
