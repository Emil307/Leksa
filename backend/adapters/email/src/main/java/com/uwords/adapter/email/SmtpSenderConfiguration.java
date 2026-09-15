package com.uwords.adapter.email;

import java.util.Properties;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.JavaMailSenderImpl;

@Configuration
@EnableConfigurationProperties(EmailProperties.class)
public class SmtpSenderConfiguration {

    public static final String ENCODING = "UTF-8";

    private static final String SSL_ENABLE = "mail.smtp.ssl.enable";
    private static final String CONNECTION_TIMEOUT = "mail.smtp.connectiontimeout";
    private static final String READ_TIMEOUT = "mail.smtp.timeout";
    private static final String WRITE_TIMEOUT = "mail.smtp.writetimeout";

    @Bean
    public JavaMailSender javaMailSender(EmailProperties properties) {
        JavaMailSenderImpl sender = new JavaMailSenderImpl();
        sender.setHost(properties.host());
        sender.setPort(properties.port());
        sender.setUsername(emptyToNull(properties.username()));
        sender.setPassword(emptyToNull(properties.password()));
        sender.setDefaultEncoding(ENCODING);
        sender.setJavaMailProperties(transportProperties(properties));
        return sender;
    }

    private static Properties transportProperties(EmailProperties properties) {
        String timeout = Integer.toString(properties.timeoutMillis());
        Properties transport = new Properties();
        transport.setProperty(SSL_ENABLE, Boolean.toString(properties.useTls()));
        transport.setProperty(CONNECTION_TIMEOUT, timeout);
        transport.setProperty(READ_TIMEOUT, timeout);
        transport.setProperty(WRITE_TIMEOUT, timeout);
        return transport;
    }

    private static String emptyToNull(String value) {
        return value == null || value.isEmpty() ? null : value;
    }
}
