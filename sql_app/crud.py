from sqlalchemy.orm import Session
from . import models, schemas


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def update_user_refresh_token(db: Session, user: schemas.UserRefreshTokenUpdate):
    db_user = (
        db.query(models.User).filter(models.User.username == user.username).first()
    )
    db_user.refresh_token = user.refresh_token
    db_user.refresh_token_expires = user.refresh_token_expires
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_refresh_token(db: Session, username: str, refresh_token: str):
    return (
        db.query(models.User)
        .filter(
            models.User.username == username, models.User.refresh_token == refresh_token
        )
        .first()
    )
