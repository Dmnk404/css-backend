import hashlib
import os
import secrets
from datetime import UTC, datetime, timedelta

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

load_dotenv()

# --- Security configuration ---
bearer_scheme = HTTPBearer(auto_error=True)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is missing in .env")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))


# --- Password hashing ---
def get_password_hash(password: str) -> str:
    """Hashes a user's password using a strong one-way algorithm (PBKDF2)."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against its stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


# --- JWT token creation ---
def create_access_token(username: str) -> str:
    """Generates a signed JWT access token for authentication."""
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# --- JWT token validation ---
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    """Extracts and validates the current user from the provided JWT token."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token does not contain a username",
            )
        return {"username": username}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


# --- Password reset token utilities ---
def generate_reset_token() -> str:
    """Generates a secure, random reset token (sent via email)."""
    return secrets.token_urlsafe(32)


def hash_reset_token(token: str) -> str:
    """Creates a deterministic SHA256 hash of the token for safe database storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_reset_token(plain_token: str, hashed_token: str) -> bool:
    """Checks if a plain-text token matches its SHA256 hash."""
    return hashlib.sha256(plain_token.encode()).hexdigest() == hashed_token
