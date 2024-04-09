from typing import Optional
import jwt
from datetime import datetime, timedelta
from sql_app import crud


def authenticate_user(db, username, password):
    user = crud.get_user_by_username(db, username)
    if not user:
        return False
    if not password == user.password:
        return False
    return user


def create_access_token(
    data: dict,
    SECRET_KEY: str,
    ALGORITHM: str,
    expires_delta: Optional[timedelta] = None,
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
