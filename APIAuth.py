from typing import Optional
import jwt
from datetime import datetime, timedelta


def authenticate_user(username, password):
    with open(".user", "r") as file:
        lines = file.readlines()
    for line in lines:
        if "username" in line:
            _username = line.split("=")[1].strip().strip('"')
        elif "password" in line:
            _password = line.split("=")[1].strip().strip('"')
    if _username and _password:
        if username == _username and password == _password:
            return True
    return None


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
