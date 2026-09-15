package com.uwords.adapter.email;

import com.uwords.usecase.port.notifications.EmailSenderPort;
import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;
import org.springframework.mail.MailPreparationException;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Component;

@Component
public class SmtpSender implements EmailSenderPort {

    private final JavaMailSender mailSender;
    private final EmailProperties properties;

    public SmtpSender(JavaMailSender mailSender, EmailProperties properties) {
        this.mailSender = mailSender;
        this.properties = properties;
    }

    @Override
    public void send(String to, String subject, String body) {
        mailSender.send(compose(to, subject, body));
    }

    private MimeMessage compose(String to, String subject, String body) {
        MimeMessage message = mailSender.createMimeMessage();
        try {
            MimeMessageHelper helper =
                    new MimeMessageHelper(message, false, SmtpSenderConfiguration.ENCODING);
            helper.setFrom(properties.sender());
            helper.setTo(to);
            helper.setSubject(subject);
            helper.setText(body);
        } catch (MessagingException cause) {
            throw new MailPreparationException(cause);
        }
        return message;
    }
}
