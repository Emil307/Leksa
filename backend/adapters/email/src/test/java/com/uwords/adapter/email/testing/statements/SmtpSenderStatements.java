package com.uwords.adapter.email.testing.statements;

import static org.assertj.core.api.Assertions.assertThat;

import com.icegreen.greenmail.junit5.GreenMailExtension;
import com.icegreen.greenmail.util.GreenMailUtil;
import com.uwords.adapter.email.EmailProperties;
import com.uwords.adapter.email.SmtpSender;
import com.uwords.adapter.email.SmtpSenderConfiguration;
import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;

public class SmtpSenderStatements {

    private static final int TIMEOUT_MILLIS = 5000;
    private static final String NO_CREDENTIALS = "";

    private final GreenMailExtension greenMail;
    private final SmtpSender sender;

    public SmtpSenderStatements(GreenMailExtension greenMail, String from) {
        this.greenMail = greenMail;
        EmailProperties properties = new EmailProperties(
                greenMail.getSmtp().getBindTo(),
                greenMail.getSmtp().getPort(),
                NO_CREDENTIALS,
                NO_CREDENTIALS,
                false,
                from,
                TIMEOUT_MILLIS);
        this.sender = new SmtpSender(new SmtpSenderConfiguration().javaMailSender(properties), properties);
    }

    public void whenMessageSent(String to, String subject, String body) {
        sender.send(to, subject, body);
    }

    public void assertExactlyOneMessageReachedConfiguredServer() {
        assertThat(deliveredMessages()).hasSize(1);
    }

    public void assertDeliveredFrom(String expected) throws MessagingException {
        assertThat(deliveredMessage().getFrom()).extracting(Object::toString).containsExactly(expected);
    }

    public void assertDeliveredTo(String expected) throws MessagingException {
        assertThat(deliveredMessage().getAllRecipients()).extracting(Object::toString).containsExactly(expected);
    }

    public void assertDeliveredSubject(String expected) throws MessagingException {
        assertThat(deliveredMessage().getSubject()).isEqualTo(expected);
    }

    public void assertDeliveredBody(String expected) {
        assertThat(GreenMailUtil.getBody(deliveredMessage())).isEqualTo(expected);
    }

    private MimeMessage deliveredMessage() {
        MimeMessage[] delivered = deliveredMessages();
        assertThat(delivered).hasSize(1);
        return delivered[0];
    }

    private MimeMessage[] deliveredMessages() {
        assertThat(greenMail.waitForIncomingEmail(TIMEOUT_MILLIS, 1)).isTrue();
        return greenMail.getReceivedMessages();
    }
}
