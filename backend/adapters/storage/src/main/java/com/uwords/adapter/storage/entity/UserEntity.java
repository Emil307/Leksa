package com.uwords.adapter.storage.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.annotations.DynamicInsert;

@Entity
@Table(name = "t_users", schema = "auth")
@DynamicInsert
@Getter
@Setter
@NoArgsConstructor
public class UserEntity {

    public static final String GENDER_COLUMN_DEFINITION = "user_gender";

    @Id
    private UUID id;

    @Column(nullable = false)
    private String name;

    private String surname;

    private String email;

    @Column(name = "is_superuser")
    private Boolean isSuperuser;

    @Column(name = "created_at")
    private Instant createdAt;

    @Column(name = "updated_at")
    private Instant updatedAt;

    @Column(name = "avatar_id")
    private UUID avatarId;

    private LocalDate birthday;

    @Column(columnDefinition = GENDER_COLUMN_DEFINITION)
    private String gender;

    private String city;

    private String phone;
}
