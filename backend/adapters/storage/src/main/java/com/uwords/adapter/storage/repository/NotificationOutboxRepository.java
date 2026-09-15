package com.uwords.adapter.storage.repository;

import com.uwords.adapter.storage.entity.NotificationOutboxEntity;
import jakarta.persistence.EntityManager;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

@Repository
public class NotificationOutboxRepository extends StorageRepository implements NotificationOutboxEntries {

    public NotificationOutboxRepository(EntityManager entityManager) {
        super(entityManager);
    }

    @Override
    @Transactional
    public NotificationOutboxEntity addOne(NotificationOutboxEntity entry) {
        return super.addOne(entry);
    }
}
