package com.uwords.adapter.storage;

import com.uwords.adapter.storage.entity.UserEntity;
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import javax.sql.DataSource;
import org.hibernate.cfg.AvailableSettings;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.boot.autoconfigure.orm.jpa.HibernatePropertiesCustomizer;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@EntityScan(basePackageClasses = UserEntity.class)
@EnableConfigurationProperties(DbProperties.class)
public class StorageDataSourceConfiguration {

    private static final String OPTIONS_PROPERTY = "options";
    private static final String STATEMENT_TIMEOUT_OPTION = "-c statement_timeout=";
    private static final String STRING_TYPE_PROPERTY = "stringtype";
    private static final String UNSPECIFIED_STRING_TYPE = "unspecified";
    private static final String VALIDATE_SCHEMA = "validate";

    @Bean
    public DataSource dataSource(DbProperties properties) {
        HikariConfig configuration = new HikariConfig();
        configuration.setJdbcUrl(properties.jdbcUrl());
        configuration.setUsername(properties.user());
        configuration.setPassword(properties.password());
        configuration.setMaximumPoolSize(properties.poolSize());
        configuration.addDataSourceProperty(
                OPTIONS_PROPERTY, STATEMENT_TIMEOUT_OPTION + properties.statementTimeoutMillis());
        configuration.addDataSourceProperty(STRING_TYPE_PROPERTY, UNSPECIFIED_STRING_TYPE);
        return new HikariDataSource(configuration);
    }

    @Bean
    public HibernatePropertiesCustomizer storageSchemaValidation() {
        return properties -> properties.put(AvailableSettings.HBM2DDL_AUTO, VALIDATE_SCHEMA);
    }
}
