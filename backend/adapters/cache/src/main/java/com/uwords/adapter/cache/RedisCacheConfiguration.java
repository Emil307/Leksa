package com.uwords.adapter.cache;

import io.lettuce.core.ClientOptions;
import io.lettuce.core.SocketOptions;
import java.time.Duration;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisStandaloneConfiguration;
import org.springframework.data.redis.connection.lettuce.LettuceClientConfiguration;
import org.springframework.data.redis.connection.lettuce.LettuceConnectionFactory;
import org.springframework.data.redis.core.StringRedisTemplate;

@Configuration
public class RedisCacheConfiguration {

    private final String host;
    private final int port;
    private final String password;
    private final int database;
    private final long socketConnectTimeoutSeconds;
    private final long socketTimeoutSeconds;

    public RedisCacheConfiguration(
            @Value("${redis.host:localhost}") String host,
            @Value("${redis.port:6379}") int port,
            @Value("${redis.password:}") String password,
            @Value("${redis.db:0}") int database,
            @Value("${redis.socket-connect-timeout-seconds:5}") long socketConnectTimeoutSeconds,
            @Value("${redis.socket-timeout-seconds:5}") long socketTimeoutSeconds) {
        this.host = host;
        this.port = port;
        this.password = password;
        this.database = database;
        this.socketConnectTimeoutSeconds = socketConnectTimeoutSeconds;
        this.socketTimeoutSeconds = socketTimeoutSeconds;
    }

    @Bean
    public LettuceConnectionFactory redisConnectionFactory() {
        RedisStandaloneConfiguration server = new RedisStandaloneConfiguration(host, port);
        server.setDatabase(database);
        server.setPassword(password);
        return new LettuceConnectionFactory(server, clientConfiguration());
    }

    @Bean
    public StringRedisTemplate stringRedisTemplate(LettuceConnectionFactory redisConnectionFactory) {
        return new StringRedisTemplate(redisConnectionFactory);
    }

    private LettuceClientConfiguration clientConfiguration() {
        SocketOptions socketOptions = SocketOptions.builder()
                .connectTimeout(Duration.ofSeconds(socketConnectTimeoutSeconds))
                .build();
        return LettuceClientConfiguration.builder()
                .clientOptions(ClientOptions.builder().socketOptions(socketOptions).build())
                .commandTimeout(Duration.ofSeconds(socketTimeoutSeconds))
                .build();
    }
}
