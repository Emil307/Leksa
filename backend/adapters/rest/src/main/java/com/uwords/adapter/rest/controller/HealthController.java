package com.uwords.adapter.rest.controller;

import com.uwords.adapter.rest.dto.system.HealthResponseDto;
import com.uwords.usecase.service.HealthService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HealthController {

    private final HealthService healthService;

    public HealthController(HealthService healthService) {
        this.healthService = healthService;
    }

    @GetMapping(RestPaths.HEALTH_PATH)
    public ResponseEntity<HealthResponseDto> health() {
        boolean ready = healthService.isReady();
        return ResponseEntity.status(ready ? HttpStatus.OK : HttpStatus.SERVICE_UNAVAILABLE)
                .body(HealthResponseDto.of(ready));
    }
}
