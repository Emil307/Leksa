dependencies {
    api(project(":backend:domain"))
    implementation("org.springframework:spring-context")
    implementation("org.springframework:spring-tx")
    testImplementation("org.junit.jupiter:junit-jupiter-params")
}
