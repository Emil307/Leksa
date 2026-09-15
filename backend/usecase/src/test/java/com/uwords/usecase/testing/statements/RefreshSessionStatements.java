package com.uwords.usecase.testing.statements;

import static org.assertj.core.api.Assertions.assertThat;

import com.uwords.usecase.service.auth.RefreshSessionRequest;
import com.uwords.usecase.service.auth.RefreshSessionTokensService;
import com.uwords.usecase.service.auth.RotatedSessionTokens;
import com.uwords.usecase.testing.AuthVerifyFixtures;
import com.uwords.usecase.testing.fakes.FakeIdGenerator;
import com.uwords.usecase.testing.fakes.FakeSessionRepository;
import com.uwords.usecase.testing.fakes.FixedClock;
import com.uwords.usecase.testing.fakes.StubAccessTokenIssuer;
import com.uwords.usecase.testing.fakes.StubRefreshTokenGenerator;
import com.uwords.usecase.testing.recording.CallJournal;
import java.util.List;

public class RefreshSessionStatements {

    private final CallJournal journal = new CallJournal();
    private final FakeSessionRepository sessions = new FakeSessionRepository(journal);
    private final FixedClock clock = new FixedClock(RefreshSessionData.LOGIN_AT);
    private final StubRefreshTokenGenerator refreshTokens =
            new StubRefreshTokenGenerator(RefreshSessionData.REFRESH_TOKENS);
    private final StubAccessTokenIssuer accessTokens =
            new StubAccessTokenIssuer(journal, RefreshSessionData.ACCESS_TOKENS);
    private final EmailCodeLogin login = new EmailCodeLogin(journal, sessions, clock, refreshTokens, accessTokens);
    private final FakeIdGenerator ids = new FakeIdGenerator(RefreshSessionData.ROTATION_IDS);
    private final RefreshSessionTokensService service = new RefreshSessionTokensService(
            sessions, refreshTokens, accessTokens, clock, ids, AuthVerifyFixtures.SESSION_POLICY);

    private String presentedRefreshToken;
    private int refreshCallsStart;
    private RotatedSessionTokens rotated;

    public void givenSignedInUserHoldsALiveSession() {
        presentedRefreshToken = login.signInAndTakeRefreshToken();
        clock.set(RefreshSessionData.ROTATION_AT);
    }

    public void whenClientRefreshesTokensWithThatSessionsRefreshToken() {
        refreshCallsStart = journal.calls().size();
        rotated = service.refresh(new RefreshSessionRequest(presentedRefreshToken));
    }

    public void assertResponseKeepsTheSessionIdentityAndCarriesANewPair() {
        assertThat(presentedRefreshToken)
                .as("refresh token the client presents is the one issued at login")
                .isEqualTo(RefreshSessionData.LOGIN_REFRESH_TOKEN);
        assertThat(rotated)
                .as("refresh answer keeps the session id and carries the rotated pair")
                .isEqualTo(RefreshSessionData.EXPECTED_ROTATED_TOKENS);
    }

    public void assertAccessTokenIsSignedForTheSameUserAndSession() {
        assertThat(refreshCalls().payloadsOf(StubAccessTokenIssuer.ISSUE_ACCESS_TOKEN))
                .as("claims handed to the access token issuer during refresh")
                .isEqualTo(List.of(RefreshSessionData.EXPECTED_ROTATED_CLAIMS));
    }

    public void assertExactlyOneConditionalRotationIsWritten() {
        assertThat(refreshCalls().payloadsOf(FakeSessionRepository.ROTATE_REFRESH_TOKEN))
                .as("conditional rotations written during refresh")
                .isEqualTo(List.of(RefreshSessionData.EXPECTED_ROTATION));
    }

    public void assertPairIsMintedBeforeTheWrite() {
        assertThat(refreshCalls().names())
                .as("order of port calls during refresh")
                .isEqualTo(RefreshSessionData.EXPECTED_REFRESH_CALL_NAMES);
    }

    public void assertNoNewSessionRowIsCreated() {
        assertThat(sessions.rows)
                .as("session rows after rotation")
                .isEqualTo(RefreshSessionData.EXPECTED_ROWS_AFTER_ROTATION);
        assertThat(sessions.users)
                .as("known accounts after rotation")
                .isEqualTo(RefreshSessionData.EXPECTED_USERS_AFTER_ROTATION);
    }

    public void assertRefreshedAccessTokenCarriesAFreshTokenId() {
        assertThat(journal.payloadsOf(StubAccessTokenIssuer.ISSUE_ACCESS_TOKEN))
                .as("claims handed to the access token issuer at login and then at refresh")
                .isEqualTo(RefreshSessionData.EXPECTED_ISSUED_CLAIMS);
    }

    private CallJournal refreshCalls() {
        return journal.since(refreshCallsStart);
    }
}
