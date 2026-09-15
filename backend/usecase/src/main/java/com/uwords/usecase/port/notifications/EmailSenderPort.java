package com.uwords.usecase.port.notifications;

public interface EmailSenderPort {

    void send(String to, String subject, String body);
}
