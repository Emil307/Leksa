package com.uwords.adapter.rest.testing;

import com.uwords.domain.auth.challenge.ChallengeType;
import com.uwords.usecase.service.auth.StartChallengeRequest;
import com.uwords.usecase.service.auth.StartedChallenge;
import java.time.Instant;
import java.util.UUID;

public final class StartChallengeData {

    public static final String START_PATH = "/api/v1/auth/challenge/start";
    public static final String EMAIL = "user@example.com";
    public static final String CHALLENGE_TYPE = "EMAIL_CODE";
    public static final int RETRY_AFTER_SECONDS = 42;
    public static final String VALIDATION_MESSAGE = "Challenge credential and type are required";
    public static final String CONFLICT_MESSAGE = "Verification code was already requested";
    public static final String UNAVAILABLE_DETAIL = "redis timed out on swap_challenge";

    public static final StartedChallenge STARTED_CHALLENGE = new StartedChallenge(
            UUID.fromString("11111111-2222-3333-4444-555555555555"),
            ChallengeType.EMAIL_CODE,
            Instant.parse("2026-08-16T12:00:00Z"));

    public static final StartChallengeRequest EXPECTED_USECASE_REQUEST =
            new StartChallengeRequest(EMAIL, CHALLENGE_TYPE);
    public static final StartChallengeRequest EMPTY_USECASE_REQUEST = new StartChallengeRequest("", "");

    public static final String EXPECTED_RESPONSE = """
            {"challengeId":"11111111-2222-3333-4444-555555555555",
             "challengeType":"EMAIL_CODE",
             "expiresAt":"2026-08-16T12:00:00Z"}""";

    public static final String VALIDATION_ENVELOPE = """
            {"code":"VALIDATION_FAILED","message":"Challenge credential and type are required","payload":{}}""";

    public static final String CONFLICT_ENVELOPE = """
            {"code":"CONFLICT",
             "message":"Verification code was already requested",
             "payload":{"retryAfterSeconds":42}}""";

    public static final String UNAVAILABLE_ENVELOPE = """
            {"code":"UNAVAILABLE","message":"Request could not be processed","payload":{}}""";

    public static final String READY_BODY = """
            {"email":"user@example.com","challengeType":"EMAIL_CODE"}""";

    public static final String SERVER_OWNED_BODY = """
            {"email":"user@example.com",
             "challengeType":"EMAIL_CODE",
             "challengeId":"99999999-9999-9999-9999-999999999999",
             "expiresAt":"2000-01-01T00:00:00Z",
             "code":"000000",
             "status":"VERIFIED",
             "userId":"77777777-7777-7777-7777-777777777777"}""";

    public static final String EMPTY_BODY = "{}";
    public static final String NULL_FIELDS_BODY = """
            {"email":null,"challengeType":null}""";
    public static final String EMPTY_FIELDS_BODY = """
            {"email":"","challengeType":""}""";

    private StartChallengeData() {
    }
}
