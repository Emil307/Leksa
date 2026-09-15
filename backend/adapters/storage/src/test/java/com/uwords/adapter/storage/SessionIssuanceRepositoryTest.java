package com.uwords.adapter.storage;

import com.uwords.adapter.storage.repository.SessionIssuanceRepository;
import com.uwords.adapter.storage.testing.statements.SessionIssuanceStatements;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

class SessionIssuanceRepositoryTest extends StorageTest {

    @Autowired
    private SessionIssuanceRepository repository;

    private SessionIssuanceStatements statements;

    @BeforeEach
    void createStatements() {
        statements = new SessionIssuanceStatements(dataSource, repository);
    }

    @Test
    void shouldReuseTheExistingUserInsteadOfCreatingAnother() {
        statements.givenExistingUserWithoutAnEmailAccount();

        statements.issueSessionForTheAccount();

        statements.assertReusedTheExistingUserWithoutCreatingOne();
    }

    @Test
    void shouldCreateTheMissingEmailAccountForTheExistingUser() {
        statements.givenExistingUserWithoutAnEmailAccount();

        statements.issueSessionForTheAccount();

        statements.assertSingleEmailAccountLinksTheExistingUser();
    }

    @Test
    void shouldInsertOneSessionRowForTheExistingUser() {
        statements.givenExistingUserWithoutAnEmailAccount();

        statements.issueSessionForTheAccount();

        statements.assertSingleSessionRowBelongsToTheExistingUser();
    }

    @Test
    void shouldAddASecondSessionWithoutASecondIdentity() {
        statements.givenExistingUserWithoutAnEmailAccount();

        statements.issueSessionForTheAccount();
        statements.issueASecondSessionForTheSameAccount();

        statements.assertOneIdentityCarriesBothSessions();
    }

    @Test
    void shouldRegisterANewUserWhenNoIdentityOwnsTheAccount() {
        statements.givenNoUserOwnsTheAccount();

        statements.issueSessionForTheAccount();

        statements.assertRegisteredTheCandidateUserWithAnEmptyName();
    }

    @Test
    void shouldLinkTheRegisteredUserToOneAccountAndOneSession() {
        statements.givenNoUserOwnsTheAccount();

        statements.issueSessionForTheAccount();

        statements.assertSingleEmailAccountAndSessionBelongToTheRegisteredUser();
    }

    @Test
    void shouldReuseTheExistingUserWhenStoredEmailHasDifferentCase() {
        statements.givenExistingUserWithMixedCaseEmail();

        statements.issueSessionForTheAccount();

        statements.assertReusedTheMixedCaseUserWithItsAccountAndSession();
    }

    @Test
    void shouldReuseTheExistingUserWhenStoredEmailHasSurroundingWhitespace() {
        statements.givenExistingUserWithWhitespaceEmail();

        statements.issueSessionForTheAccount();

        statements.assertReusedTheWhitespaceUserWithItsAccountAndSession();
    }
}
