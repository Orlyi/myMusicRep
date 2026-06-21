from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field

class UserRegisterResponse(BaseModel):
    user_id: int

class UserRegisterRequest(BaseModel):
    user_name: str = Field(min_length=1, max_length=20)
    password: str = Field(min_length=6, max_length=32)
    email: EmailStr | None = None


class UserLoginRequest(BaseModel):
    user_name: str
    password: str

class UserLoginResponse(BaseModel):
    token: str
    user_id: int
    user_name:str
    roles:str


class UserBase(BaseModel):
    user_id: int
    user_name: str
    email: str | None = None
    roles: str
    create_time: datetime

    model_config = {"from_attributes": True}

class UserDetailsRequest(BaseModel):
    email: str | None = None
    roles: str | None = None
    nick_name: str | None = None
    gender: str | None = None
    birthdate: date | None = None
    city: str | None = None

class UserDetailResponse(BaseModel):
    nick_name: str | None = None
    gender: str | None = None
    birthdate: date | None = None
    city: str | None = None
    fans_count: int
    followed_count: int

    model_config = {"from_attributes": True}






