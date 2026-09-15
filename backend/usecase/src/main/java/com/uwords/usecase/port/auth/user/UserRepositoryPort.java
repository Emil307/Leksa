package com.uwords.usecase.port.auth.user;

import com.uwords.domain.auth.user.User;
import java.util.Optional;
import java.util.UUID;

public interface UserRepositoryPort {

    Optional<User> findById(UUID userId);
}
