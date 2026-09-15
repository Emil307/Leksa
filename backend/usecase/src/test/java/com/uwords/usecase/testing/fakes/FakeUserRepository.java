package com.uwords.usecase.testing.fakes;

import com.uwords.domain.auth.user.User;
import com.uwords.domain.common.UnavailableException;
import com.uwords.usecase.port.auth.user.UserRepositoryPort;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

public class FakeUserRepository implements UserRepositoryPort {

    public final Map<UUID, User> users = new HashMap<>();
    public boolean unavailable;

    @Override
    public Optional<User> findById(UUID userId) {
        if (unavailable) {
            throw new UnavailableException("account storage is unreachable");
        }
        return Optional.ofNullable(users.get(userId));
    }
}
