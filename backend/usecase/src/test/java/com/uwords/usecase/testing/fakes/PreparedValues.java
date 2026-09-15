package com.uwords.usecase.testing.fakes;

import java.util.Deque;

final class PreparedValues {

    private PreparedValues() {
    }

    static <T> T take(Deque<T> remaining, String owner) {
        if (remaining.isEmpty()) {
            throw new AssertionError(owner + " ran out of prepared values");
        }
        return remaining.removeFirst();
    }
}
