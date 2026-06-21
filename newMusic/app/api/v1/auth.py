from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Users
from app.schemas.common import APIResponse
from app.schemas.user import UserRegisterRequest, UserLoginRequest, UserLoginResponse, UserRegisterResponse, UserBase
from app.utils.security import hash_password, verify_password, create_access_token

router = APIRouter()

@router.post("/login", response_model=APIResponse)
async def login(body: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Users).where(Users.user_name == body.user_name)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token(user.user_id)
    return APIResponse(
        data=UserLoginResponse(
            token=token,
            user_id=user.user_id,
            user_name=user.user_name,
            roles=user.roles
        ).model_dump()
    )

@router.post("/register", response_model=APIResponse)
async def register(body: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Users).where(Users.user_name == body.user_name)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User already exists")

    user = Users(
        user_name=body.user_name,
        password=hash_password(body.password),
        email=body.email
    )
    db.add(user)
    await db.flush()
    return APIResponse(
        data=UserRegisterResponse(user_id=user.user_id).model_dump()
    )

@router.get("/me" , response_model=APIResponse)
async def get_me(current_user:Users = Depends(get_current_user)):
    return APIResponse(data=UserBase.model_validate(current_user))