package com.uwords.application.testing.statements;

import static com.uwords.application.testing.statements.AccessTokenData.SECRET;
import static com.uwords.application.testing.statements.ApplicationBootData.BLANK_SECRET;
import static com.uwords.application.testing.statements.ApplicationBootData.JWT_SECRET_PROPERTY;
import static org.assertj.core.api.Assertions.assertThat;

import com.uwords.application.config.AuthTokenProperties;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.boot.test.context.runner.ApplicationContextRunner;

public class SigningSecretStatements {

    private static final String ACCESS_TOKEN_TTL_PROPERTY = "auth.token.access-token-ttl-seconds=900";
    private static final String REFRESH_TOKEN_TTL_PROPERTY = "auth.token.refresh-token-ttl-seconds=2592000";

    private static final String JWT_SECRET_PREFIX = "auth.token";
    private static final String JWT_SECRET_FIELD = "jwtSecret";

    private String secret = SECRET;
    private ApplicationContextRunner runner;

    public void givenABlankSigningSecret() {
        secret = BLANK_SECRET;
    }

    public void whenBuildingTheApplicationIsAttempted() {
        runner = new ApplicationContextRunner()
                .withUserConfiguration(AuthTokenPropertiesHolder.class)
                .withPropertyValues(
                        JWT_SECRET_PROPERTY + "=" + secret,
                        ACCESS_TOKEN_TTL_PROPERTY,
                        REFRESH_TOKEN_TTL_PROPERTY);
    }

    public void assertBootRefusedTheBlankSigningSecret() {
        runner.run(context -> assertThat(context)
                .hasFailed()
                .getFailure()
                .rootCause()
                .hasMessageContaining(JWT_SECRET_PREFIX)
                .hasMessageContaining(JWT_SECRET_FIELD));
    }

    @EnableConfigurationProperties(AuthTokenProperties.class)
    static class AuthTokenPropertiesHolder {
    }
}
