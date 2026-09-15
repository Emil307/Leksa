package com.uwords.application.config;

import jakarta.validation.constraints.NotBlank;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;
import org.springframework.validation.annotation.Validated;

@Validated
@ConfigurationProperties(prefix = "auth.email-code")
public record EmailCodeTemplateProperties(
        @DefaultValue("Код для входа в uwords") @NotBlank String subject,
        @DefaultValue("auth/email_code.html") @NotBlank String templatePath) {
}
