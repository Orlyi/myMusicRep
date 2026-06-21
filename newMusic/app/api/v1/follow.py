from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Users, Artists, UserDetails
from app.models.user_follow_artist import UserFollowArtist
from app.models.user_follow_user import UserFollowUser
from app.schemas.common import APIResponse

router = APIRouter()

@router.post("/artist/{artist_id}", response_model=APIResponse)
async def follow_artist(
        artist_id: int,
        current_user:Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    artist = await db.get(Artists, artist_id)
    if not artist:
        return APIResponse(code=404, message="Artist not found")

    existing = await db.get(UserFollowArtist, (current_user.user_id, artist_id))
    if existing:
        return APIResponse(code=400, message="Artist followed already")

    db.add(UserFollowArtist(user_id=current_user.user_id, artist_id=artist_id))
    artist.fans_count += 1
    result = await db.execute(
        select(UserDetails)
        .where(UserDetails.user_id == current_user.user_id)
    )
    details = result.scalar_one_or_none()
    if details:
        details.followed_count += 1

    await db.flush()
    return APIResponse(message="Artist followed successfully")

@router.post("/user/{followed_id}", response_model=APIResponse)
async def follow_user(
        followed_id: int,
        current_user:Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    if followed_id == current_user.user_id:
        return APIResponse(code=400, message="Cannot follow yourself")

    target = await db.get(Users, followed_id)
    if not target:
        return APIResponse(code=404, message="User not found")

    existing = await db.get(UserFollowUser, (current_user.user_id, followed_id))
    if existing:
        return APIResponse(code=400, message="Already followed user")

    db.add(UserFollowUser(fans_id=current_user.user_id, followed_id=followed_id))
    result = await db.execute(
        select(UserDetails)
        .where(UserDetails.user_id == current_user.user_id)
    )
    my_details = result.scalar_one_or_none()
    if my_details:
        my_details.followed_count += 1

    target_result = await db.execute(
        select(UserDetails)
        .where(UserDetails.user_id == followed_id)
    )
    target_details = target_result.scalar_one_or_none()
    if target_details:
        target_details.fans_count += 1

    await db.flush()
    return APIResponse(message="User followed successfully")

@router.delete("/artist/{artist_id}", response_model=APIResponse)
async def unfollow_artist(
      artist_id: int,
      current_user: Users = Depends(get_current_user),
      db: AsyncSession = Depends(get_db)):
  follow = await db.get(UserFollowArtist, (current_user.user_id, artist_id))
  if not follow:
      return APIResponse(code=404, message="Not followed")

  await db.delete(follow)
  artist = await db.get(Artists, artist_id)
  if artist and artist.fans_count > 0:
      artist.fans_count -= 1

  result = await db.execute(
      select(UserDetails).where(UserDetails.user_id == current_user.user_id)
  )
  details = result.scalar_one_or_none()
  if details and details.followed_count > 0:
      details.followed_count -= 1

  await db.flush()
  return APIResponse(message="Unfollowed artist")


@router.delete("/user/{followed_id}", response_model=APIResponse)
async def unfollow_user(
        followed_id: int,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    follow = await db.get(UserFollowUser, (current_user.user_id, followed_id))
    if not follow:
        return APIResponse(code=404, message="Not followed")

    await db.delete(follow)

    my_result = await db.execute(
        select(UserDetails).where(UserDetails.user_id == current_user.user_id)
    )
    my_detail = my_result.scalar_one_or_none()
    if my_detail and my_detail.followed_count > 0:
        my_detail.followed_count -= 1

    target_result = await db.execute(
        select(UserDetails).where(UserDetails.user_id == followed_id)
    )
    target_detail = target_result.scalar_one_or_none()
    if target_detail and target_detail.fans_count > 0:
        target_detail.fans_count -= 1

    await db.flush()
    return APIResponse(message="Unfollowed user")