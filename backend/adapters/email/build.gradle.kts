dependencies {
    api(project(":backend:usecase"))
    implementation("org.springframework.boot:spring-boot-starter-mail")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("com.icegreen:greenmail-junit5:2.1.0")
}
