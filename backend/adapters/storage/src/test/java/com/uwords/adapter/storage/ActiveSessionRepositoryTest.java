package com.uwords.adapter.storage;

import com.uwords.adapter.storage.repository.ActiveSessionRepository;
import com.uwords.adapter.storage.testing.statements.ActiveSessionStatements;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

class ActiveSessionRepositoryTest extends StorageTest {

    @Autowired
    private ActiveSessionRepository repository;

    private ActiveSessionStatements statements;

    @BeforeEach
    void createStatements() {
        statements = new ActiveSessionStatements(dataSource, repository);
    }

    @Test
    void shouldReturnTheLiveSession() {
        statements.givenLiveSession();

        statements.readActiveSession();

        statements.assertLiveSession();
    }

    @Test
    void shouldReturnNoneWhenTheSessionIsAbsent() {
        statements.readActiveSession();

        statements.assertNoActiveSession();
    }

    @Test
    void shouldRefuseALegacyRowWithoutExpiry() {
        statements.givenLegacySession();

        statements.captureActiveSessionFailure();

        statements.assertLegacySessionRefusal();
    }

    @Test
    void shouldRaiseUnavailableWhenTheDatabaseFails() {
        statements.captureUnreachableActiveSessionFailure();

        statements.assertSessionStorageUnavailable();
    }
}
