package com.uwords.adapter.storage;

import com.uwords.adapter.storage.repository.SessionIssuanceRepository;
import com.uwords.adapter.storage.repository.SessionRepository;
import com.uwords.adapter.storage.testing.statements.SessionRepositoryStatements;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

class SessionRepositoryTest extends StorageTest {

    @Autowired
    private SessionIssuanceRepository issuance;

    @Autowired
    private SessionRepository repository;

    private SessionRepositoryStatements statements;

    @BeforeEach
    void createStatements() {
        statements = new SessionRepositoryStatements(dataSource, issuance, repository);
    }

    @Test
    void shouldFindTheLiveSessionByItsRefreshToken() {
        statements.givenLiveSession();

        statements.findByStoredRefreshToken();

        statements.assertFoundTheLiveSession();
    }

    @Test
    void shouldReturnNoneForAnUnknownRefreshToken() {
        statements.givenLiveSession();

        statements.findByUnknownRefreshToken();

        statements.assertNoSessionFound();
    }

    @Test
    void shouldReturnNoneWhenTheSessionExpiresExactlyNow() {
        statements.givenSessionExpiringExactlyNow();

        statements.findByStoredRefreshToken();

        statements.assertNoSessionFound();
    }

    @Test
    void shouldRotateTheLiveSessionInPlace() {
        statements.givenLiveSession();

        statements.rotateWithTheStoredRefreshToken();

        statements.assertRotatedTheSessionInPlace();
    }

    @Test
    void shouldRefuseRotationWhenThePresentedTokenWasAlreadyRotated() {
        statements.givenSessionAlreadyRotatedOnce();

        statements.replayTheConsumedRefreshToken();

        statements.assertRefusedAndLeftTheRotatedSessionUntouched();
    }

    @Test
    void shouldRefuseRotationOfAnExpiredSession() {
        statements.givenSessionExpiringExactlyNow();

        statements.rotateWithTheStoredRefreshToken();

        statements.assertRefusedAndLeftTheExpiredSessionUntouched();
    }
}
