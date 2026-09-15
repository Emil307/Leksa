package com.uwords.application.system;

import com.uwords.usecase.port.system.IdGeneratorPort;
import java.util.UUID;
import org.springframework.stereotype.Component;

@Component
public class UuidGenerator implements IdGeneratorPort {

    @Override
    public UUID newId() {
        return UUID.randomUUID();
    }
}
