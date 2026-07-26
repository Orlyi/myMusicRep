from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Users, Messages
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.message import MessageSendRequest, MessageResponse
from app.core.cache import cached, cache_delete

router = APIRouter()


@router.post("", response_model=APIResponse)
async def send_message(
        body: MessageSendRequest,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    if body.receiver_id == current_user.user_id:
        return APIResponse(code=400, message="不能给自己发消息")

    receiver = await db.get(Users, body.receiver_id)
    if not receiver:
        return APIResponse(code=404, message="用户不存在")

    msg = Messages(
        sender_id=current_user.user_id,
        receiver_id=body.receiver_id,
        content=body.content,
    )
    db.add(msg)
    await db.flush()
    await cache_delete("msg:*")
    return APIResponse(message="发送成功", data={"message_id": msg.message_id})


@router.get("/received", response_model=APIResponse)
@cached("msg:received", ttl=120)
async def received_messages(
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    """收到的私信"""
    where = and_(
        Messages.receiver_id == current_user.user_id,
        Messages.is_deleted_receiver == False,
    )
    count_query = select(func.count()).select_from(Messages).where(where)
    total = (await db.execute(count_query)).scalar() or 0

    result = await db.execute(
        select(Messages, Users.user_name)
        .outerjoin(Users, Messages.sender_id == Users.user_id)
        .where(where)
        .order_by(Messages.sent_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = result.all()

    return APIResponse(
        data=PaginatedResponse(
            items=[{
                "message_id": msg.message_id,
                "sender_id": msg.sender_id,
                "sender_name": sender_name or "已注销",
                "content": msg.content,
                "is_read": msg.is_read,
                "sent_time": msg.sent_time.isoformat(),
            } for msg, sender_name in rows],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.get("/list", response_model=APIResponse)
@cached("msg:sent", ttl=120)
async def list_messages(
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    """我发送的私信"""
    where = and_(
        Messages.sender_id == current_user.user_id,
        Messages.is_deleted_sender == False,
    )
    count_query = select(func.count()).select_from(Messages).where(where)
    total = (await db.execute(count_query)).scalar() or 0

    result = await db.execute(
        select(Messages, Users.user_name)
        .outerjoin(Users, Messages.receiver_id == Users.user_id)
        .where(where)
        .order_by(Messages.sent_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = result.all()

    return APIResponse(data=PaginatedResponse(
        items=[{
            "message_id": msg.message_id,
            "receiver_id": msg.receiver_id,
            "receiver_name": receiver_name or "已注销",
            "content": msg.content,
            "is_read": msg.is_read,
            "sent_time": msg.sent_time.isoformat(),
        } for msg, receiver_name in rows],
        total=total, page=page, page_size=page_size,
    ))


@router.delete("/{message_id}", response_model=APIResponse)
async def delete_message(
        message_id: int,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    """软删除私信（发送/接收双方各自删除，不影响对方）"""
    msg = await db.get(Messages, message_id)
    if not msg:
        return APIResponse(code=404, message="消息不存在")

    if msg.sender_id == current_user.user_id:
        msg.is_deleted_sender = True
    elif msg.receiver_id == current_user.user_id:
        msg.is_deleted_receiver = True
    else:
        return APIResponse(code=403, message="无权操作")

    await db.flush()
    await cache_delete("msg:*")
    return APIResponse(message="已删除")
