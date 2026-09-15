package com.uwords.adapter.storage.repository;

import com.uwords.adapter.storage.mapper.SessionIssuanceMapper;
import com.uwords.domain.auth.user.AuthProvider;
import com.uwords.usecase.port.auth.session.IssuedSessionRecord;
import com.uwords.usecase.port.auth.session.SessionIssuancePort;
import com.uwords.usecase.port.auth.session.SessionIssuanceRequest;
import jakarta.persistence.EntityManager;
import java.util.Optional;
import java.util.UUID;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

@Repository
public class SessionIssuanceRepository extends StorageRepository implements SessionIssuancePort {

    private static final String LINKED_USER_QUERY =
            "select account.userId from AuthAccountEntity account "
                    + "where account.provider = :provider and account.providerId = :providerId";
    private static final String USER_BY_NORMALIZED_EMAIL_QUERY =
            "select stored.id from UserEntity stored where lower(trim(stored.email)) = lower(trim(:email))";
    private static final String PROVIDER_PARAMETER = "provider";
    private static final String PROVIDER_ID_PARAMETER = "providerId";
    private static final String EMAIL_PARAMETER = "email";

    public SessionIssuanceRepository(EntityManager entityManager) {
        super(entityManager);
    }

    @Override
    @Transactional
    public IssuedSessionRecord issueSession(SessionIssuanceRequest request) {
        LinkedUser linked = linkUser(request);
        addOne(SessionIssuanceMapper.toSessionEntity(request, linked.userId()));
        return new IssuedSessionRecord(linked.userId(), request.sessionId(), linked.createdUser());
    }

    private LinkedUser linkUser(SessionIssuanceRequest request) {
        return findLinkedUserId(request)
                .map(userId -> new LinkedUser(userId, false))
                .orElseGet(() -> registerAccount(request));
    }

    private LinkedUser registerAccount(SessionIssuanceRequest request) {
        LinkedUser resolved = resolveUser(request);
        addOne(SessionIssuanceMapper.toAccountEntity(request, resolved.userId()));
        return resolved;
    }

    private LinkedUser resolveUser(SessionIssuanceRequest request) {
        return findUserIdByEmail(request)
                .map(userId -> new LinkedUser(userId, false))
                .orElseGet(() -> registerUser(request));
    }

    private LinkedUser registerUser(SessionIssuanceRequest request) {
        addOne(SessionIssuanceMapper.toUserEntity(request));
        return new LinkedUser(request.candidateUserId(), true);
    }

    private Optional<UUID> findLinkedUserId(SessionIssuanceRequest request) {
        return entityManager.createQuery(LINKED_USER_QUERY, UUID.class)
                .setParameter(PROVIDER_PARAMETER, request.account().provider().value())
                .setParameter(PROVIDER_ID_PARAMETER, request.account().providerId())
                .getResultStream()
                .findFirst();
    }

    private Optional<UUID> findUserIdByEmail(SessionIssuanceRequest request) {
        if (request.account().provider() != AuthProvider.EMAIL) {
            return Optional.empty();
        }
        return entityManager.createQuery(USER_BY_NORMALIZED_EMAIL_QUERY, UUID.class)
                .setParameter(EMAIL_PARAMETER, request.account().providerId())
                .getResultStream()
                .findFirst();
    }

    private record LinkedUser(UUID userId, boolean createdUser) {
    }
}
