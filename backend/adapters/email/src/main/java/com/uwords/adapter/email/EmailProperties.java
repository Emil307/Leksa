package com.uwords.adapter.email;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;

@ConfigurationProperties(prefix = "mail")
public record EmailProperties(
        @DefaultValue("localhost") String host,
        @DefaultValue("1025") int port,
        @DefaultValue("") String username,
        @DefaultValue("") String password,
        @DefaultValue("false") boolean useTls,
        @DefaultValue("no-reply@uwords.local") String sender,
        @DefaultValue("60000") int timeoutMillis) {
}
