package com.uwords.application.config;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Positive;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;
import org.springframework.validation.annotation.Validated;

@Validated
@ConfigurationProperties(prefix = "auth.challenge")
public record ChallengeProperties(
        @DefaultValue("300") @Positive long ttlSeconds,
        @DefaultValue("5") @Positive int maxAttempts,
        @DefaultValue("60") @Positive long resendCooldownSeconds,
        @DefaultValue("60") @Positive long replayWindowSeconds,
        @DefaultValue("6") @Min(4) @Max(10) int codeLength,
        @DefaultValue("") @Pattern(regexp = "\\d*") String fixedCode) {
}
