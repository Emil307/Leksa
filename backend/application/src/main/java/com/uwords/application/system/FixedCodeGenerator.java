package com.uwords.application.system;

import com.uwords.domain.auth.code.CodeGenerator;

public class FixedCodeGenerator implements CodeGenerator {

    private static final String LENGTH_MISMATCH = "Fixed challenge code %s does not have the configured length %d";

    private final String code;

    public FixedCodeGenerator(String code) {
        this.code = code;
    }

    @Override
    public String generate(int length) {
        if (code.length() != length) {
            throw new IllegalArgumentException(LENGTH_MISMATCH.formatted(code, length));
        }
        return code;
    }
}
