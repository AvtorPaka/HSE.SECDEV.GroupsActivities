import secrets
import uuid


class KeyGenerator:
    @staticmethod
    def generate_session_id(length: int = 24) -> str:
        return secrets.token_urlsafe(length)

    @staticmethod
    def generate_composite_key() -> str:
        random_part = KeyGenerator.generate_session_id()
        guid_part = uuid.uuid4().hex

        return f"{guid_part}{random_part}"
