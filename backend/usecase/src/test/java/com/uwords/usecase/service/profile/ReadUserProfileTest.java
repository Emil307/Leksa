package com.uwords.usecase.service.profile;

import com.uwords.usecase.testing.fakes.FakeAccessTokenDecoder;
import com.uwords.usecase.testing.fakes.FakeActiveSessionRepository;
import com.uwords.usecase.testing.fakes.FakeUserRepository;
import com.uwords.usecase.testing.fakes.FixedClock;
import com.uwords.usecase.testing.statements.AuthData;
import com.uwords.usecase.testing.statements.AuthStatements;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ReadUserProfileTest {

    private AuthStatements statements;

    @BeforeEach
    void createStatements() {
        statements = new AuthStatements(
                new FakeAccessTokenDecoder(),
                new FakeActiveSessionRepository(),
                new FakeUserRepository(),
                new FixedClock(AuthData.NOW));
    }

    @Test
    void shouldReturnEveryFieldOfTheStoredAccount() {
        statements.givenSignedInCallerWithAStoredAccount();

        statements.whenTheOwnProfileIsRead();

        statements.assertProfileIsTheWholeStoredAccount();
    }

    @Test
    void shouldRefuseWhenTheAccountRowIsAbsent() {
        statements.givenActiveSessionAndValidToken();
        statements.givenAccountRowIsAbsent();

        statements.whenTheOwnProfileReadIsAttempted();

        statements.assertProfileRefusedAsAccount();
    }

    @Test
    void shouldRefuseWhenAccountStorageIsUnreachable() {
        statements.givenSignedInCallerWithAStoredAccount();
        statements.givenAccountStorageIsUnreachable();

        statements.whenTheOwnProfileReadIsAttempted();

        statements.assertProfileRefusedAsStorage();
    }
}
