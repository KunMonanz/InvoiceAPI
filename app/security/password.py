from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()


def hash_password(plain_password: str):
    return ph.hash(plain_password)

def verify_password(hashed_password: str, plain_password: str):
    return ph.verify(hashed_password, plain_password)

def dummy_hash_and_verify(plain_password: str):
    DUMMY_PASSWORD = "This_is_dummy_hash_to_fool_attackers"
    DUMMY_HASH = ph.hash(DUMMY_PASSWORD)
    ph.verify(plain_password, DUMMY_HASH)
    
    