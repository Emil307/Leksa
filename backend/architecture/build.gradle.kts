dependencies {
    testImplementation(project(":backend:domain"))
    testImplementation(project(":backend:usecase"))
    testImplementation(project(":backend:adapters:rest"))
    testImplementation(project(":backend:adapters:storage"))
    testImplementation(project(":backend:adapters:cache"))
    testImplementation(project(":backend:adapters:email"))
    testImplementation(project(":backend:application"))
    testImplementation("com.tngtech.archunit:archunit-junit5:1.3.0")
}
