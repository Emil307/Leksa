package com.uwords.application.testing.statements;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.uwords.application.config.ChallengeProperties;
import com.uwords.application.config.CodeGeneratorConfiguration;
import com.uwords.application.system.FixedCodeGenerator;
import com.uwords.application.system.SecureNumericCodeGenerator;
import java.util.ArrayList;
import java.util.List;

public class FixedCodeGeneratorStatements {

    private FixedCodeGenerator generator;
    private final List<String> issued = new ArrayList<>();

    public void givenTheFixedCode(String code) {
        generator = new FixedCodeGenerator(code);
    }

    public void whenACodeOfLengthIsGenerated(int length) {
        issued.add(generator.generate(length));
    }

    public void assertEveryIssuedCodeIs(String code) {
        assertThat(issued).isNotEmpty().containsOnly(code);
    }

    public void assertGeneratingLengthIsRefused(int length) {
        assertThatThrownBy(() -> generator.generate(length)).isInstanceOf(IllegalArgumentException.class);
    }

    public void assertConfiguredGeneratorIsFixedFor(String fixedCode) {
        assertThat(new CodeGeneratorConfiguration().codeGenerator(propertiesWith(fixedCode)))
                .isInstanceOf(FixedCodeGenerator.class);
    }

    public void assertConfiguredGeneratorIsSecureFor(String fixedCode) {
        assertThat(new CodeGeneratorConfiguration().codeGenerator(propertiesWith(fixedCode)))
                .isInstanceOf(SecureNumericCodeGenerator.class);
    }

    private static ChallengeProperties propertiesWith(String fixedCode) {
        return new ChallengeProperties(300, 5, 60, 60, 6, fixedCode);
    }
}
