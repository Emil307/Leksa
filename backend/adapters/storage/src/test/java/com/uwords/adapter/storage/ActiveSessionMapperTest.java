package com.uwords.adapter.storage;

import com.uwords.adapter.storage.testing.statements.ActiveSessionMapperStatements;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ActiveSessionMapperTest {

    private ActiveSessionMapperStatements statements;

    @BeforeEach
    void createStatements() {
        statements = new ActiveSessionMapperStatements();
    }

    @Test
    void shouldYieldNoSessionForALegacyRowWithoutExpiry() {
        statements.mapLegacySessionRow();

        statements.assertNoMappedSession();
    }
}
