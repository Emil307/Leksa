package com.uwords.usecase.port.auth.session;

import com.uwords.domain.auth.session.ActiveSession;
import java.util.Optional;
import java.util.UUID;

public interface ActiveSessionRepositoryPort {

    Optional<ActiveSession> findById(UUID sessionId);
}
