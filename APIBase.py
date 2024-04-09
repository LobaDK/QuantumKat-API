import APIFunctions
import APIAuth
import uvicorn
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from dotenv import load_dotenv
from os import environ

from sql_app import models, crud, schemas
from sql_app.database import SessionLocal, engine

load_dotenv()

SECRET_KEY = environ.get("SECRET_KEY")
if SECRET_KEY is None or SECRET_KEY == "":
    raise ValueError("SECRET_KEY not set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

models.Base.metadata.create_all(bind=engine)

app = FastAPI(root_path="/api")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = APIAuth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = APIAuth.create_access_token(
        data={"sub": form_data.username},
        SECRET_KEY=SECRET_KEY,
        ALGORITHM=ALGORITHM,
        expires_delta=access_token_expires,
    )
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = APIAuth.create_refresh_token(
        data={"sub": form_data.username},
        SECRET_KEY=SECRET_KEY,
        ALGORITHM=ALGORITHM,
        expires_delta=refresh_token_expires,
    )
    crud.update_user_refresh_token(
        db,
        schemas.UserRefreshTokenUpdate(
            username=form_data.username,
            refresh_token=refresh_token,
            refresh_token_expires=datetime.utcnow() + refresh_token_expires,
        ),
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@app.post("/token/refresh")
async def refresh_token(
    refresh_token: APIAuth.RefreshToken = Depends(),
    db: Session = Depends(get_db),
):
    user = APIAuth.verify_refresh_token(
        db, refresh_token.username, refresh_token.refresh_token
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    if not APIAuth.verify_refresh_token_expiration(
        db, refresh_token.username, refresh_token.refresh_token
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = APIAuth.create_access_token(
        data={"sub": refresh_token.username},
        SECRET_KEY=SECRET_KEY,
        ALGORITHM=ALGORITHM,
        expires_delta=access_token_expires,
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@app.post("/logout")
async def logout(
    refresh_token: APIAuth.RefreshToken = Depends(),
    db: Session = Depends(get_db),
):
    user = APIAuth.verify_refresh_token(
        db, refresh_token.username, refresh_token.refresh_token
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    if not APIAuth.verify_refresh_token_expiration(
        db, refresh_token.username, refresh_token.refresh_token
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    crud.update_user_refresh_token(
        db,
        schemas.UserRefreshTokenUpdate(
            username=refresh_token.username,
            refresh_token="",
            refresh_token_expires=datetime.utcnow(),
        ),
    )
    return {"message": "Logout successful"}


@app.get("/logs/")
async def get_logs(
    token: Annotated[str, Depends(oauth2_scheme)],
    query: APIFunctions.LogQuery = Depends(),
    log_order: APIFunctions.LogOrder = APIFunctions.LogOrder.desc,
    log_level: APIFunctions.LogLevels = APIFunctions.LogLevels.INFO,
):
    if query.log_file is None or query.log_file == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="log_file is required.",
        )
    if query.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="amount must be greater than 0.",
        )
    try:
        return APIFunctions.get_logs(
            query.log_file, log_order, query.amount, log_level, query.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def start_api():
    await uvicorn.run(app, host="127.0.0.1", port=8888)


start_api()
