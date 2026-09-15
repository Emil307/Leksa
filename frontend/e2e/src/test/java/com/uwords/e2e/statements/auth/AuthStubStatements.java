package com.uwords.e2e.statements.auth;

import static org.assertj.core.api.Assertions.assertThat;

import com.uwords.e2e.stub.ApiStub;
import com.uwords.e2e.stub.ChallengeHandler;
import com.uwords.e2e.stub.ChallengeStore;
import com.uwords.e2e.stub.IssuedChallenge;
import com.uwords.e2e.stub.IssuedSession;
import com.uwords.e2e.stub.RecordedRequest;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;

public class AuthStubStatements {

    private static final String POST = "POST";
    private static final String EMAIL_CODE = "EMAIL_CODE";

    private final ChallengeStore store = ApiStub.instance().store();

    public String uniqueEmail() {
        return "ui-1-1-" + UUID.randomUUID().toString().substring(0, 8) + "@example.test";
    }

    public String codeSentTo(String email) {
        return issuedChallenge(email).code();
    }

    public Instant issuedExpiresAt(String email) {
        return issuedChallenge(email).expiresAt();
    }

    public List<String> issuedSecrets(String email) {
        IssuedSession session = store.sessionOf(email).orElseThrow(
                () -> new AssertionError("stub opened no session for " + email));
        return List.of(session.accessToken(), session.refreshToken(), session.sessionId(),
                issuedChallenge(email).challengeId());
    }

    public void assertExactlyOneStartRequest(String email) {
        assertThat(requestsTo(email, ChallengeHandler.START_PATH))
                .as("start requests for %s", email)
                .containsExactly(new RecordedRequest(POST, ChallengeHandler.START_PATH,
                        Map.of("email", email, "challengeType", EMAIL_CODE)));
    }

    public void assertExactlyOneVerifyRequest(String email) {
        IssuedChallenge challenge = issuedChallenge(email);
        assertThat(requestsTo(email, ChallengeHandler.VERIFY_PATH))
                .as("verify requests for %s", email)
                .containsExactly(new RecordedRequest(POST, ChallengeHandler.VERIFY_PATH,
                        Map.of("challengeId", challenge.challengeId(), "code", challenge.code())));
    }

    private IssuedChallenge issuedChallenge(String email) {
        return store.byEmail(email).orElseThrow(
                () -> new AssertionError("stub issued no challenge for " + email));
    }

    private List<RecordedRequest> requestsTo(String email, String path) {
        return store.requestsOf(email).stream().filter(request -> path.equals(request.path())).toList();
    }
}
