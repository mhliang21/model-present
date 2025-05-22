from fastapi import APIRouter

# 创建路由器
router = APIRouter(tags=["API"])

# 导入子路由
from app.api.chat import router as chat_router
from app.api.knowledge import router as knowledge_router

# 注册子路由
router.include_router(chat_router)
router.include_router(knowledge_router)
