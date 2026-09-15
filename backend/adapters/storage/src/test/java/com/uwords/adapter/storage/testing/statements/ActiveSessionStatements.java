package com.uwords.adapter.storage.testing.statements;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.catchThrowable;

import com.uwords.adapter.storage.repository.ActiveSessionRepository;
import com.uwords.adapter.storage.testing.AuthData;
import com.uwords.adapter.storage.testing.AuthRows;
import com.uwords.adapter.storage.testing.AuthSchema;
import com.uwords.adapter.storage.testing.FailureShape;
import com.uwords.adapter.storage.testing.UnreachableStorage;
import com.uwords.domain.auth.failure.AuthFailureReason;
import com.uwords.domain.auth.failure.Unauthorized;
import com.uwords.domain.auth.session.ActiveSession;
import com.uwords.domain.common.ErrorCode;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import javax.sql.DataSource;

public class ActiveSessionStatements {

    private static final Map<String, Object> NO_PAYLOAD = Map.of();
    private static final Map<String, Object> LEGACY_SESSION_PAYLOAD =
            Map.of("reason", AuthFailureReason.LEGACY_SESSION.value());

    private final DataSource dataSource;
    private final ActiveSessionRepository repository;
    private final UUID sessionId = UUID.randomUUID();
    private final UUID userId = UUID.randomUUID();
    private Optional<ActiveSession> found = Optional.empty();
    private Throwable failure;

    public ActiveSessionStatements(DataSource dataSource, ActiveSessionRepository repository) {
        this.dataSource = dataSource;
        this.repository = repository;
    }

    public void givenLiveSession() {
        AuthRows.givenLiveSession(dataSource, sessionId, userId);
    }

    public void givenLegacySession() {
        AuthSchema.allowLegacySessionRows(dataSource);
        AuthRows.givenLegacySession(dataSource, sessionId, userId);
    }

    public void readActiveSession() {
        found = repository.findById(sessionId);
    }

    public void captureActiveSessionFailure() {
        failure = catchThrowable(() -> repository.findById(sessionId));
    }

    public void captureUnreachableActiveSessionFailure() {
        ActiveSessionRepository unreachable = new ActiveSessionRepository(UnreachableStorage.entityManager());
        failure = catchThrowable(() -> unreachable.findById(sessionId));
    }

    public void assertLiveSession() {
        assertThat(found).contains(new ActiveSession(sessionId, userId, AuthData.SESSION_EXPIRES_AT));
    }

    public void assertNoActiveSession() {
        assertThat(found).isEmpty();
    }

    public void assertLegacySessionRefusal() {
        assertThat(FailureShape.of(failure)).isEqualTo(new FailureShape(
                ErrorCode.UNAUTHORIZED, Unauthorized.UNAUTHORIZED_MESSAGE, LEGACY_SESSION_PAYLOAD, false));
    }

    public void assertSessionStorageUnavailable() {
        assertThat(FailureShape.of(failure)).isEqualTo(new FailureShape(
                ErrorCode.UNAVAILABLE, ActiveSessionRepository.UNAVAILABLE_MESSAGE, NO_PAYLOAD, false));
    }
}
