package com.uwords.usecase.testing.statements;

import com.uwords.domain.auth.challenge.Challenge;
import com.uwords.domain.auth.challenge.ChallengeType;
import com.uwords.domain.auth.code.VerificationCode;
import com.uwords.domain.notifications.OutboundEmail;
import com.uwords.usecase.service.auth.StartedChallenge;
import com.uwords.usecase.testing.ChallengeStartFixtures;
import com.uwords.usecase.testing.EmailCodeFixtures;
import com.uwords.usecase.testing.recording.CooldownArguments;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;

public final class StartChallengeFixtures {

    public static final UUID CHALLENGE_ID = UUID.fromString("2f1a6b64-9e1c-4d2a-9c0f-5b3d7e8a1c02");
    public static final Instant EXPIRES_AT =
            EmailCodeFixtures.NOW.plusSeconds(ChallengeStartFixtures.TTL_SECONDS);
    public static final String QUEUE_FAILURE_MESSAGE = "outbox insert failed";
    public static final String UNAVAILABLE_MESSAGE = "Challenge start could not be queued";

    public static final CooldownArguments EXPECTED_COOLDOWN_ARGUMENTS = new CooldownArguments(
            "EMAIL_CODE", EmailCodeFixtures.EMAIL, ChallengeStartFixtures.COOLDOWN_SECONDS);
    public static final Challenge EXPECTED_CHALLENGE = new Challenge(
            CHALLENGE_ID,
            ChallengeType.EMAIL_CODE,
            EmailCodeFixtures.EMAIL,
            new VerificationCode(EmailCodeFixtures.CODE),
            EmailCodeFixtures.NOW,
            EXPIRES_AT,
            0);
    public static final OutboundEmail EXPECTED_EMAIL = new OutboundEmail(
            EmailCodeFixtures.EMAIL,
            EmailCodeFixtures.SENDER,
            EmailCodeFixtures.SUBJECT,
            CHALLENGE_ID,
            EmailCodeFixtures.TEMPLATE_PATH,
            Map.of("code", EmailCodeFixtures.CODE));
    public static final StartedChallenge EXPECTED_STARTED_CHALLENGE =
            new StartedChallenge(CHALLENGE_ID, ChallengeType.EMAIL_CODE, EXPIRES_AT);

    private StartChallengeFixtures() {
    }
}
