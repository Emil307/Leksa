plugins {
    id("org.springframework.boot")
}

dependencies {
    api(project(":backend:adapters:rest"))
    api(project(":backend:adapters:storage"))
    api(project(":backend:adapters:cache"))
    api(project(":backend:adapters:email"))
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-validation")
    implementation("com.auth0:java-jwt:4.4.0")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.testcontainers:junit-jupiter")
    testImplementation("org.testcontainers:postgresql")
}

springBoot {
    mainClass.set("com.uwords.application.UwordsApplication")
}

tasks.named<Jar>("jar") {
    enabled = true
    archiveClassifier.set("plain")
}
