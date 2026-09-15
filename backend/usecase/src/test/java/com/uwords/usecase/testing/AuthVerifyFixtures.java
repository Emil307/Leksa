package com.uwords.usecase.testing;

import com.uwords.domain.auth.challenge.ChallengeVerification;
import com.uwords.domain.auth.session.AccessTokenClaims;
import com.uwords.domain.auth.session.RefreshToken;
import com.uwords.domain.auth.session.SessionPolicy;
import com.uwords.domain.auth.user.AuthProvider;
import com.uwords.domain.auth.user.ProviderAccount;
import com.uwords.usecase.port.auth.session.IssuedSessionRecord;
import com.uwords.usecase.port.auth.session.SessionIssuanceRequest;
import com.uwords.usecase.service.auth.VerifiedSession;
import com.uwords.usecase.testing.fakes.FakeChallengeStore;
import com.uwords.usecase.testing.fakes.FakeChallengeVerificationStore;
import com.uwords.usecase.testing.fakes.FakeNotificationQueue;
import com.uwords.usecase.testing.fakes.FakeSessionIssuance;
import com.uwords.usecase.testing.fakes.StubAccessTokenIssuer;
import com.uwords.usecase.testing.recording.ClaimArguments;
import com.uwords.usecase.testing.recording.RememberedVerification;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.IntStream;

public final class AuthVerifyFixtures {

    public static final List<UUID> IDS =
            IntStream.rangeClosed(1, 8).mapToObj(index -> new UUID(0L, index)).toList();
    public static final UUID FIRST_CHALLENGE_ID = IDS.get(0);
    public static final UUID USER_ID = IDS.get(1);
    public static final UUID FIRST_SESSION_ID = IDS.get(2);
    public static final UUID FIRST_TOKEN_ID = IDS.get(3);
    public static final UUID CHALLENGE_ID = IDS.get(4);
    public static final UUID CANDIDATE_USER_ID = IDS.get(5);
    public static final UUID SESSION_ID = IDS.get(6);
    public static final UUID TOKEN_ID = IDS.get(7);

    public static final List<String> REFRESH_TOKENS =
            List.of("refresh-token-of-first-login", "refresh-token-of-second-login");
    public static final List<String> ACCESS_TOKENS =
            List.of("access-token-of-first-login", "access-token-of-second-login");

    public static final ProviderAccount ACCOUNT =
            new ProviderAccount(AuthProvider.EMAIL, EmailCodeFixtures.EMAIL);
    public static final long ACCESS_TOKEN_TTL_SECONDS = 900;
    public static final long REFRESH_TOKEN_TTL_SECONDS = 2592000;
    public static final SessionPolicy SESSION_POLICY =
            new SessionPolicy(ACCESS_TOKEN_TTL_SECONDS, REFRESH_TOKEN_TTL_SECONDS);
    public static final Instant REFRESH_EXPIRES_AT =
            EmailCodeFixtures.NOW.plusSeconds(REFRESH_TOKEN_TTL_SECONDS);
    public static final Instant ACCESS_EXPIRES_AT =
            EmailCodeFixtures.NOW.plusSeconds(ACCESS_TOKEN_TTL_SECONDS);

    public static final List<String> START_CALL_NAMES = List.of(
            FakeChallengeStore.ACQUIRE_COOLDOWN,
            FakeChallengeStore.SWAP_CHALLENGE,
            FakeNotificationQueue.ENQUEUE);
    public static final List<String> VERIFY_CALL_NAMES = List.of(
            FakeChallengeVerificationStore.FIND_CHALLENGE,
            FakeChallengeVerificationStore.CLAIM_ATTEMPT,
            FakeChallengeVerificationStore.REDEEM_CHALLENGE,
            FakeSessionIssuance.ISSUE_SESSION,
            FakeChallengeVerificationStore.REMEMBER_VERIFICATION,
            StubAccessTokenIssuer.ISSUE_ACCESS_TOKEN);
    public static final List<String> EXPECTED_CALL_NAMES = concat();
    public static final List<Integer> VERIFY_STARTS =
            List.of(START_CALL_NAMES.size(), EXPECTED_CALL_NAMES.size() - VERIFY_CALL_NAMES.size());

    public static final List<UUID> EXPECTED_CHALLENGE_IDS = List.of(FIRST_CHALLENGE_ID, CHALLENGE_ID);
    public static final List<ClaimArguments> EXPECTED_CLAIMS = List.of(
            new ClaimArguments(FIRST_CHALLENGE_ID, ChallengeStartFixtures.MAX_ATTEMPTS),
            new ClaimArguments(CHALLENGE_ID, ChallengeStartFixtures.MAX_ATTEMPTS));
    public static final List<SessionIssuanceRequest> EXPECTED_ISSUANCE_REQUESTS = List.of(
            new SessionIssuanceRequest(
                    ACCOUNT,
                    USER_ID,
                    FIRST_SESSION_ID,
                    new RefreshToken(REFRESH_TOKENS.get(0)),
                    EmailCodeFixtures.NOW,
                    REFRESH_EXPIRES_AT),
            new SessionIssuanceRequest(
                    ACCOUNT,
                    CANDIDATE_USER_ID,
                    SESSION_ID,
                    new RefreshToken(REFRESH_TOKENS.get(1)),
                    EmailCodeFixtures.NOW,
                    REFRESH_EXPIRES_AT));
    public static final List<IssuedSessionRecord> EXPECTED_ISSUED_RECORDS = List.of(
            new IssuedSessionRecord(USER_ID, FIRST_SESSION_ID, true),
            new IssuedSessionRecord(USER_ID, SESSION_ID, false));

    public static final ChallengeVerification FIRST_VERIFICATION =
            new ChallengeVerification(FIRST_CHALLENGE_ID, USER_ID, FIRST_SESSION_ID);
    public static final ChallengeVerification SECOND_VERIFICATION =
            new ChallengeVerification(CHALLENGE_ID, USER_ID, SESSION_ID);
    public static final List<RememberedVerification> EXPECTED_REMEMBERED = List.of(
            new RememberedVerification(FIRST_VERIFICATION, ChallengeStartFixtures.REPLAY_WINDOW_SECONDS),
            new RememberedVerification(SECOND_VERIFICATION, ChallengeStartFixtures.REPLAY_WINDOW_SECONDS));
    public static final Map<UUID, ChallengeVerification> EXPECTED_VERIFICATIONS =
            Map.of(FIRST_CHALLENGE_ID, FIRST_VERIFICATION, CHALLENGE_ID, SECOND_VERIFICATION);
    public static final List<AccessTokenClaims> EXPECTED_ACCESS_TOKEN_CLAIMS = List.of(
            new AccessTokenClaims(USER_ID, FIRST_SESSION_ID, FIRST_TOKEN_ID, ACCESS_EXPIRES_AT),
            new AccessTokenClaims(USER_ID, SESSION_ID, TOKEN_ID, ACCESS_EXPIRES_AT));
    public static final VerifiedSession EXPECTED_VERIFIED_SESSION = new VerifiedSession(
            USER_ID, SESSION_ID, REFRESH_TOKENS.get(1), ACCESS_TOKENS.get(1));

    private AuthVerifyFixtures() {
    }

    private static List<String> concat() {
        return java.util.stream.Stream.of(
                        START_CALL_NAMES, VERIFY_CALL_NAMES, START_CALL_NAMES, VERIFY_CALL_NAMES)
                .flatMap(List::stream)
                .toList();
    }
}
