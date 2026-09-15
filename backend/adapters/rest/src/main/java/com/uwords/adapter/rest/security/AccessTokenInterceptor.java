package com.uwords.adapter.rest.security;

import com.uwords.usecase.service.auth.AuthenticateRequestService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.web.servlet.HandlerInterceptor;

public class AccessTokenInterceptor implements HandlerInterceptor {

    public static final String CALLER_ATTRIBUTE = "com.uwords.adapter.rest.security.caller";

    private static final String AUTHORIZATION_HEADER = "Authorization";

    private final AuthenticateRequestService authenticateService;

    public AccessTokenInterceptor(AuthenticateRequestService authenticateService) {
        this.authenticateService = authenticateService;
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        request.setAttribute(
                CALLER_ATTRIBUTE, authenticateService.authenticate(request.getHeader(AUTHORIZATION_HEADER)));
        return true;
    }
}
