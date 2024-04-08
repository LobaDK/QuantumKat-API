import APIFunctions
import APIAuth
import uvicorn
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from datetime import timedelta
from dotenv import load_dotenv
from os import environ

load_dotenv()

SECRET_KEY = environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = APIAuth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = APIAuth.create_access_token(
        data={"sub": form_data.username},
        SECRET_KEY=SECRET_KEY,
        ALGORITHM=ALGORITHM,
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


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
