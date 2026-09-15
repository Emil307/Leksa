package com.uwords.e2e.stub;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;

public final class ChallengeHandler {

    public static final String START_PATH = "/api/v1/auth/challenge/start";
    public static final String VERIFY_PATH = "/api/v1/auth/challenge/verify";

    private final ChallengeStore store;

    public ChallengeHandler(ChallengeStore store) {
        this.store = store;
    }

    public StubResponse handle(String method, String path, String rawBody) {
        if (!"POST".equals(method)) {
            return StubResponse.error(405, "METHOD_NOT_ALLOWED", "Only POST is supported", Map.of());
        }
        Map<String, Object> body = Json.parseObject(rawBody);
        if (START_PATH.equals(path)) {
            return start(method, path, body);
        }
        if (VERIFY_PATH.equals(path)) {
            return verify(method, path, body);
        }
        return StubResponse.error(404, "NOT_FOUND", "Unknown path " + path, Map.of());
    }

    private StubResponse start(String method, String path, Map<String, Object> body) {
        String email = String.valueOf(body.get("email"));
        store.record(email, new RecordedRequest(method, path, body));
        Instant now = Instant.now();
        long retryAfter = store.remainingCooldownSeconds(email, now);
        if (retryAfter > 0) {
            return StubResponse.error(409, "CONFLICT", "Resend cooldown is active", Map.of("retryAfterSeconds", retryAfter));
        }
        IssuedChallenge challenge = store.issue(email, now);
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("challengeId", challenge.challengeId());
        payload.put("challengeType", "EMAIL_CODE");
        payload.put("expiresAt", challenge.expiresAt().toString());
        return StubResponse.ok(payload);
    }

    private StubResponse verify(String method, String path, Map<String, Object> body) {
        Object challengeId = body.get("challengeId");
        Optional<IssuedChallenge> challenge = store.byId(challengeId instanceof String id ? id : null);
        store.record(challenge.map(IssuedChallenge::email).orElse(null), new RecordedRequest(method, path, body));
        Object code = body.get("code");
        if (!(challengeId instanceof String) || !(code instanceof String)) {
            return StubResponse.error(400, "VALIDATION_FAILED", "challengeId and code must be strings", Map.of());
        }
        if (challenge.isEmpty() || !store.isCurrent(challenge.get()) || !challenge.get().code().equals(code)) {
            return StubResponse.error(401, "UNAUTHORIZED", "Code rejected", Map.of());
        }
        if (Instant.now().isAfter(challenge.get().expiresAt())) {
            return StubResponse.error(401, "UNAUTHORIZED", "Code expired", Map.of());
        }
        IssuedSession session = store.openSession(challenge.get().email());
        Map<String, Object> sessionPayload = new LinkedHashMap<>();
        sessionPayload.put("id", session.sessionId());
        sessionPayload.put("accessToken", session.accessToken());
        sessionPayload.put("refreshToken", session.refreshToken());
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("user", Map.of("id", session.userId()));
        payload.put("session", sessionPayload);
        return StubResponse.ok(payload);
    }
}
