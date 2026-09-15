val liquibaseRuntime: Configuration by configurations.creating

dependencies {
    liquibaseRuntime("info.picocli:picocli:4.7.6")
    api(project(":backend:usecase"))
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.liquibase:liquibase-core")
    runtimeOnly("org.postgresql:postgresql")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.testcontainers:junit-jupiter")
    testImplementation("org.testcontainers:postgresql")
}

tasks.register<JavaExec>("liquibaseUpdate") {
    group = "database"
    description = "Applies db/changelog/db.changelog-master.xml to the configured database"
    classpath = sourceSets["main"].runtimeClasspath + liquibaseRuntime
    mainClass.set("liquibase.integration.commandline.LiquibaseCommandLine")
    args(
        "--changelog-file=db/changelog/db.changelog-master.xml",
        "--url=${providers.environmentVariable("LIQUIBASE_URL").getOrElse("")}",
        "--username=${providers.environmentVariable("LIQUIBASE_USERNAME").getOrElse("")}",
        "--password=${providers.environmentVariable("LIQUIBASE_PASSWORD").getOrElse("")}",
        "update",
    )
}
