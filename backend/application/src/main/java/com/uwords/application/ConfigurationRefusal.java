package com.uwords.application;

import java.util.LinkedHashSet;
import java.util.Locale;
import java.util.Optional;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.springframework.boot.context.properties.bind.validation.BindValidationException;
import org.springframework.core.NestedExceptionUtils;
import org.springframework.core.env.ConfigurableEnvironment;
import org.springframework.core.env.EnumerablePropertySource;
import org.springframework.core.env.PropertySource;
import org.springframework.validation.FieldError;
import org.springframework.validation.ObjectError;

public final class ConfigurationRefusal {

    private static final Pattern PLACEHOLDER = Pattern.compile("\\$\\{([A-Za-z_][A-Za-z0-9_]*)");
    private static final Pattern CAPITAL = Pattern.compile("([a-z0-9])([A-Z])");
    private static final String KEBAB = "$1-$2";
    private static final String SEPARATOR = ", ";

    private final ConfigurableEnvironment environment;

    public ConfigurationRefusal(ConfigurableEnvironment environment) {
        this.environment = environment;
    }

    public String describe(Throwable refusal) {
        String message = NestedExceptionUtils.getMostSpecificCause(refusal).getMessage();
        Set<String> variables = variablesOf(refusal);
        return variables.isEmpty() ? message : String.join(SEPARATOR, variables) + ": " + message;
    }

    private Set<String> variablesOf(Throwable refusal) {
        Set<String> variables = new LinkedHashSet<>();
        BindValidationException validation = validationFailureOf(refusal);
        if (validation == null) {
            return variables;
        }
        String prefix = validation.getValidationErrors().getName().toString();
        for (ObjectError error : validation.getValidationErrors().getAllErrors()) {
            if (error instanceof FieldError field) {
                variableOf(prefix + "." + kebab(field.getField())).ifPresent(variables::add);
            }
        }
        return variables;
    }

    private static BindValidationException validationFailureOf(Throwable refusal) {
        for (Throwable cause = refusal; cause != null; cause = cause.getCause()) {
            if (cause instanceof BindValidationException validation) {
                return validation;
            }
        }
        return null;
    }

    private Optional<String> variableOf(String property) {
        for (PropertySource<?> source : environment.getPropertySources()) {
            if (source instanceof EnumerablePropertySource<?> enumerable) {
                Object raw = enumerable.getProperty(property);
                Matcher matcher = raw == null ? null : PLACEHOLDER.matcher(raw.toString());
                if (matcher != null && matcher.find()) {
                    return Optional.of(matcher.group(1));
                }
            }
        }
        return Optional.empty();
    }

    private static String kebab(String field) {
        return CAPITAL.matcher(field).replaceAll(KEBAB).toLowerCase(Locale.ROOT);
    }
}
