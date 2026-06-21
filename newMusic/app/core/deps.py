from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import Users
from app.utils.security import decode_access_token

security = HTTPBearer()


async def get_current_user(
        credentials:HTTPAuthorizationCredentials = Depends(security),
        db:AsyncSession = Depends(get_db)
) -> Users:
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token is invalid or expired")

    result = await db.execute(select(Users).where(Users.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="User does not exist")

    return user