from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from app.schemas.chat import ChatMessageCreate, ChatMessageResponse
from app.models.mock_model import MockModel

router = APIRouter()
model_service = MockModel()


@router.get("/test")
def test_endpoint():
    return {"status": "new API works"}

@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
        message: ChatMessageCreate
):
    """
    发送消息并获取AI回复
    """
    # 调用模型服务获取回复
    response = await model_service.predict(message.content)

    return {"response": response}
