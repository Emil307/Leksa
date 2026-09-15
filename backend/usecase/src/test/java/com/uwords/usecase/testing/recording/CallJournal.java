package com.uwords.usecase.testing.recording;

import java.util.ArrayList;
import java.util.List;

public class CallJournal {

    private final List<JournalEntry> calls;

    public CallJournal() {
        this(new ArrayList<>());
    }

    private CallJournal(List<JournalEntry> calls) {
        this.calls = calls;
    }

    public void record(String call) {
        record(call, null);
    }

    public void record(String call, Object payload) {
        calls.add(new JournalEntry(call, payload));
    }

    public List<JournalEntry> calls() {
        return List.copyOf(calls);
    }

    public CallJournal since(int start) {
        return new CallJournal(new ArrayList<>(calls.subList(start, calls.size())));
    }

    public List<String> names() {
        return calls.stream().map(JournalEntry::name).toList();
    }

    public List<Object> payloadsOf(String call) {
        return calls.stream()
                .filter(entry -> entry.name().equals(call))
                .map(JournalEntry::payload)
                .toList();
    }

    public Object payloadOf(String call) {
        return calls.stream()
                .filter(entry -> entry.name().equals(call))
                .findFirst()
                .map(JournalEntry::payload)
                .orElseThrow(() -> new AssertionError("CallJournal has no recorded call named " + call));
    }
}
