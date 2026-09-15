package com.uwords.adapter.cache.testing;

import com.uwords.adapter.cache.RedisCacheConfiguration;
import com.uwords.adapter.cache.testing.fakes.EnvFile;
import org.springframework.data.redis.connection.lettuce.LettuceConnectionFactory;
import org.springframework.data.redis.core.StringRedisTemplate;

public final class LiveRedis {

    public static final String HOST_VARIABLE = "REDIS_HOST";
    public static final String PORT_VARIABLE = "REDIS_PORT";
    public static final String PASSWORD_VARIABLE = "REDIS_PASSWORD";
    public static final String DB_VARIABLE = "REDIS_DB";
    public static final String DEFAULT_HOST = "localhost";
    public static final int DEFAULT_PORT = 6379;
    public static final String DEFAULT_PASSWORD = "";
    public static final int DEFAULT_DB = 0;
    public static final long TIMEOUT_SECONDS = 5;

    private LiveRedis() {
    }

    public static StringRedisTemplate template() {
        RedisCacheConfiguration configuration = new RedisCacheConfiguration(
                EnvFile.value(HOST_VARIABLE, DEFAULT_HOST),
                EnvFile.number(PORT_VARIABLE, DEFAULT_PORT),
                EnvFile.value(PASSWORD_VARIABLE, DEFAULT_PASSWORD),
                EnvFile.number(DB_VARIABLE, DEFAULT_DB),
                TIMEOUT_SECONDS,
                TIMEOUT_SECONDS);
        LettuceConnectionFactory factory = configuration.redisConnectionFactory();
        factory.afterPropertiesSet();
        return configuration.stringRedisTemplate(factory);
    }
}
