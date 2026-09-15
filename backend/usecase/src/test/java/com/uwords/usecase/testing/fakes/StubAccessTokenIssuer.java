package com.uwords.usecase.testing.fakes;

import com.uwords.domain.auth.session.AccessTokenClaims;
import com.uwords.usecase.port.auth.session.AccessTokenIssuerPort;
import com.uwords.usecase.testing.recording.CallJournal;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.List;

public class StubAccessTokenIssuer implements AccessTokenIssuerPort {

    public static final String ISSUE_ACCESS_TOKEN = "issue_access_token";

    private final CallJournal journal;
    private final Deque<String> remaining;

    public StubAccessTokenIssuer(CallJournal journal, List<String> tokens) {
        this.journal = journal;
        this.remaining = new ArrayDeque<>(tokens);
    }

    @Override
    public String issue(AccessTokenClaims claims) {
        journal.record(ISSUE_ACCESS_TOKEN, claims);
        return PreparedValues.take(remaining, "StubAccessTokenIssuer");
    }
}
