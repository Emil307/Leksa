package com.uwords.usecase.testing.fakes;

import com.uwords.domain.auth.code.CodeGenerator;
import java.util.ArrayList;
import java.util.List;

public class StubCodeGenerator implements CodeGenerator {

    public final List<Integer> requestedLengths = new ArrayList<>();

    private final String code;

    public StubCodeGenerator(String code) {
        this.code = code;
    }

    @Override
    public String generate(int length) {
        requestedLengths.add(length);
        return code;
    }
}
