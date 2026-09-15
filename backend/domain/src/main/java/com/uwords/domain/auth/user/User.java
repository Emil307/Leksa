package com.uwords.domain.auth.user;

import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;

public record User(
        UUID id,
        String name,
        String surname,
        String email,
        Boolean isSuperuser,
        Instant createdAt,
        Instant updatedAt,
        UUID avatarId,
        LocalDate birthday,
        Gender gender,
        String city,
        String phone) {
}
