from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.schemas.user import UserCreate

from app.db import get_db
from app.models.user import User
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
)

router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=True)


# -------------------------------
# Registrierung eines neuen Users
# -------------------------------
@router.post("/register", status_code=201)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Benutzername ist bereits vergeben",
        )

    hashed_pw = hash_password(user_data.password) # Nutze user_data.password
    new_user = User(username=user_data.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": f"Benutzer '{new_user.username}' wurde erfolgreich registriert."}


# -------------------------------
# 🔹 Login & Token-Erstellung
# -------------------------------
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falscher Benutzername oder Passwort",
        )

    access_token = create_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}
# -------------------------------
# 🔹 Dependency: aktuellen User aus Token laden
# -------------------------------
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token enthält keinen Benutzernamen")
    except JWTError:
        raise HTTPException(status_code=401, detail="Ungültiger oder abgelaufener Token")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    return user


# -------------------------------
# 🔹 Endpoint: "Ich selbst" (nur mit Token)
# -------------------------------
@router.get("/me")
def read_current_user(user: User = Depends(get_current_user)):
    return {"id": user.id, "username": user.username}
