package com.uwords.architecture;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.lang.ArchRule;
import org.junit.jupiter.api.Test;

import static com.tngtech.archunit.library.Architectures.layeredArchitecture;

class LayerDependencyRulesTest {

    private final JavaClasses classes = new ClassFileImporter()
            .withImportOption(ImportOption.Predefined.DO_NOT_INCLUDE_TESTS)
            .importPackages(ArchitecturePackages.ROOT);

    @Test
    void dependenciesFlowInward() {
        ArchRule rule = layeredArchitecture()
                .consideringOnlyDependenciesInLayers()
                .layer("Domain").definedBy(ArchitecturePackages.DOMAIN)
                .layer("Usecase").definedBy(ArchitecturePackages.USECASE)
                .layer("Adapters").definedBy(ArchitecturePackages.ADAPTERS)
                .layer("Application").definedBy(ArchitecturePackages.APPLICATION)
                .whereLayer("Application").mayNotBeAccessedByAnyLayer()
                .whereLayer("Adapters").mayOnlyBeAccessedByLayers("Application")
                .whereLayer("Usecase").mayOnlyBeAccessedByLayers("Adapters", "Application")
                .whereLayer("Domain").mayOnlyBeAccessedByLayers("Usecase", "Adapters", "Application");

        rule.check(classes);
    }
}
