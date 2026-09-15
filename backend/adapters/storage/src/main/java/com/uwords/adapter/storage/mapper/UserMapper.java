package com.uwords.adapter.storage.mapper;

import com.uwords.adapter.storage.entity.UserEntity;
import com.uwords.domain.auth.user.Gender;
import com.uwords.domain.auth.user.User;
import java.util.Arrays;

public final class UserMapper {

    private UserMapper() {
    }

    public static User toDomain(UserEntity entity) {
        return new User(
                entity.getId(),
                entity.getName(),
                entity.getSurname(),
                entity.getEmail(),
                entity.getIsSuperuser(),
                entity.getCreatedAt(),
                entity.getUpdatedAt(),
                entity.getAvatarId(),
                entity.getBirthday(),
                genderOf(entity.getGender()),
                entity.getCity(),
                entity.getPhone());
    }

    private static Gender genderOf(String stored) {
        if (stored == null) {
            return null;
        }
        return Arrays.stream(Gender.values())
                .filter(gender -> gender.value().equals(stored))
                .findFirst()
                .orElseThrow();
    }
}
