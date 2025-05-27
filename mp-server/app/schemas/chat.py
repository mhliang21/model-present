from pydantic import BaseModel, Field
from typing import Optional

class ChatMessageBase(BaseModel):
    content: str = Field(..., description="聊天消息内容")

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(BaseModel):
    response: str = Field(..., description="模型生成的回复内容")