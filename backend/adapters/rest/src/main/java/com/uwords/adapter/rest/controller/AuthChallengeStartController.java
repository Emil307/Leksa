package com.uwords.adapter.rest.controller;

import com.uwords.adapter.rest.dto.auth.ChallengeStartRequestDto;
import com.uwords.adapter.rest.dto.auth.ChallengeStartResponseDto;
import com.uwords.usecase.service.auth.StartAuthChallengeService;
import com.uwords.usecase.service.auth.StartedChallenge;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping(RestPaths.CHALLENGE_PREFIX)
public class AuthChallengeStartController {

    private final StartAuthChallengeService startChallengeService;

    public AuthChallengeStartController(StartAuthChallengeService startChallengeService) {
        this.startChallengeService = startChallengeService;
    }

    @PostMapping("/start")
    public ResponseEntity<ChallengeStartResponseDto> start(@RequestBody ChallengeStartRequestDto body) {
        StartedChallenge started = startChallengeService.start(body.toUsecaseRequest());
        return ResponseEntity.ok(ChallengeStartResponseDto.from(started));
    }
}
