plugins {
    java
}

group = "com.uwords"
version = "0.1.0"

repositories {
    mavenCentral()
}

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(21))
    }
}

dependencies {
    testImplementation("org.seleniumhq.selenium:selenium-java:4.27.0")
    testImplementation("org.junit.jupiter:junit-jupiter:5.11.3")
    testImplementation("org.assertj:assertj-core:3.26.3")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher:1.11.3")
}

tasks.withType<JavaCompile>().configureEach {
    options.encoding = "UTF-8"
}

tasks.test {
    useJUnitPlatform()
    environment("APP_URL", System.getenv("APP_URL") ?: "")
    environment("E2E_HEADLESS", System.getenv("E2E_HEADLESS") ?: "true")
    environment("E2E_API_STUB_PORT", System.getenv("E2E_API_STUB_PORT") ?: "")
    testLogging {
        events("passed", "failed", "skipped")
        exceptionFormat = org.gradle.api.tasks.testing.logging.TestExceptionFormat.FULL
    }
}
