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
@Table(name = "t_outbox", schema = "notifications")
@DynamicInsert
@Getter
@Setter
@NoArgsConstructor
public class NotificationOutboxEntity {

    public static final int MAX_TYPE_OCTETS = 64;
    public static final int MAX_STATUS_OCTETS = 16;
    public static final String DATA_COLUMN_DEFINITION = "jsonb";

    @Id
    private UUID id;

    @Column(nullable = false, length = MAX_TYPE_OCTETS)
    private String type;

    @Column(nullable = false, length = MAX_STATUS_OCTETS)
    private String status;

    @Column(nullable = false, columnDefinition = DATA_COLUMN_DEFINITION)
    private String data;

    private Integer attempts;

    @Column(name = "last_error")
    private String lastError;

    @Column(name = "created_at")
    private Instant createdAt;

    @Column(name = "updated_at")
    private Instant updatedAt;
}
