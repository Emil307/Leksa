package com.uwords.adapter.rest.testing;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class BoomController {

    public static final String BOOM_PATH = "/boom";

    private final RuntimeException failure;

    public BoomController(RuntimeException failure) {
        this.failure = failure;
    }

    @GetMapping(BOOM_PATH)
    public ResponseEntity<Void> boom() {
        throw failure;
    }
}
