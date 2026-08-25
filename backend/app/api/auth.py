import base64
import hashlib
import hmac
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest


router = APIRouter(prefix="/auth", tags=["auth"])
HASH_NAME = "sha256"
HASH_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        HASH_NAME, password.encode("utf-8"), salt, HASH_ITERATIONS
    )
    encoded_salt = base64.urlsafe_b64encode(salt).decode("ascii")
    encoded_hash = base64.urlsafe_b64encode(password_hash).decode("ascii")
    return f"pbkdf2_{HASH_NAME}${HASH_ITERATIONS}${encoded_salt}${encoded_hash}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, encoded_salt, encoded_hash = stored_hash.split("$")
        if algorithm != f"pbkdf2_{HASH_NAME}":
            return False
        salt = base64.urlsafe_b64decode(encoded_salt.encode("ascii"))
        expected_hash = base64.urlsafe_b64decode(encoded_hash.encode("ascii"))
        actual_hash = hashlib.pbkdf2_hmac(
            HASH_NAME, password.encode("utf-8"), salt, int(iterations)
        )
    except (TypeError, ValueError, UnicodeError):
        return False
    return hmac.compare_digest(actual_hash, expected_hash)


def create_stub_token(user: User) -> str:
    return f"dev-token-{user.id}"


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    existing_user = db.scalar(select(User).where(User.email == payload.email))
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже зарегистрирован",
        )

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return AuthResponse(user=user, access_token=create_stub_token(user))


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return AuthResponse(user=user, access_token=create_stub_token(user))