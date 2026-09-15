package com.uwords.adapter.storage.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.annotations.DynamicInsert;

@Entity
@Table(name = "t_auth", schema = "auth")
@DynamicInsert
@Getter
@Setter
@NoArgsConstructor
public class AuthAccountEntity {

    public static final int MAX_PROVIDER_OCTETS = 32;
    public static final int MAX_PROVIDER_ID_OCTETS = 254;

    @Id
    private UUID id;

    @Column(name = "user_id", nullable = false)
    private UUID userId;

    @Column(nullable = false, length = MAX_PROVIDER_OCTETS)
    private String provider;

    @Column(name = "provider_id", nullable = false, length = MAX_PROVIDER_ID_OCTETS)
    private String providerId;

    @Column(name = "created_at")
    private Instant createdAt;

    @Column(name = "updated_at")
    private Instant updatedAt;
}
