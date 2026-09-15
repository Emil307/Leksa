package com.uwords.adapter.cache.testing.fakes;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Deque;
import java.util.List;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.RedisScript;

public class FakeStringRedisTemplate extends StringRedisTemplate {

    private final Deque<Object> results = new ArrayDeque<>();
    private final List<EvalCall> calls = new ArrayList<>();

    public void willReturn(Object result) {
        results.addLast(result);
    }

    public List<EvalCall> calls() {
        return calls;
    }

    @Override
    @SuppressWarnings("unchecked")
    public <T> T execute(RedisScript<T> script, List<String> keys, Object... args) {
        calls.add(new EvalCall(script.getScriptAsString(), List.copyOf(keys), textArgs(args)));
        return (T) results.pollFirst();
    }

    private List<String> textArgs(Object... args) {
        return Arrays.stream(args).map(String::valueOf).toList();
    }
}
