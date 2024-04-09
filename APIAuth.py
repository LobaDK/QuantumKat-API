from typing import Optional
import jwt
from datetime import datetime, timedelta
from sql_app import crud
from pydantic import BaseModel


class RefreshToken(BaseModel):
    username: str
    refresh_token: str


def authenticate_user(db, username, password):
    """
    Authenticates a user by checking if the provided username and password match the user's credentials.

    Args:
        db (Database): The database object used to query user information.
        username (str): The username of the user to authenticate.
        password (str): The password of the user to authenticate.

    Returns:
        Union[User, bool]: Returns the authenticated user object if the username and password match,
        otherwise returns False.
    """
    user = crud.get_user_by_username(db, username)
    if not user:
        return False
    if not password == user.password:
        return False
    return user


def verify_refresh_token(db, username, refresh_token):
    """
    Verify the refresh token for a given user.

    Args:
        db (Database): The database connection.
        username (str): The username of the user.
        refresh_token (str): The refresh token to verify.

    Returns:
        Union[User, bool]: The user object if the refresh token is valid, False otherwise.
    """
    user = crud.get_user_by_refresh_token(db, username, refresh_token)
    if not user:
        return False
    if not refresh_token == user.refresh_token:
        return False
    return user


def verify_refresh_token_expiration(db, username, refresh_token):
    """
    Verify the expiration of the refresh token for a given user.

    Args:
        db (Database): The database connection.
        username (str): The username of the user.
        refresh_token (str): The refresh token to verify.

    Returns:
        Union[User, bool]: The user object if the refresh token is valid and not expired, False otherwise.
    """
    user = crud.get_user_by_refresh_token(db, username, refresh_token)
    if not user:
        return False
    if not refresh_token == user.refresh_token:
        return False
    if datetime.utcnow() > user.refresh_token_expires:
        return False
    return user


def create_access_token(
    data: dict,
    SECRET_KEY: str,
    ALGORITHM: str,
    expires_delta: Optional[timedelta] = None,
):
    """
    Create an access token using the provided data, secret key, and algorithm and return the encoded JWT.

    Args:
        data (dict): The data to be encoded in the JWT.
        SECRET_KEY (str): The secret key used for encoding the JWT.
        ALGORITHM (str): The algorithm used for encoding the JWT.
        expires_delta (Optional[timedelta], optional): The expiration time delta for the JWT.
            If not provided, the token will expire after 15 minutes by default.

    Returns:
        str: The encoded JWT access token.

    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    data: dict,
    SECRET_KEY: str,
    ALGORITHM: str,
    expires_delta: Optional[timedelta] = None,
):
    """
    Create a refresh token using the provided data, secret key, and algorithm and return the encoded JWT.

    Args:
        data (dict): The data to be encoded in the JWT.
        SECRET_KEY (str): The secret key used for encoding the JWT.
        ALGORITHM (str): The algorithm used for encoding the JWT.
        expires_delta (Optional[timedelta], optional): The expiration time delta for the JWT.
            If not provided, the token will expire after 1 day by default.

    Returns:
        str: The encoded JWT refresh token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
