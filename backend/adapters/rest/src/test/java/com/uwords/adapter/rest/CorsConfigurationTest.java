package com.uwords.adapter.rest;

import com.uwords.adapter.rest.testing.CorsStatements;
import org.junit.jupiter.api.Test;

class CorsConfigurationTest {

    private final CorsStatements statements = new CorsStatements();

    @Test
    void shouldAllowConfiguredOriginsOnApiPaths() {
        statements.givenAllowedOrigins("http://localhost:5174", "https://app.uwords.local");

        statements.whenCorsMappingsAreRegistered();

        statements.assertApiPathsAcceptOrigin("http://localhost:5174");
        statements.assertApiPathsAcceptOrigin("https://app.uwords.local");
        statements.assertApiPathsAllowMethods("GET", "POST", "OPTIONS");
    }

    @Test
    void shouldRejectUnknownOrigins() {
        statements.givenAllowedOrigins("http://localhost:5174");

        statements.whenCorsMappingsAreRegistered();

        statements.assertApiPathsRejectOrigin("http://evil.example");
    }

    @Test
    void shouldRegisterNothingWhenNoOriginIsConfigured() {
        statements.givenAllowedOrigins();

        statements.whenCorsMappingsAreRegistered();

        statements.assertNoCorsMappingIsRegistered();
    }
}
