package com.uwords.adapter.rest.controller;

import com.uwords.adapter.rest.dto.auth.SessionRefreshRequestDto;
import com.uwords.adapter.rest.dto.auth.SessionRefreshResponseDto;
import com.uwords.usecase.service.auth.RefreshSessionTokensService;
import com.uwords.usecase.service.auth.RotatedSessionTokens;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping(RestPaths.TOKEN_PREFIX)
public class AuthTokenController {

    private final RefreshSessionTokensService refreshSessionService;

    public AuthTokenController(RefreshSessionTokensService refreshSessionService) {
        this.refreshSessionService = refreshSessionService;
    }

    @PostMapping("/refresh")
    public ResponseEntity<SessionRefreshResponseDto> refresh(@RequestBody SessionRefreshRequestDto body) {
        RotatedSessionTokens rotated = refreshSessionService.refresh(body.toUsecaseRequest());
        return ResponseEntity.ok(SessionRefreshResponseDto.from(rotated));
    }
}
