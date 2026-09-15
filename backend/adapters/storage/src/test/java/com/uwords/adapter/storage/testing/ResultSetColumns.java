package com.uwords.adapter.storage.testing;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.OffsetDateTime;

final class ResultSetColumns {

    private ResultSetColumns() {
    }

    static Instant instantOf(ResultSet row, String column) throws SQLException {
        OffsetDateTime moment = row.getObject(column, OffsetDateTime.class);
        return moment == null ? null : moment.toInstant();
    }
}
