package com.uwords.adapter.storage.repository;

import jakarta.persistence.EntityManager;
import java.util.Optional;

public abstract class StorageRepository {

    protected final EntityManager entityManager;

    protected StorageRepository(EntityManager entityManager) {
        this.entityManager = entityManager;
    }

    protected <T> Optional<T> getOne(Class<T> type, Object identifier) {
        return Optional.ofNullable(entityManager.find(type, identifier));
    }

    protected <T> T addOne(T entity) {
        entityManager.persist(entity);
        entityManager.flush();
        return entity;
    }
}
