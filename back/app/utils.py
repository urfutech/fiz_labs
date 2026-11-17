from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(pswd: str):
    return pwd_context.hash(pswd)


def verify(pswd: str, hash: str):
    return pwd_context.verify(pswd, hash)
