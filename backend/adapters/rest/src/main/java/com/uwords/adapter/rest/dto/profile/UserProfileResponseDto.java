package com.uwords.adapter.rest.dto.profile;

import com.uwords.domain.auth.user.Gender;
import com.uwords.domain.auth.user.User;
import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;

public record UserProfileResponseDto(
        UUID id,
        String name,
        String surname,
        String email,
        Boolean isSuperuser,
        String createdAt,
        String updatedAt,
        UUID avatarId,
        String birthday,
        String gender,
        String city,
        String phone) {

    public static UserProfileResponseDto from(User user) {
        return new UserProfileResponseDto(
                user.id(),
                user.name(),
                user.surname(),
                user.email(),
                user.isSuperuser(),
                instant(user.createdAt()),
                instant(user.updatedAt()),
                user.avatarId(),
                calendarDate(user.birthday()),
                gender(user.gender()),
                user.city(),
                user.phone());
    }

    private static String instant(Instant value) {
        return value == null ? null : value.toString();
    }

    private static String calendarDate(LocalDate value) {
        return value == null ? null : value.toString();
    }

    private static String gender(Gender value) {
        return value == null ? null : value.value();
    }
}
