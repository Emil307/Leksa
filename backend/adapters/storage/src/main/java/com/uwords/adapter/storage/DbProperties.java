package com.uwords.adapter.storage;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;

@ConfigurationProperties(prefix = "db")
public record DbProperties(
        @DefaultValue("localhost") String host,
        @DefaultValue("5432") int port,
        @DefaultValue("uwords") String name,
        @DefaultValue("uwords") String user,
        @DefaultValue("uwords") String password,
        @DefaultValue("10") int poolSize,
        @DefaultValue("5.0") double statementTimeoutSeconds) {

    private static final String JDBC_PREFIX = "jdbc:postgresql://";
    private static final long MILLIS_PER_SECOND = 1000L;

    public String jdbcUrl() {
        return JDBC_PREFIX + host + ":" + port + "/" + name;
    }

    public long statementTimeoutMillis() {
        return Math.round(statementTimeoutSeconds * MILLIS_PER_SECOND);
    }
}
