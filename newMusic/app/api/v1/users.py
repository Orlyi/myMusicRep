from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_current_user
from app.core.database import get_db
from app.models import Users, UserDetails, Songs, PlayHistory
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.user import UserBase, UserDetailResponse, UserDetailsRequest
from datetime import datetime

router = APIRouter()



@router.get("/me/info", response_model=APIResponse)
async def get_my_info(
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserDetails)
        .where(UserDetails.user_id == current_user.user_id)
    )
    details = result.scalar_one_or_none()

    # 如果没有 details 记录，自动创建
    if not details:
        details = UserDetails(user_id=current_user.user_id)
        db.add(details)
        await db.flush()

    return APIResponse(
        data={"user": UserBase.model_validate(current_user).model_dump(),
              "details": UserDetailResponse.model_validate(details).model_dump() if details else None},
    )

@router.get("/me/history", response_model=APIResponse)
async def get_my_history(
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    count_result = await db.execute(
        select(func.count())
        .select_from(PlayHistory)
        .where(PlayHistory.user_id == current_user.user_id)
    )
    total = count_result.scalar() or 0
    result = await db.execute(
        select(PlayHistory, Songs.song_name, Songs.picture_url)
        .outerjoin(Songs, PlayHistory.song_id == Songs.song_id)
        .where(PlayHistory.user_id == current_user.user_id)
        .order_by(PlayHistory.create_time.desc())
        .offset((page - 1)* page_size)
        .limit(page_size)
    )
    rows = result.all()

    items = [{
        "play_id":h.play_id,
        "song_id":h.song_id,
        "song_name":song_name or "",
        "picture_url":picture_url or "",
        "artist_id":h.artist_id,
        "playlist_id":h.playlist_id,
        "playlist_duration":h.playlist_duration,
        "is_completed":h.is_completed,
        "create_time":h.create_time.isoformat(),
    } for h, song_name, picture_url in rows]

    return APIResponse(
        data=PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )
    )

@router.get("/me/register-duration", response_model=APIResponse)
async def register_duration(
        current_user: Users = Depends(get_current_user)):
    days = (datetime.now() - current_user.create_time).days
    return APIResponse(
        data={"days": days}
    )

@router.put("/me", response_model=APIResponse)
async def write_my_info(
        body: UserDetailsRequest,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserDetails).where(UserDetails.user_id == current_user.user_id)
    )
    details = result.scalar_one_or_none()
    if not details:
        details = UserDetails(user_id=current_user.user_id)
        db.add(details)
        await db.flush()
    update_data = body.model_dump(exclude_unset=True)
    if "email" in update_data:
        current_user.email = update_data.pop("email")
    if "roles" in update_data:
        current_user.roles = update_data.pop("roles")

    for field, value in update_data.items():
        setattr(details, field, value)

    await db.flush()
    return APIResponse(
        message="User details updated successfully",
    )