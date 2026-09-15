package com.uwords.adapter.rest.testing;

import com.uwords.adapter.rest.config.CorsProperties;
import com.uwords.adapter.rest.config.RestWebConfiguration;
import com.uwords.usecase.service.auth.AuthenticateRequestService;
import java.util.List;
import java.util.Map;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;

public class CorsStatements {

    private static final String API_PATTERN = "/api/**";

    private CorsProperties properties;
    private Map<String, CorsConfiguration> configurations;

    public void givenAllowedOrigins(String... origins) {
        properties = new CorsProperties(List.of(origins));
    }

    public void whenCorsMappingsAreRegistered() {
        RestWebConfiguration configuration = new RestWebConfiguration(
                mock(AuthenticateRequestService.class), properties);
        ExposedCorsRegistry registry = new ExposedCorsRegistry();
        configuration.addCorsMappings(registry);
        configurations = registry.configurations();
    }

    public void assertApiPathsAcceptOrigin(String origin) {
        assertThat(apiConfiguration().checkOrigin(origin)).isEqualTo(origin);
    }

    public void assertApiPathsRejectOrigin(String origin) {
        assertThat(apiConfiguration().checkOrigin(origin)).isNull();
    }

    public void assertApiPathsAllowMethods(String... methods) {
        assertThat(apiConfiguration().getAllowedMethods()).containsExactly(methods);
    }

    public void assertNoCorsMappingIsRegistered() {
        assertThat(configurations).isEmpty();
    }

    private CorsConfiguration apiConfiguration() {
        assertThat(configurations).containsOnlyKeys(API_PATTERN);
        return configurations.get(API_PATTERN);
    }

    private static final class ExposedCorsRegistry extends CorsRegistry {

        Map<String, CorsConfiguration> configurations() {
            return getCorsConfigurations();
        }
    }
}
