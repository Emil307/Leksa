package com.uwords.usecase.port.notifications;

import com.uwords.domain.notifications.OutboundNotification;
import java.util.UUID;

public interface NotificationQueuePort {

    UUID enqueue(OutboundNotification message);
}
