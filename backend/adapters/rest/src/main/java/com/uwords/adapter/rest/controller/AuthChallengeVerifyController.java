package com.uwords.adapter.rest.controller;

import com.uwords.adapter.rest.dto.auth.ChallengeVerifyRequestDto;
import com.uwords.adapter.rest.dto.auth.ChallengeVerifyResponseDto;
import com.uwords.usecase.service.auth.VerifiedSession;
import com.uwords.usecase.service.auth.VerifyAuthChallengeService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping(RestPaths.CHALLENGE_PREFIX)
public class AuthChallengeVerifyController {

    private final VerifyAuthChallengeService verifyChallengeService;

    public AuthChallengeVerifyController(VerifyAuthChallengeService verifyChallengeService) {
        this.verifyChallengeService = verifyChallengeService;
    }

    @PostMapping("/verify")
    public ResponseEntity<ChallengeVerifyResponseDto> verify(@RequestBody ChallengeVerifyRequestDto body) {
        VerifiedSession verified = verifyChallengeService.verify(body.toUsecaseRequest());
        return ResponseEntity.ok(ChallengeVerifyResponseDto.from(verified));
    }
}
