package com.uwords.adapter.storage;

import com.uwords.adapter.storage.entity.NotificationOutboxEntity;
import com.uwords.adapter.storage.repository.NotificationOutboxEntries;
import com.uwords.domain.notifications.OutboundNotification;
import com.uwords.domain.notifications.OutboxStatus;
import com.uwords.usecase.port.notifications.NotificationQueuePort;
import java.util.UUID;
import org.springframework.stereotype.Component;

@Component
public class OutboxNotificationQueue implements NotificationQueuePort {

    private final NotificationOutboxEntries entries;

    public OutboxNotificationQueue(NotificationOutboxEntries entries) {
        this.entries = entries;
    }

    @Override
    public UUID enqueue(OutboundNotification message) {
        NotificationOutboxEntity entry = new NotificationOutboxEntity();
        entry.setId(message.messageId());
        entry.setType(message.notificationType().value());
        entry.setStatus(OutboxStatus.ACTIVE.value());
        entry.setData(PayloadJson.write(message.payload()));
        return entries.addOne(entry).getId();
    }
}
