package com.uwords.application.config;

import com.uwords.application.system.FixedCodeGenerator;
import com.uwords.application.system.SecureNumericCodeGenerator;
import com.uwords.domain.auth.code.CodeGenerator;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class CodeGeneratorConfiguration {

    @Bean
    public CodeGenerator codeGenerator(ChallengeProperties properties) {
        if (properties.fixedCode().isEmpty()) {
            return new SecureNumericCodeGenerator();
        }
        return new FixedCodeGenerator(properties.fixedCode());
    }
}
