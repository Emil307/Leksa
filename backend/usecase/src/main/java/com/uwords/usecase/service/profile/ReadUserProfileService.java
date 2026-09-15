package com.uwords.usecase.service.profile;

import com.uwords.domain.auth.failure.AuthFailureReason;
import com.uwords.domain.auth.failure.Unauthorized;
import com.uwords.domain.auth.user.User;
import com.uwords.domain.common.UnavailableException;
import com.uwords.usecase.AuthenticatedCaller;
import com.uwords.usecase.port.auth.user.UserRepositoryPort;
import java.util.Optional;
import org.springframework.stereotype.Service;

@Service
public class ReadUserProfileService {

    private final UserRepositoryPort users;

    public ReadUserProfileService(UserRepositoryPort users) {
        this.users = users;
    }

    public User read(AuthenticatedCaller caller) {
        Optional<User> account = findAccount(caller);
        return account.orElseThrow(() -> Unauthorized.of(AuthFailureReason.ACCOUNT));
    }

    private Optional<User> findAccount(AuthenticatedCaller caller) {
        try {
            return users.findById(caller.userId());
        } catch (UnavailableException unreachable) {
            throw Unauthorized.of(AuthFailureReason.STORAGE);
        }
    }
}
