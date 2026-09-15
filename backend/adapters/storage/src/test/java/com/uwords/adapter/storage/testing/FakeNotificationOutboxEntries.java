package com.uwords.adapter.storage.testing;

import com.uwords.adapter.storage.entity.NotificationOutboxEntity;
import com.uwords.adapter.storage.repository.NotificationOutboxEntries;
import java.util.ArrayList;
import java.util.List;

public class FakeNotificationOutboxEntries implements NotificationOutboxEntries {

    public final List<OutboxRow> written = new ArrayList<>();

    @Override
    public NotificationOutboxEntity addOne(NotificationOutboxEntity entry) {
        written.add(new OutboxRow(entry.getId(), entry.getType(), entry.getStatus(), entry.getData()));
        return entry;
    }
}
