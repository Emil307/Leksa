package com.uwords.domain.notifications;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

public record OutboundEmail(
        String to,
        String sender,
        String subject,
        UUID messageId,
        String templatePath,
        Map<String, String> variables) implements OutboundNotification {

    public static final String VARIABLES_KEY = "variables";

    public OutboundEmail {
        variables = variables == null
                ? Map.of()
                : Collections.unmodifiableMap(new LinkedHashMap<>(variables));
    }

    @Override
    public NotificationType notificationType() {
        return NotificationType.EMAIL;
    }

    @Override
    public Map<String, Object> payload() {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("to", to);
        body.put("from", sender);
        body.put("subject", subject);
        body.put("messageId", messageId.toString());
        body.put("templatePath", templatePath);
        body.put(VARIABLES_KEY, new LinkedHashMap<>(variables));
        return body;
    }

    @Override
    public String toString() {
        return "OutboundEmail(messageId=" + messageId
                + ", template=" + templatePath
                + ", variables=<redacted>)";
    }
}
