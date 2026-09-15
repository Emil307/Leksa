import uuid


class TestData:
    EMAIL_DOMAIN = "uwords-acceptance.local"

    @classmethod
    def unique_email(cls, prefix: str = "learner") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:12]}@{cls.EMAIL_DOMAIN}"

    @classmethod
    def unique_name(cls, prefix: str = "name") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:12]}"
