from pydantic import BaseModel


class UserSearch(BaseModel):
    username: str


class UserRefreshTokenUpdate(UserSearch):
    refresh_token: str
    refresh_token_expires: str
