package com.uwords.adapter.storage.testing.statements;

import static com.uwords.adapter.storage.testing.SessionIssuanceData.ACCOUNT;
import static com.uwords.adapter.storage.testing.SessionIssuanceData.ALL_USER_IDS;
import static com.uwords.adapter.storage.testing.SessionIssuanceData.CANDIDATE_USER_ID;
import static com.uwords.adapter.storage.testing.SessionIssuanceData.CREATED_AT;
import static com.uwords.adapter.storage.testing.SessionIssuanceData.EMAIL;
import static com.uwords.adapter.storage.testing.SessionIssuanceData.EMPTY_NAME;
import static com.uwords.adapter.storage.testing.SessionIssuanceData.EXISTING_USER_ID;
import static com.uwords.adapter.storage.testing.SessionIssuanceData.EXPIRES_AT;
import static com.uwords.adapter.storage.testing.SessionIssuanceData.FIRST_REFRESH_TOKEN;
import static com.uwords.adapter.storage.testing.SessionIssuanceData.FIRST_SESSION_ID;
import static com.uwords.adapter.storage.testing.SessionIssuanceData.MIXED_CASE_USER_ID;
import static com.uwords.adapter.storage.testing.SessionIssuanceData.SECOND_REFRESH_TOKEN;
import static com.uwords.adapter.storage.testing.SessionIssuanceData.SECOND_SESSION_ID;
import static com.uwords.adapter.storage.testing.SessionIssuanceData.STORED_MIXED_CASE_EMAIL;
import static com.uwords.adapter.storage.testing.SessionIssuanceData.STORED_WHITESPACE_EMAIL;
import static com.uwords.adapter.storage.testing.SessionIssuanceData.WHITESPACE_USER_ID;
import static com.uwords.adapter.storage.testing.SessionIssuanceData.accountRowsOf;
import static com.uwords.adapter.storage.testing.SessionIssuanceData.firstSessionRowOf;
import static com.uwords.adapter.storage.testing.SessionIssuanceData.secondSessionRowOf;
import static org.assertj.core.api.Assertions.assertThat;

import com.uwords.adapter.storage.repository.SessionIssuanceRepository;
import com.uwords.domain.auth.session.RefreshToken;
import com.uwords.adapter.storage.testing.SessionIssuanceRows;
import com.uwords.adapter.storage.testing.SessionIssuanceRows.AccountRow;
import com.uwords.adapter.storage.testing.SessionIssuanceRows.IdentityRow;
import com.uwords.adapter.storage.testing.SessionIssuanceRows.SessionRow;
import com.uwords.usecase.port.auth.session.IssuedSessionRecord;
import com.uwords.usecase.port.auth.session.SessionIssuanceRequest;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import javax.sql.DataSource;

public class SessionIssuanceStatements {

    private final DataSource dataSource;
    private final SessionIssuanceRepository repository;
    private final List<IssuedSessionRecord> issued = new ArrayList<>();

    public SessionIssuanceStatements(DataSource dataSource, SessionIssuanceRepository repository) {
        this.dataSource = dataSource;
        this.repository = repository;
    }

    public void givenExistingUserWithoutAnEmailAccount() {
        SessionIssuanceRows.givenStoredUser(dataSource, EXISTING_USER_ID, EMAIL);
    }

    public void givenExistingUserWithMixedCaseEmail() {
        SessionIssuanceRows.givenStoredUser(dataSource, MIXED_CASE_USER_ID, STORED_MIXED_CASE_EMAIL);
    }

    public void givenExistingUserWithWhitespaceEmail() {
        SessionIssuanceRows.givenStoredUser(dataSource, WHITESPACE_USER_ID, STORED_WHITESPACE_EMAIL);
    }

    public void givenNoUserOwnsTheAccount() {
        assertThat(userIds()).isEmpty();
    }

    public void issueSessionForTheAccount() {
        issued.add(repository.issueSession(requestOf(FIRST_SESSION_ID, FIRST_REFRESH_TOKEN)));
    }

    public void issueASecondSessionForTheSameAccount() {
        issued.add(repository.issueSession(requestOf(SECOND_SESSION_ID, SECOND_REFRESH_TOKEN)));
    }

    public void assertReusedTheExistingUserWithoutCreatingOne() {
        assertThat(issued).isEqualTo(List.of(reusedRecord(EXISTING_USER_ID, FIRST_SESSION_ID)));
        assertThat(userIds()).isEqualTo(List.of(EXISTING_USER_ID));
    }

    public void assertSingleEmailAccountLinksTheExistingUser() {
        assertThat(accountRows()).isEqualTo(accountRowsOf(EXISTING_USER_ID));
    }

    public void assertSingleSessionRowBelongsToTheExistingUser() {
        assertThat(sessionRows()).isEqualTo(List.of(firstSessionRowOf(EXISTING_USER_ID)));
    }

    public void assertReusedTheMixedCaseUserWithItsAccountAndSession() {
        assertReusedWithoutCreating(MIXED_CASE_USER_ID);
    }

    public void assertReusedTheWhitespaceUserWithItsAccountAndSession() {
        assertReusedWithoutCreating(WHITESPACE_USER_ID);
    }

    public void assertRegisteredTheCandidateUserWithAnEmptyName() {
        assertThat(issued).isEqualTo(
                List.of(new IssuedSessionRecord(CANDIDATE_USER_ID, FIRST_SESSION_ID, true)));
        assertThat(identityRows()).isEqualTo(
                List.of(new IdentityRow(CANDIDATE_USER_ID, EMPTY_NAME, EMAIL)));
    }

    public void assertSingleEmailAccountAndSessionBelongToTheRegisteredUser() {
        assertThat(accountRows()).isEqualTo(accountRowsOf(CANDIDATE_USER_ID));
        assertThat(sessionRows()).isEqualTo(List.of(firstSessionRowOf(CANDIDATE_USER_ID)));
    }

    public void assertOneIdentityCarriesBothSessions() {
        assertThat(issued).isEqualTo(List.of(
                reusedRecord(EXISTING_USER_ID, FIRST_SESSION_ID),
                reusedRecord(EXISTING_USER_ID, SECOND_SESSION_ID)));
        assertThat(userIds()).isEqualTo(List.of(EXISTING_USER_ID));
        assertThat(accountRows()).isEqualTo(accountRowsOf(EXISTING_USER_ID));
        assertThat(sessionRows()).isEqualTo(
                List.of(firstSessionRowOf(EXISTING_USER_ID), secondSessionRowOf(EXISTING_USER_ID)));
    }

    private void assertReusedWithoutCreating(UUID userId) {
        assertThat(issued).isEqualTo(List.of(reusedRecord(userId, FIRST_SESSION_ID)));
        assertThat(userIds()).isEqualTo(List.of(userId));
        assertThat(accountRows()).isEqualTo(accountRowsOf(userId));
        assertThat(sessionRows()).isEqualTo(List.of(firstSessionRowOf(userId)));
    }

    private IssuedSessionRecord reusedRecord(UUID userId, UUID sessionId) {
        return new IssuedSessionRecord(userId, sessionId, false);
    }

    private SessionIssuanceRequest requestOf(UUID sessionId, RefreshToken token) {
        return new SessionIssuanceRequest(ACCOUNT, CANDIDATE_USER_ID, sessionId, token, CREATED_AT, EXPIRES_AT);
    }

    private List<UUID> userIds() {
        return SessionIssuanceRows.userIds(dataSource, ALL_USER_IDS);
    }

    private List<IdentityRow> identityRows() {
        return SessionIssuanceRows.identityRows(dataSource, ALL_USER_IDS);
    }

    private List<AccountRow> accountRows() {
        return SessionIssuanceRows.accountRows(dataSource, ALL_USER_IDS);
    }

    private List<SessionRow> sessionRows() {
        return SessionIssuanceRows.sessionRows(dataSource, ALL_USER_IDS);
    }
}
