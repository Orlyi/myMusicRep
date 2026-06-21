from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Users, Comments, Songs
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.comment import CommentCreateRequest, CommentResponse

router = APIRouter()


@router.post("/songs/{song_id}/comments", response_model=APIResponse)
async def create_comment(
        song_id: int,
        body: CommentCreateRequest,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    song = await db.get(Songs, song_id)
    if not song:
        return APIResponse(code=404, message="Song not found")

    root_id = 0
    if body.parent_id is not None:
        parent = await db.get(Comments, body.parent_id)
        if not parent or parent.current_status != 1:
            return APIResponse(code=404, message="Parent comment not found")
        root_id = parent.root_id if parent.root_id != 0 else parent.comment_id

    comment = Comments(
        song_id=song_id,
        user_id=current_user.user_id,
        content=body.content,
        parent_id=body.parent_id,
        root_id=root_id,
    )
    db.add(comment)
    await db.flush()
    return APIResponse(message="Comment posted",data={"comment_id":comment.comment_id})

@router.get("/songs/{song_id}/comments", response_model=APIResponse)
async def list_comments(
        song_id: int,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=10, ge=1, le=100),
        db: AsyncSession = Depends(get_db)):
    total_result = await db.execute(
        select(func.count())
        .select_from(Comments)
        .where(Comments.song_id == song_id, Comments.parent_id.is_(None), Comments.current_status == 1)
    )
    total = total_result.scalar()

    result = await db.execute(
        select(Comments, Users.user_name)
        .outerjoin(Users, Comments.user_id == Users.user_id)
        .where(Comments.song_id == song_id, Comments.parent_id.is_(None), Comments.current_status == 1)
        .order_by(Comments.is_top.desc(), Comments.create_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size))
    rows = result.all()

    items = []
    for comment , user_name in rows:
        items.append(
            CommentResponse(
                comment_id=comment.comment_id,
                song_id=comment.song_id,
                user_id=comment.user_id,
                user_name=user_name or "",
                content=comment.content,
                parent_id=comment.parent_id,
                root_id=comment.root_id,
                like_count=comment.like_count,
                reply_count=comment.reply_count,
                is_top=comment.is_top,
                create_time=comment.create_time,
                ).model_dump()
            )
    return APIResponse(
        data=PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )
    )

@router.delete("/comments/{comment_id}", response_model=APIResponse)
async def delete_comment(
        comment_id: int,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    comment = await db.get(Comments, comment_id)
    if not comment:
        return APIResponse(code=404, message="Comment not found")
    if comment.user_id != current_user.user_id:
        return APIResponse(code=403, message="Not your comment")

    await db.delete(comment)
    await db.flush()
    return APIResponse(message="Comment deleted")
