
import bcrypt


def token_hasher(token: str) -> bytes:
    return bcrypt.hashpw(token.encode("utf-8"), bcrypt.gensalt())