from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Users, Messages
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.message import MessageSendRequest, MessageResponse

router = APIRouter()

@router.post("", response_model=APIResponse)
async def send_message(
        body: MessageSendRequest,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    if body.receiver_id == current_user.user_id:
        return APIResponse(code=400, message="You can't send messages to yourself!")

    receiver = await db.get(Users, body.receiver_id)
    if not receiver:
        return APIResponse(code=404, message="User not found!")

    msg = Messages(
        sender_id=current_user.user_id,
        receiver_id=body.receiver_id,
        content=body.content,
    )
    db.add(msg)
    await db.flush()
    return APIResponse(
        message="Message sent successfully!",
        data={"message_id": msg.message_id}
    )

@router.get("/received", response_model=APIResponse)
async def received_messages(
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    count_query = select(func.count()).select_from(Messages).where(Messages.receiver_id == current_user.user_id, Messages.is_deleted_receiver == False)
    total = (await db.execute(count_query)).scalar() or 0
    result = await db.execute(
        select(Messages, Users.user_name)
        .outerjoin(Users, Messages.sender_id == Users.user_id)
        .where(Messages.receiver_id == current_user.user_id, Messages.is_deleted_receiver == False)
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
                "sender_name": sender_name or "",
                "content": msg.content,
                "is_read":msg.is_read,
                "sent_time": msg.sent_time.isoformat(),
            }for msg, sender_name in rows],
            total=total,
            page=page,
            page_size=page_size
        )
    )


@router.get("/list", response_model=APIResponse)
async def list_messages(
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    count_query = select(func.count()).select_from(Messages).where(
        (Messages.sender_id == current_user.user_id) & (Messages.is_deleted_sender == False)
        | (Messages.receiver_id == current_user.user_id) & (Messages.is_deleted_receiver == False),
    )
    total = (await db.execute(count_query)).scalar() or 0

    result = await db.execute(
        select(Messages, Users.user_name)
        .outerjoin(Users, Messages.sender_id == Users.user_id)
        .where(
            (Messages.sender_id == current_user.user_id) & (Messages.is_deleted_sender == False)
            | (Messages.receiver_id == current_user.user_id) & (Messages.is_deleted_receiver == False),
        )
        .order_by(Messages.sent_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = result.all()

    return APIResponse(data=PaginatedResponse(
        items=[{
            "message_id": msg.message_id,
            "sender_id": msg.sender_id,
            "sender_name": sender_name or "",
            "content": msg.content,
            "is_read": msg.is_read,
            "sent_time": msg.sent_time.isoformat(),
        } for msg, sender_name in rows],
        total=total, page=page, page_size=page_size,
    ))


@router.delete("/{message_id}", response_model=APIResponse)
async def delete_message_soft(
        message_id: int,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    msg = await db.get(Messages, message_id)
    if not msg:
        return APIResponse(code=404, message="Message not found")

    if msg.sender_id == current_user.user_id:
        msg.is_deleted_sender = True
    elif msg.receiver_id == current_user.user_id:
        msg.is_deleted_receiver = True
    else:
        return APIResponse(code=403, message="Not your message")

    await db.flush()
    return APIResponse(message="Deleted for yourself successfully")

@router.delete("/{message_id}", response_model=APIResponse)
async def delete_message_hard(
      message_id: int,
      current_user: Users = Depends(get_current_user),
      db: AsyncSession = Depends(get_db)):
  msg = await db.get(Messages, message_id)
  if not msg:
      return APIResponse(code=404, message="Message not found")

  if msg.sender_id != current_user.user_id:
      return APIResponse(code=403, message="Not your message")

  if (datetime.now() - msg.sent_time).total_seconds() > 300:
      return APIResponse(code=400, message="You can't delete this message")

  await db.delete(msg)
  await db.flush()
  return APIResponse(message="Deleted completely successfully")