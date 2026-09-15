package com.uwords.adapter.storage;

import com.uwords.adapter.storage.repository.UserRepository;
import com.uwords.adapter.storage.testing.statements.UserStatements;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

class UserRepositoryTest extends StorageTest {

    @Autowired
    private UserRepository repository;

    private UserStatements statements;

    @BeforeEach
    void createStatements() {
        statements = new UserStatements(dataSource, repository);
    }

    @Test
    void shouldReturnEveryStoredColumnOfTheUser() {
        statements.givenStoredFullUser();

        statements.readUser();

        statements.assertFullUser();
    }

    @Test
    void shouldReturnNoneForEveryUnsetNullableColumn() {
        statements.givenStoredMinimalUser();

        statements.readUser();

        statements.assertMinimalUser();
    }

    @Test
    void shouldReturnNoneWhenTheUserIsAbsent() {
        statements.readUser();

        statements.assertNoUser();
    }

    @Test
    void shouldRaiseUnavailableWhenGenderIsOutsideTheDomain() {
        statements.givenStoredUserWithOutOfDomainGender();

        statements.captureUserFailure();

        statements.assertOutOfDomainGenderFailure();
    }

    @Test
    void shouldRaiseUnavailableWhenTheDatabaseFails() {
        statements.captureUnreachableUserFailure();

        statements.assertUserStorageUnavailable();
    }
}
