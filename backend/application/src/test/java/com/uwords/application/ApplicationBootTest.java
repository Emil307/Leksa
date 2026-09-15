package com.uwords.application;

import static com.uwords.application.testing.statements.AccessTokenData.SECRET;

import com.uwords.application.testing.statements.ApplicationRoutesStatements;
import com.uwords.application.testing.statements.ExpiredTokenStatements;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.ApplicationContext;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.testcontainers.containers.PostgreSQLContainer;

@SpringBootTest
@AutoConfigureMockMvc
class ApplicationBootTest {

    private static final long ACCESS_TOKEN_TTL_SECONDS = 900;
    private static final long REFRESH_TOKEN_TTL_SECONDS = 2592000;
    private static final String POSTGRES_IMAGE = "postgres:17-alpine";
    private static final PostgreSQLContainer<?> POSTGRES = new PostgreSQLContainer<>(POSTGRES_IMAGE);

    static {
        POSTGRES.start();
    }

    @Autowired
    private ApplicationContext context;

    @Autowired
    private MockMvc mockMvc;

    private ApplicationRoutesStatements routes;
    private ExpiredTokenStatements expiredToken;

    @DynamicPropertySource
    static void applicationProperties(DynamicPropertyRegistry registry) {
        registry.add("db.host", POSTGRES::getHost);
        registry.add("db.port", () -> POSTGRES.getMappedPort(PostgreSQLContainer.POSTGRESQL_PORT));
        registry.add("db.name", POSTGRES::getDatabaseName);
        registry.add("db.user", POSTGRES::getUsername);
        registry.add("db.password", POSTGRES::getPassword);
        registry.add("auth.token.jwt-secret", () -> SECRET);
        registry.add("auth.token.access-token-ttl-seconds", () -> ACCESS_TOKEN_TTL_SECONDS);
        registry.add("auth.token.refresh-token-ttl-seconds", () -> REFRESH_TOKEN_TTL_SECONDS);
    }

    @BeforeEach
    void createStatements() {
        routes = new ApplicationRoutesStatements(context);
        expiredToken = new ExpiredTokenStatements(mockMvc);
    }

    @Test
    void shouldExposeTheHealthRoute() {
        routes.assertTheHealthRouteIsExposed();
    }

    @Test
    void shouldRegisterTheDomainExceptionHandler() {
        routes.assertTheDomainExceptionHandlerIsRegistered();
    }

    @Test
    void shouldExposeTheChallengeStartRoute() {
        routes.assertTheChallengeStartRouteAcceptsOnlyPost();
    }

    @Test
    void shouldExposeTheChallengeVerifyRoute() {
        routes.assertTheChallengeVerifyRouteAcceptsOnlyPost();
    }

    @Test
    void shouldMountTheProfileRoute() {
        routes.assertTheProfileRouteIsMountedAsAGuardedRead();
    }

    @Test
    void shouldRefuseAnExpiredTokenThroughTheRealWiredClock() throws Exception {
        expiredToken.givenAnExpiredButCorrectlySignedToken();

        expiredToken.whenTheProfileIsRequested();

        expiredToken.assertTheWiredClockRefusedTheRequestWithTheUniform401();
    }
}
