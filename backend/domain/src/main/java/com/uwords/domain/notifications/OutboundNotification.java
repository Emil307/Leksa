package com.uwords.domain.notifications;

import java.util.Map;
import java.util.UUID;

public interface OutboundNotification {

    UUID messageId();

    NotificationType notificationType();

    Map<String, Object> payload();
}
