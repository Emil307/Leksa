package com.uwords.architecture;

import com.tngtech.archunit.base.DescribedPredicate;
import com.tngtech.archunit.core.domain.JavaClass;
import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.lang.ArchRule;
import org.junit.jupiter.api.Test;

import static com.tngtech.archunit.base.DescribedPredicate.not;
import static com.tngtech.archunit.core.domain.JavaClass.Predicates.resideInAPackage;
import static com.tngtech.archunit.core.domain.JavaClass.Predicates.resideInAnyPackage;
import static com.tngtech.archunit.core.domain.JavaClass.Predicates.simpleNameEndingWith;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;

class LayerPurityRulesTest {

    private final JavaClasses classes = new ClassFileImporter()
            .withImportOption(ImportOption.Predefined.DO_NOT_INCLUDE_TESTS)
            .importPackages(ArchitecturePackages.ROOT);

    @Test
    void domainCarriesNoFramework() {
        ArchRule rule = noClasses()
                .that().resideInAPackage(ArchitecturePackages.DOMAIN)
                .should().dependOnClassesThat(resideInAnyPackage(
                        ArchitecturePackages.SPRING,
                        ArchitecturePackages.JAKARTA,
                        ArchitecturePackages.JACKSON,
                        ArchitecturePackages.HIBERNATE));

        rule.check(classes);
    }

    @Test
    void usecaseCarriesOnlyServiceAndTransactional() {
        DescribedPredicate<JavaClass> forbiddenFramework = resideInAnyPackage(
                        ArchitecturePackages.SPRING,
                        ArchitecturePackages.JAKARTA,
                        ArchitecturePackages.JACKSON,
                        ArchitecturePackages.HIBERNATE)
                .and(not(resideInAnyPackage(
                        ArchitecturePackages.SPRING_STEREOTYPE,
                        ArchitecturePackages.SPRING_TRANSACTION)));

        ArchRule rule = noClasses()
                .that().resideInAPackage(ArchitecturePackages.USECASE)
                .should().dependOnClassesThat(forbiddenFramework);

        rule.check(classes);
    }

    @Test
    void usecaseNeverCallsUsecase() {
        DescribedPredicate<JavaClass> anotherService = resideInAPackage(ArchitecturePackages.USECASE)
                .and(simpleNameEndingWith("Service"));

        ArchRule rule = noClasses()
                .that().resideInAPackage(ArchitecturePackages.USECASE)
                .and().haveSimpleNameEndingWith("Service")
                .should().dependOnClassesThat(anotherService);

        rule.check(classes);
    }

    @Test
    void controllersNeverCallControllers() {
        DescribedPredicate<JavaClass> anotherController = resideInAPackage(ArchitecturePackages.REST)
                .and(simpleNameEndingWith("Controller"));

        ArchRule rule = noClasses()
                .that().resideInAPackage(ArchitecturePackages.REST)
                .and().haveSimpleNameEndingWith("Controller")
                .should().dependOnClassesThat(anotherController);

        rule.check(classes);
    }
}
