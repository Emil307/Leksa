package com.uwords.adapter.rest.config;

import com.uwords.adapter.rest.controller.RestPaths;
import com.uwords.adapter.rest.security.AccessTokenInterceptor;
import com.uwords.adapter.rest.security.AuthenticatedCallerArgumentResolver;
import com.uwords.usecase.service.auth.AuthenticateRequestService;
import java.util.List;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.method.support.HandlerMethodArgumentResolver;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
@EnableConfigurationProperties(CorsProperties.class)
public class RestWebConfiguration implements WebMvcConfigurer {

    private static final String API_PATTERN = "/api/**";
    private static final String[] API_METHODS = {"GET", "POST", "OPTIONS"};

    private final AuthenticateRequestService authenticateService;
    private final CorsProperties cors;

    public RestWebConfiguration(AuthenticateRequestService authenticateService, CorsProperties cors) {
        this.authenticateService = authenticateService;
        this.cors = cors;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new AccessTokenInterceptor(authenticateService))
                .addPathPatterns(RestPaths.PROFILE_PATH);
    }

    @Override
    public void addArgumentResolvers(List<HandlerMethodArgumentResolver> resolvers) {
        resolvers.add(new AuthenticatedCallerArgumentResolver());
    }

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        if (cors.allowedOrigins().isEmpty()) {
            return;
        }
        registry.addMapping(API_PATTERN)
                .allowedOrigins(cors.allowedOrigins().toArray(String[]::new))
                .allowedMethods(API_METHODS);
    }
}
