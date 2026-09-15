package com.uwords.usecase.service;

import com.uwords.usecase.port.system.HealthCheckPort;
import org.springframework.stereotype.Service;

@Service
public class HealthService {

    private final HealthCheckPort database;

    public HealthService(HealthCheckPort database) {
        this.database = database;
    }

    public boolean isReady() {
        return database.ping();
    }
}
