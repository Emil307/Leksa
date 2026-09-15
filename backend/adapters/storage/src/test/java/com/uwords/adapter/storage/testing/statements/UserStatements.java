package com.uwords.adapter.storage.testing.statements;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.catchThrowable;

import com.uwords.adapter.storage.repository.UserRepository;
import com.uwords.adapter.storage.testing.AuthData;
import com.uwords.adapter.storage.testing.AuthRows;
import com.uwords.adapter.storage.testing.FailureShape;
import com.uwords.adapter.storage.testing.UnreachableStorage;
import com.uwords.domain.auth.user.User;
import com.uwords.domain.common.ErrorCode;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import javax.sql.DataSource;

public class UserStatements {

    private static final Map<String, Object> NO_PAYLOAD = Map.of();

    private final DataSource dataSource;
    private final UserRepository repository;
    private final UUID userId = UUID.randomUUID();
    private Optional<User> found = Optional.empty();
    private Throwable failure;

    public UserStatements(DataSource dataSource, UserRepository repository) {
        this.dataSource = dataSource;
        this.repository = repository;
    }

    public void givenStoredFullUser() {
        AuthRows.givenStoredFullUser(dataSource, userId);
    }

    public void givenStoredMinimalUser() {
        AuthRows.givenStoredMinimalUser(dataSource, userId);
    }

    public void givenStoredUserWithOutOfDomainGender() {
        AuthRows.givenStoredUserWithOutOfDomainGender(dataSource, userId);
    }

    public void readUser() {
        found = repository.findById(userId);
    }

    public void captureUserFailure() {
        failure = catchThrowable(() -> repository.findById(userId));
    }

    public void captureUnreachableUserFailure() {
        UserRepository unreachable = new UserRepository(UnreachableStorage.entityManager());
        failure = catchThrowable(() -> unreachable.findById(userId));
    }

    public void assertFullUser() {
        assertThat(found).contains(AuthData.expectedFullUser(userId));
    }

    public void assertMinimalUser() {
        assertThat(found).contains(AuthData.expectedMinimalUser(userId));
    }

    public void assertNoUser() {
        assertThat(found).isEmpty();
    }

    public void assertOutOfDomainGenderFailure() {
        assertThat(FailureShape.of(failure)).isEqualTo(new FailureShape(
                ErrorCode.UNAVAILABLE, UserRepository.OUT_OF_DOMAIN_GENDER_MESSAGE, NO_PAYLOAD, false));
    }

    public void assertUserStorageUnavailable() {
        assertThat(FailureShape.of(failure)).isEqualTo(new FailureShape(
                ErrorCode.UNAVAILABLE, UserRepository.UNAVAILABLE_MESSAGE, NO_PAYLOAD, false));
    }
}
