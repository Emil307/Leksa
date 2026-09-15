package com.uwords.usecase.testing.fakes;

import com.uwords.domain.auth.user.ProviderAccount;
import com.uwords.usecase.port.auth.session.IssuedSessionRecord;
import com.uwords.usecase.port.auth.session.SessionIssuancePort;
import com.uwords.usecase.port.auth.session.SessionIssuanceRequest;
import com.uwords.usecase.testing.recording.CallJournal;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

public class FakeSessionIssuance implements SessionIssuancePort {

    public static final String ISSUE_SESSION = "issue_session";

    public final Map<ProviderAccount, UUID> users = new LinkedHashMap<>();
    public final List<IssuedSessionRecord> issued = new ArrayList<>();

    private final CallJournal journal;

    public FakeSessionIssuance(CallJournal journal) {
        this.journal = journal;
    }

    @Override
    public IssuedSessionRecord issueSession(SessionIssuanceRequest request) {
        journal.record(ISSUE_SESSION, request);
        UUID known = users.get(request.account());
        UUID userId = known == null ? request.candidateUserId() : known;
        users.put(request.account(), userId);
        IssuedSessionRecord record =
                new IssuedSessionRecord(userId, request.sessionId(), known == null);
        issued.add(record);
        return record;
    }
}
