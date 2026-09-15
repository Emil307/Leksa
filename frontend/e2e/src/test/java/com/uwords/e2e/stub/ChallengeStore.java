package com.uwords.e2e.stub;

import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

public final class ChallengeStore {

    public static final Duration CHALLENGE_TTL = Duration.ofSeconds(300);
    public static final Duration RESEND_COOLDOWN = Duration.ofSeconds(60);
    private static final String UNKNOWN_EMAIL = "unknown";

    private final Map<String, IssuedChallenge> challengesByEmail = new ConcurrentHashMap<>();
    private final Map<String, IssuedChallenge> challengesById = new ConcurrentHashMap<>();
    private final Map<String, IssuedSession> sessionsByEmail = new ConcurrentHashMap<>();
    private final Map<String, List<RecordedRequest>> journal = new ConcurrentHashMap<>();

    public synchronized long remainingCooldownSeconds(String email, Instant now) {
        IssuedChallenge previous = challengesByEmail.get(email);
        if (previous == null) {
            return 0;
        }
        Instant cooldownEnd = previous.issuedAt().plus(RESEND_COOLDOWN);
        return Math.max(0, Duration.between(now, cooldownEnd).toSeconds());
    }

    public synchronized IssuedChallenge issue(String email, Instant now) {
        String challengeId = UUID.randomUUID().toString();
        IssuedChallenge challenge = new IssuedChallenge(challengeId, email, deterministicCode(challengeId), now, now.plus(CHALLENGE_TTL));
        challengesByEmail.put(email, challenge);
        challengesById.put(challengeId, challenge);
        return challenge;
    }

    public Optional<IssuedChallenge> byId(String challengeId) {
        return Optional.ofNullable(challengeId).map(challengesById::get);
    }

    public Optional<IssuedChallenge> byEmail(String email) {
        return Optional.ofNullable(challengesByEmail.get(email));
    }

    public boolean isCurrent(IssuedChallenge challenge) {
        return challenge.equals(challengesByEmail.get(challenge.email()));
    }

    public IssuedSession openSession(String email) {
        IssuedSession session = new IssuedSession(
                UUID.randomUUID().toString(),
                UUID.randomUUID().toString(),
                "access-" + UUID.randomUUID(),
                "refresh-" + UUID.randomUUID());
        sessionsByEmail.put(email, session);
        return session;
    }

    public Optional<IssuedSession> sessionOf(String email) {
        return Optional.ofNullable(sessionsByEmail.get(email));
    }

    public void record(String email, RecordedRequest request) {
        journal.computeIfAbsent(email == null ? UNKNOWN_EMAIL : email, key -> new CopyOnWriteArrayList<>()).add(request);
    }

    public List<RecordedRequest> requestsOf(String email) {
        return List.copyOf(journal.getOrDefault(email, List.of()));
    }

    static String deterministicCode(String challengeId) {
        int digits = Math.floorMod(challengeId.hashCode(), 1_000_000);
        return String.format("%06d", digits);
    }
}
