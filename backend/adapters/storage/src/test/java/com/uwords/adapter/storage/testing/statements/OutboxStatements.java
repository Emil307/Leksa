package com.uwords.adapter.storage.testing.statements;

import static org.assertj.core.api.Assertions.assertThat;

import com.uwords.adapter.storage.OutboxNotificationQueue;
import com.uwords.adapter.storage.testing.FakeNotificationOutboxEntries;
import com.uwords.adapter.storage.testing.OutboxRow;
import com.uwords.domain.notifications.OutboundEmail;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;

public class OutboxStatements {

    public static final UUID MESSAGE_ID = UUID.fromString("6f1b0d2e-9a44-4a1f-8f21-3c5b8e7d0a11");

    private static final String RECIPIENT = "learner@uwords.app";
    private static final String SENDER = "no-reply@uwords.app";
    private static final String SUBJECT = "Kod dlya vhoda";
    private static final String TEMPLATE_PATH = "auth/email_code.html";
    private static final String CODE = "004321";
    private static final String EXPECTED_DATA = "{\"to\":\"learner@uwords.app\","
            + "\"from\":\"no-reply@uwords.app\","
            + "\"subject\":\"Kod dlya vhoda\","
            + "\"messageId\":\"6f1b0d2e-9a44-4a1f-8f21-3c5b8e7d0a11\","
            + "\"templatePath\":\"auth/email_code.html\","
            + "\"variables\":{\"code\":\"004321\"}}";
    private static final OutboxRow EXPECTED_ROW = new OutboxRow(MESSAGE_ID, "EMAIL", "ACTIVE", EXPECTED_DATA);

    private final FakeNotificationOutboxEntries entries = new FakeNotificationOutboxEntries();
    private final OutboxNotificationQueue queue = new OutboxNotificationQueue(entries);
    private final OutboundEmail message =
            new OutboundEmail(RECIPIENT, SENDER, SUBJECT, MESSAGE_ID, TEMPLATE_PATH, Map.of("code", CODE));
    private final List<UUID> returned = new ArrayList<>();

    public void enqueuePendingNotification() {
        returned.add(queue.enqueue(message));
    }

    public void assertStoredAsActiveEmailCarryingThePayload() {
        assertThat(entries.written).isEqualTo(List.of(EXPECTED_ROW));
    }

    public void assertReturnedIdentifierIsTheWrittenRow() {
        assertThat(returned).isEqualTo(List.of(MESSAGE_ID));
        assertThat(entries.written).isEqualTo(List.of(EXPECTED_ROW));
    }

    public void assertEveryEnqueueReusedTheMessageIdentifier() {
        assertThat(returned).isEqualTo(List.of(MESSAGE_ID, MESSAGE_ID));
        assertThat(entries.written).isEqualTo(List.of(EXPECTED_ROW, EXPECTED_ROW));
    }
}
