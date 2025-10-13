import hashlib, argon2, secrets

def sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

def hash_password(password: str) -> str:
    return argon2.PasswordHasher().hash(password)
    
def verify_password(password: str, password_hash: str) -> bool:
    ph = argon2.PasswordHasher()

    try:
        return ph.verify(password_hash, password)

    except argon2.exceptions.VerifyMismatchError:
        return False
    
def generate_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)