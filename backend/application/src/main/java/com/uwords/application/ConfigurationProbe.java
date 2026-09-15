package com.uwords.application;

import com.uwords.adapter.email.EmailProperties;
import com.uwords.adapter.storage.DbProperties;
import com.uwords.application.config.AuthTokenProperties;
import com.uwords.application.config.ChallengeProperties;
import com.uwords.application.config.EmailCodeTemplateProperties;
import org.springframework.boot.Banner;
import org.springframework.boot.WebApplicationType;
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.core.env.ConfigurableEnvironment;
import org.springframework.core.env.StandardEnvironment;

@EnableConfigurationProperties({
        AuthTokenProperties.class,
        ChallengeProperties.class,
        EmailCodeTemplateProperties.class,
        EmailProperties.class,
        DbProperties.class})
public class ConfigurationProbe {

    private static final int CONFIGURATION_REJECTED = 1;

    public static void main(String[] args) {
        ConfigurableEnvironment environment = new StandardEnvironment();
        try (ConfigurableApplicationContext context = probe(args, environment)) {
            context.getBean(AuthTokenProperties.class);
        } catch (RuntimeException refusal) {
            System.err.println(new ConfigurationRefusal(environment).describe(refusal));
            System.exit(CONFIGURATION_REJECTED);
        }
    }

    private static ConfigurableApplicationContext probe(String[] args, ConfigurableEnvironment environment) {
        return new SpringApplicationBuilder(ConfigurationProbe.class)
                .web(WebApplicationType.NONE)
                .bannerMode(Banner.Mode.OFF)
                .environment(environment)
                .run(args);
    }
}
