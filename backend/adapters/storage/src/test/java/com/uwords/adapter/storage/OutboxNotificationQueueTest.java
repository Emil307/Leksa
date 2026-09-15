package com.uwords.adapter.storage;

import com.uwords.adapter.storage.testing.statements.OutboxStatements;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class OutboxNotificationQueueTest {

    private OutboxStatements statements;

    @BeforeEach
    void createStatements() {
        statements = new OutboxStatements();
    }

    @Test
    void shouldStoreTheNotificationAsAnActiveEmailRow() {
        statements.enqueuePendingNotification();

        statements.assertStoredAsActiveEmailCarryingThePayload();
    }

    @Test
    void shouldReturnTheIdentifierOfTheWrittenRow() {
        statements.enqueuePendingNotification();

        statements.assertReturnedIdentifierIsTheWrittenRow();
    }

    @Test
    void shouldReuseTheMessageIdentifierInsteadOfMintingANewOne() {
        statements.enqueuePendingNotification();
        statements.enqueuePendingNotification();

        statements.assertEveryEnqueueReusedTheMessageIdentifier();
    }
}
