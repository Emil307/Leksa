package com.uwords.adapter.storage.repository;

import com.uwords.adapter.storage.entity.UserEntity;
import com.uwords.adapter.storage.mapper.UserMapper;
import com.uwords.domain.auth.user.User;
import com.uwords.domain.common.UnavailableException;
import com.uwords.usecase.port.auth.user.UserRepositoryPort;
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceException;
import java.util.NoSuchElementException;
import java.util.Optional;
import java.util.UUID;
import org.springframework.dao.DataAccessException;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

@Repository
public class UserRepository extends StorageRepository implements UserRepositoryPort {

    public static final String UNAVAILABLE_MESSAGE = "User storage is unavailable";
    public static final String OUT_OF_DOMAIN_GENDER_MESSAGE = "Stored gender is outside the domain";

    public UserRepository(EntityManager entityManager) {
        super(entityManager);
    }

    @Override
    @Transactional
    public Optional<User> findById(UUID userId) {
        try {
            return getOne(UserEntity.class, userId).map(UserMapper::toDomain);
        } catch (NoSuchElementException error) {
            throw new UnavailableException(OUT_OF_DOMAIN_GENDER_MESSAGE, null, false);
        } catch (PersistenceException | DataAccessException error) {
            throw new UnavailableException(UNAVAILABLE_MESSAGE, null, false);
        }
    }
}
