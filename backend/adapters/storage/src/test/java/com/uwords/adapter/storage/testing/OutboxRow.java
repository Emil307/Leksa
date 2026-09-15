package com.uwords.adapter.storage.testing;

import java.util.UUID;

public record OutboxRow(UUID id, String type, String status, String data) {
}
