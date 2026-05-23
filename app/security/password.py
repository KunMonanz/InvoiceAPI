from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

def hash_password(plain_password: str):
    return ph.hash(plain_password)

def verify_password(hashed_password: str, plain_password: str):
    return ph.verify(hashed_password, plain_password)