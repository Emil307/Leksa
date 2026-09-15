package com.uwords.application.testing.statements;

import static com.uwords.application.testing.statements.ApplicationBootData.CHALLENGE_START_PATH;
import static com.uwords.application.testing.statements.ApplicationBootData.CHALLENGE_VERIFY_PATH;
import static com.uwords.application.testing.statements.ApplicationBootData.HEALTH_PATH;
import static com.uwords.application.testing.statements.ApplicationBootData.PROFILE_PATH;
import static org.assertj.core.api.Assertions.assertThat;

import com.uwords.adapter.rest.dto.profile.UserProfileResponseDto;
import com.uwords.adapter.rest.security.AccessTokenInterceptor;
import com.uwords.domain.common.BaseDomainException;
import com.uwords.domain.common.UnauthorizedException;
import java.lang.reflect.Method;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.stream.Collectors;
import org.springframework.aop.support.AopUtils;
import org.springframework.context.ApplicationContext;
import org.springframework.core.ResolvableType;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.HandlerMethod;
import org.springframework.web.servlet.HandlerExecutionChain;
import org.springframework.web.servlet.mvc.method.RequestMappingInfo;
import org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping;

public class ApplicationRoutesStatements {

    private final ApplicationContext context;
    private final RequestMappingHandlerMapping handlerMapping;

    public ApplicationRoutesStatements(ApplicationContext context) {
        this.context = context;
        this.handlerMapping = context.getBean(RequestMappingHandlerMapping.class);
    }

    public void assertTheHealthRouteIsExposed() {
        assertThat(methodsOf(HEALTH_PATH)).containsExactly(RequestMethod.GET);
    }

    public void assertTheDomainExceptionHandlerIsRegistered() {
        assertThat(handledExceptions())
                .contains(BaseDomainException.class, UnauthorizedException.class);
    }

    public void assertTheChallengeStartRouteAcceptsOnlyPost() {
        assertThat(methodsOf(CHALLENGE_START_PATH)).containsExactly(RequestMethod.POST);
    }

    public void assertTheChallengeVerifyRouteAcceptsOnlyPost() {
        assertThat(methodsOf(CHALLENGE_VERIFY_PATH)).containsExactly(RequestMethod.POST);
    }

    public void assertTheProfileRouteIsMountedAsAGuardedRead() {
        assertThat(methodsOf(PROFILE_PATH)).containsExactly(RequestMethod.GET);
        assertThat(answerTypeOf(PROFILE_PATH)).isEqualTo(UserProfileResponseDto.class);
        assertThat(interceptorsOf(PROFILE_PATH)).hasAtLeastOneElementOfType(AccessTokenInterceptor.class);
    }

    private Set<RequestMethod> methodsOf(String path) {
        return mappingsOf(path).stream()
                .flatMap(info -> info.getMethodsCondition().getMethods().stream())
                .collect(Collectors.toSet());
    }

    private Class<?> answerTypeOf(String path) {
        Map.Entry<RequestMappingInfo, HandlerMethod> mapping = handlerMapping.getHandlerMethods().entrySet().stream()
                .filter(entry -> patternsOf(entry.getKey()).contains(path))
                .findFirst()
                .orElseThrow();
        ResolvableType answer = ResolvableType.forMethodParameter(mapping.getValue().getReturnType());
        return answer.hasGenerics() ? answer.getGeneric(0).resolve() : answer.resolve();
    }

    private List<?> interceptorsOf(String path) {
        try {
            HandlerExecutionChain chain =
                    handlerMapping.getHandler(new MockHttpServletRequest(RequestMethod.GET.name(), path));
            return Objects.requireNonNull(chain).getInterceptorList();
        } catch (Exception refusal) {
            throw new IllegalStateException(path, refusal);
        }
    }

    private Set<RequestMappingInfo> mappingsOf(String path) {
        return handlerMapping.getHandlerMethods().keySet().stream()
                .filter(info -> patternsOf(info).contains(path))
                .collect(Collectors.toSet());
    }

    private static Set<String> patternsOf(RequestMappingInfo info) {
        return Objects.requireNonNull(info.getPathPatternsCondition()).getPatternValues();
    }

    private Set<Class<?>> handledExceptions() {
        return context.getBeansWithAnnotation(RestControllerAdvice.class).values().stream()
                .map(AopUtils::getTargetClass)
                .flatMap(type -> Arrays.stream(type.getDeclaredMethods()))
                .map(ApplicationRoutesStatements::declaredExceptions)
                .filter(Objects::nonNull)
                .flatMap(Arrays::stream)
                .collect(Collectors.toSet());
    }

    private static Class<?>[] declaredExceptions(Method method) {
        ExceptionHandler declaration = method.getAnnotation(ExceptionHandler.class);
        return declaration == null ? null : declaration.value();
    }
}
