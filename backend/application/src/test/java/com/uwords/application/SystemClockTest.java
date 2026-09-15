package com.uwords.application;

import com.uwords.application.testing.statements.SystemClockStatements;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SystemClockTest {

    private SystemClockStatements statements;

    @BeforeEach
    void createStatements() {
        statements = new SystemClockStatements();
    }

    @Test
    void shouldAnswerAZoneIndependentUtcInstant() {
        statements.whenAClockOfAForeignZoneIsRead();

        statements.assertTheReadingIsAZoneIndependentUtcInstant();
    }

    @Test
    void shouldAnswerTheRealCurrentInstant() {
        statements.whenTheClockIsRead();

        statements.assertTheReadingTracksTheRealCurrentInstant();
    }

    @Test
    void shouldAnswerNonDecreasingInstants() {
        statements.whenTheClockIsReadTwice();

        statements.assertTheReadingsNeverGoBackwards();
    }
}
