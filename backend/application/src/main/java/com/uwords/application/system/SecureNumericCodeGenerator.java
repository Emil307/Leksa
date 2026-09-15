package com.uwords.application.system;

import com.uwords.domain.auth.code.CodeGenerator;
import java.security.SecureRandom;
import java.util.random.RandomGenerator;

public class SecureNumericCodeGenerator implements CodeGenerator {

    private static final int DECIMAL_BASE = 10;

    private final RandomGenerator digits;

    public SecureNumericCodeGenerator() {
        this(new SecureRandom());
    }

    public SecureNumericCodeGenerator(RandomGenerator digits) {
        this.digits = digits;
    }

    @Override
    public String generate(int length) {
        StringBuilder code = new StringBuilder(length);
        for (int position = 0; position < length; position++) {
            code.append(digits.nextInt(DECIMAL_BASE));
        }
        return code.toString();
    }
}
