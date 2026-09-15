package com.uwords.domain.auth.emailcode;

public record EmailCodeTemplate(String sender, String subject, String templatePath) {
}
