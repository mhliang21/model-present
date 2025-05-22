from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

# 导入API路由模块
from app.api import chat, knowledge

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="智能问答系统API",
    description="基于FastAPI的智能问答系统后端（简化版）",
    version="1.0.0"
)

# 配置CORS,允许前端域名访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(chat.router)
app.include_router(knowledge.router)

@app.get("/")
async def root():
    return {"message": "智能问答系统API服务正在运行（支持推理模式）"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )
