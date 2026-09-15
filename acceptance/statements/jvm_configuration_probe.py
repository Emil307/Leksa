import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

PROBE_MAIN_CLASS = "com.uwords.application.ConfigurationProbe"
PROPERTIES_LAUNCHER = "org.springframework.boot.loader.launch.PropertiesLauncher"
APPLICATION_LIBRARY_DIRECTORY = "backend/application/build/libs"
JAR_PATTERN = "*.jar"
PLAIN_JAR_SUFFIX = "-plain.jar"
INHERITED_VARIABLES = ("PATH", "HOME", "JAVA_HOME")
PROBE_TIMEOUT_SECONDS = 90
JAVA_EXECUTABLE = "java"
JAVA_HOME_VARIABLE = "JAVA_HOME"
JAR_ABSENT = "boot-jar не собран: выполните ./gradlew :backend:application:bootJar"


@dataclass(frozen=True)
class ProbeResult:
    exit_code: int
    diagnostics: str


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def application_jar() -> Path:
    library_directory = repository_root() / APPLICATION_LIBRARY_DIRECTORY
    jars = [jar for jar in sorted(library_directory.glob(JAR_PATTERN)) if not jar.name.endswith(PLAIN_JAR_SUFFIX)]
    assert jars, JAR_ABSENT
    return jars[0]


def java_executable() -> str:
    java_home = os.environ.get(JAVA_HOME_VARIABLE)
    if java_home:
        candidate = Path(java_home) / "bin" / JAVA_EXECUTABLE
        if candidate.exists():
            return str(candidate)
    return JAVA_EXECUTABLE


def run_configuration_probe(configuration: dict[str, str], working_directory: Path) -> ProbeResult:
    completed = subprocess.run(
        [
            java_executable(),
            f"-Dloader.main={PROBE_MAIN_CLASS}",
            "-cp",
            str(application_jar()),
            PROPERTIES_LAUNCHER,
        ],
        cwd=working_directory,
        env=_probe_environment(configuration),
        capture_output=True,
        text=True,
        timeout=PROBE_TIMEOUT_SECONDS,
        check=False,
    )
    return ProbeResult(exit_code=completed.returncode, diagnostics=completed.stderr + completed.stdout)


def _probe_environment(configuration: dict[str, str]) -> dict[str, str]:
    inherited = {name: os.environ[name] for name in INHERITED_VARIABLES if name in os.environ}
    return inherited | configuration
