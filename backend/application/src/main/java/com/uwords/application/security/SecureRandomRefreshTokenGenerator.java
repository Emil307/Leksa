package com.uwords.application.security;

import com.uwords.usecase.port.auth.session.RefreshTokenGeneratorPort;
import java.security.SecureRandom;
import java.util.Base64;
import org.springframework.stereotype.Component;

@Component
public class SecureRandomRefreshTokenGenerator implements RefreshTokenGeneratorPort {

    private static final int TOKEN_BYTES = 32;

    private final SecureRandom random = new SecureRandom();

    @Override
    public String generate() {
        byte[] material = new byte[TOKEN_BYTES];
        random.nextBytes(material);
        return Base64.getUrlEncoder().withoutPadding().encodeToString(material);
    }
}
