from pydantic import BaseModel
from datetime import datetime


class UserSearch(BaseModel):
    username: str


class UserRefreshTokenUpdate(UserSearch):
    refresh_token: str
    refresh_token_expires: datetime
