package com.uwords.application.config;

import com.uwords.adapter.email.EmailProperties;
import com.uwords.domain.auth.challenge.ChallengePolicy;
import com.uwords.domain.auth.challenge.ChallengeStrategy;
import com.uwords.domain.auth.challenge.ChallengeStrategyRegistry;
import com.uwords.domain.auth.code.CodeGenerator;
import com.uwords.domain.auth.code.CodePolicy;
import com.uwords.domain.auth.emailcode.EmailCodeStrategy;
import com.uwords.domain.auth.emailcode.EmailCodeTemplate;
import com.uwords.domain.auth.session.SessionPolicy;
import java.util.List;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableConfigurationProperties({
        AuthTokenProperties.class,
        ChallengeProperties.class,
        EmailCodeTemplateProperties.class})
public class DomainPolicyConfiguration {

    @Bean
    public SessionPolicy sessionPolicy(AuthTokenProperties properties) {
        return SessionPolicy.of(
                properties.accessTokenTtlSeconds(), properties.refreshTokenTtlSeconds());
    }

    @Bean
    public ChallengePolicy challengePolicy(ChallengeProperties properties) {
        return new ChallengePolicy(
                properties.ttlSeconds(),
                properties.maxAttempts(),
                properties.resendCooldownSeconds(),
                properties.replayWindowSeconds());
    }

    @Bean
    public CodePolicy codePolicy(ChallengeProperties properties) {
        return new CodePolicy(properties.codeLength());
    }

    @Bean
    public EmailCodeTemplate emailCodeTemplate(
            EmailProperties mail, EmailCodeTemplateProperties template) {
        return new EmailCodeTemplate(mail.sender(), template.subject(), template.templatePath());
    }

    @Bean
    public EmailCodeStrategy emailCodeStrategy(
            EmailCodeTemplate template, CodeGenerator codes, CodePolicy policy) {
        return new EmailCodeStrategy(template, codes, policy);
    }

    @Bean
    public ChallengeStrategyRegistry challengeStrategyRegistry(List<ChallengeStrategy> strategies) {
        return new ChallengeStrategyRegistry(strategies);
    }
}
