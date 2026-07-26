from datetime import datetime
from pydantic import BaseModel, Field

class MessageSendRequest(BaseModel):
    receiver_id: int
    content: str = Field(min_length=1, max_length=500)

class MessageResponse(BaseModel):
    message_id: int
    sender_id: int
    sender_name: str
    receiver_id: int
    receiver_name: str
    content: str
    is_read: bool
    sent_time: datetime

    model_config = {"from_attributes": True}