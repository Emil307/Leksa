package com.uwords.usecase.testing.fakes;

import com.uwords.domain.notifications.OutboundNotification;
import com.uwords.usecase.port.notifications.NotificationQueuePort;
import com.uwords.usecase.testing.recording.CallJournal;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class FakeNotificationQueue implements NotificationQueuePort {

    public static final String ENQUEUE = "enqueue";

    public final List<OutboundNotification> messages = new ArrayList<>();

    private final CallJournal journal;

    private RuntimeException failure;

    public FakeNotificationQueue(CallJournal journal) {
        this.journal = journal;
    }

    public CallJournal journal() {
        return journal;
    }

    public void failWith(RuntimeException failure) {
        this.failure = failure;
    }

    @Override
    public UUID enqueue(OutboundNotification message) {
        journal.record(ENQUEUE, message);
        if (failure != null) {
            throw failure;
        }
        messages.add(message);
        return message.messageId();
    }
}
