package com.uwords.usecase.testing;

import com.uwords.domain.auth.code.CodePolicy;
import com.uwords.domain.auth.emailcode.EmailCodeStrategy;
import com.uwords.domain.auth.emailcode.EmailCodeTemplate;
import com.uwords.usecase.testing.fakes.StubCodeGenerator;
import java.time.Instant;

public final class EmailCodeFixtures {

    public static final String EMAIL = "learner@example.com";
    public static final String CODE = "042137";
    public static final Instant NOW = Instant.parse("2026-03-01T12:00:00Z");
    public static final int CODE_LENGTH = 6;
    public static final String SENDER = "no-reply@uwords.app";
    public static final String SUBJECT = "Uwords login code";
    public static final String TEMPLATE_PATH = "auth/email_code.html";

    private EmailCodeFixtures() {
    }

    public static EmailCodeStrategy buildEmailCodeStrategy(StubCodeGenerator codes) {
        return new EmailCodeStrategy(
                new EmailCodeTemplate(SENDER, SUBJECT, TEMPLATE_PATH), codes, new CodePolicy(CODE_LENGTH));
    }
}
