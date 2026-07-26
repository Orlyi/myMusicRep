import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Users, UserDetails
from app.schemas.common import APIResponse
from app.schemas.user import UserRegisterRequest, UserLoginRequest, UserLoginResponse, UserRegisterResponse, UserBase
from app.utils.security import hash_password, verify_password, create_access_token
from pydantic import BaseModel, Field

router = APIRouter()

UPLOAD_DIR = "uploads/avatars"


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=6, max_length=32)
    new_password: str = Field(min_length=6, max_length=32)


@router.post("/change-password", response_model=APIResponse)
async def change_password(
        body: ChangePasswordRequest,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    if not verify_password(body.old_password, current_user.password):
        return APIResponse(code=400, message="原密码错误")
    current_user.password = hash_password(body.new_password)
    await db.flush()
    return APIResponse(message="密码修改成功")
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
            avatar_url=user.avatar_url,
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
        email=body.email,
        avatar_url=body.avatar_url
    )
    db.add(user)
    await db.flush()

    # 同步创建空 details 记录
    db.add(UserDetails(user_id=user.user_id))
    await db.flush()
    return APIResponse(
        data=UserRegisterResponse(user_id=user.user_id, avatar_url=user.avatar_url).model_dump()
    )

@router.post("/upload-avatar", response_model=APIResponse)
async def upload_avatar(file: UploadFile = File(...)):
    # 校验文件类型
    if file.content_type not in ("image/jpeg", "image/png", "image/gif", "image/webp"):
        raise HTTPException(status_code=400, detail="仅支持 JPEG/PNG/GIF/WEBP 格式")

    # 生成唯一文件名
    ext = file.filename.rsplit(".", 1)[-1] if "." in (file.filename or "") else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # 保存文件
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    # 返回可访问的 URL
    avatar_url = f"/static/avatars/{filename}"
    return APIResponse(data={"avatar_url": avatar_url})

@router.get("/me" , response_model=APIResponse)
async def get_me(current_user:Users = Depends(get_current_user)):
    return APIResponse(data=UserBase.model_validate(current_user))