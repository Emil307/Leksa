package com.uwords.adapter.storage.repository;

import com.uwords.adapter.storage.entity.NotificationOutboxEntity;

public interface NotificationOutboxEntries {

    NotificationOutboxEntity addOne(NotificationOutboxEntity entry);
}
