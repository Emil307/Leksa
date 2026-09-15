package com.uwords.adapter.cache.testing.fakes;

import java.util.List;

public record EvalCall(String script, List<String> keys, List<String> args) {
}
