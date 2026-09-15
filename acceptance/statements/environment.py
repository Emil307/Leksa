import os


def required_setting(variable: str) -> str:
    raw = os.environ.get(variable)
    assert raw, f"{variable} must be exported by infrastructure/.env — the test reads it, it never hardcodes it"
    return raw
