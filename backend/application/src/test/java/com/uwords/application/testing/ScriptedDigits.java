package com.uwords.application.testing;

import java.util.Iterator;
import java.util.List;
import java.util.random.RandomGenerator;

public class ScriptedDigits implements RandomGenerator {

    private final Iterator<Integer> digits;

    public ScriptedDigits(List<Integer> digits) {
        this.digits = digits.iterator();
    }

    @Override
    public int nextInt(int bound) {
        return digits.next();
    }

    @Override
    public long nextLong() {
        throw new UnsupportedOperationException();
    }
}
