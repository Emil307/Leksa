package com.uwords.adapter.email;

import com.icegreen.greenmail.junit5.GreenMailExtension;
import com.icegreen.greenmail.util.ServerSetupTest;
import com.uwords.adapter.email.testing.statements.SmtpSenderStatements;
import jakarta.mail.MessagingException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.RegisterExtension;

class SmtpSenderTest {

    private static final String CONFIGURED_SENDER = "no-reply@uwords.local";
    private static final String RECIPIENT = "learner@example.com";
    private static final String SUBJECT = "Welcome";
    private static final String BODY = "Hello";

    @RegisterExtension
    static final GreenMailExtension GREEN_MAIL = new GreenMailExtension(ServerSetupTest.SMTP.dynamicPort());

    private SmtpSenderStatements statements;

    @BeforeEach
    void createStatements() {
        statements = new SmtpSenderStatements(GREEN_MAIL, CONFIGURED_SENDER);
    }

    @Test
    void shouldSendMessageAddressedFromConfiguredSender() throws MessagingException {
        statements.whenMessageSent(RECIPIENT, SUBJECT, BODY);

        statements.assertDeliveredFrom(CONFIGURED_SENDER);
        statements.assertDeliveredTo(RECIPIENT);
        statements.assertDeliveredSubject(SUBJECT);
        statements.assertDeliveredBody(BODY);
    }

    @Test
    void shouldDispatchToConfiguredSmtpHostAndPort() {
        statements.whenMessageSent(RECIPIENT, SUBJECT, BODY);

        statements.assertExactlyOneMessageReachedConfiguredServer();
    }
}
