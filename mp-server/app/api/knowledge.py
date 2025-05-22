from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/knowledge", tags=["Knowledge"])

# 仅供测试使用，知识库名称列表
kb_names = ["理论研究教材知识库", "军事理论学术论文", "认知心理学研究论文库", "指挥学论文库", "学术期刊论文集"]


@router.get("/list")
async def get_knowledge_base_names():
    """
    获取所有知识库名称的API端点
    返回格式示例：
    {"message": ["知识库1", "知识库2"]}
    """
    return {"message": kb_names}


@router.get("")
async def get_knowledge_bases():
    """
    获取所有知识库的API端点
    """
    # 这里简化实现，实际应返回更详细的知识库信息
    knowledge_bases = [{"id": i, "name": name, "description": f"{name}的描述"} for i, name in enumerate(kb_names)]
    return {"data": knowledge_bases}


@router.get("/{knowledge_id}")
async def get_knowledge_base(knowledge_id: int):
    """
    获取特定知识库详情的API端点
    """
    if knowledge_id < 0 or knowledge_id >= len(kb_names):
        raise HTTPException(status_code=404, detail="知识库不存在")

    return {
        "data": {
            "id": knowledge_id,
            "name": kb_names[knowledge_id],
            "description": f"{kb_names[knowledge_id]}的详细描述",
            "document_count": 100,
            "created_at": "2025-01-01T00:00:00Z"
        }
    }
