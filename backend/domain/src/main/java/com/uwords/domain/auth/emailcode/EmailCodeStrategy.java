package com.uwords.domain.auth.emailcode;

import com.uwords.domain.auth.challenge.Challenge;
import com.uwords.domain.auth.challenge.ChallengeStrategy;
import com.uwords.domain.auth.challenge.ChallengeSubject;
import com.uwords.domain.auth.challenge.ChallengeType;
import com.uwords.domain.auth.code.CodeGenerator;
import com.uwords.domain.auth.code.CodePolicy;
import com.uwords.domain.auth.code.VerificationCode;
import com.uwords.domain.auth.user.AuthProvider;
import com.uwords.domain.auth.user.Email;
import com.uwords.domain.auth.user.ProviderAccount;
import com.uwords.domain.notifications.OutboundEmail;
import java.util.Map;

public class EmailCodeStrategy implements ChallengeStrategy {

    public static final String CODE_VARIABLE = "code";

    private final EmailCodeTemplate template;
    private final CodeGenerator codes;
    private final CodePolicy policy;

    public EmailCodeStrategy(EmailCodeTemplate template, CodeGenerator codes, CodePolicy policy) {
        this.template = template;
        this.codes = codes;
        this.policy = policy;
    }

    @Override
    public ChallengeType challengeType() {
        return ChallengeType.EMAIL_CODE;
    }

    @Override
    public ChallengeSubject subjectOf(String credential) {
        Email email = Email.of(credential);
        return new ChallengeSubject(email.value(), email.value());
    }

    @Override
    public VerificationCode issueSecret() {
        int length = policy.codeLength();
        return VerificationCode.of(codes.generate(length), length);
    }

    @Override
    public OutboundEmail notificationFor(Challenge challenge, ChallengeSubject subject) {
        return new OutboundEmail(
                subject.recipient(),
                template.sender(),
                template.subject(),
                challenge.id(),
                template.templatePath(),
                Map.of(CODE_VARIABLE, challenge.secretValue()));
    }

    @Override
    public VerificationCode restoreSecret(String value) {
        return VerificationCode.of(value, policy.codeLength());
    }

    @Override
    public ProviderAccount accountFor(String uniquenessKey) {
        return new ProviderAccount(AuthProvider.EMAIL, uniquenessKey);
    }
}
