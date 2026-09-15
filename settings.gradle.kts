rootProject.name = "uwords"

include(
    ":backend:domain",
    ":backend:usecase",
    ":backend:adapters:rest",
    ":backend:adapters:storage",
    ":backend:adapters:cache",
    ":backend:adapters:email",
    ":backend:application",
    ":backend:architecture",
)
