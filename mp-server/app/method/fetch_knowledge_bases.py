import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict
import httpx
import requests
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Optional


# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 模拟知识库数据
MOCK_KNOWLEDGE_BASES = [
    {"id": "kb001", "name": "指挥控制系统知识库"},
    {"id": "kb002", "name": "军事装备知识库"},
    {"id": "kb003", "name": "战术训练知识库"},
    {"id": "kb004", "name": "情报分析知识库"},
    {"id": "kb005", "name": "通信网络知识库"}
]

async def fetch_knowledge_bases() -> List[Dict]:
    """
    获取知识库列表的异步方法 - 使用模拟数据
    """
    try:
        logger.info("使用模拟数据获取知识库列表")
        # 模拟网络延迟
        await asyncio.sleep(0.5)
        return MOCK_KNOWLEDGE_BASES
    except Exception as e:
        logger.error(f"获取知识库列表失败: {str(e)}")
        # 即使出错也返回部分模拟数据，确保接口可用
        return MOCK_KNOWLEDGE_BASES[:2]


# # 配置常量（建议使用环境变量）
#
# KB_SERVICE_URL = "http://192.168.200.214:5480/v1/kb/list"
# TIMEOUT = 30  # 秒
#
# async def fetch_knowledge_bases() -> List[Dict]:
#     """
#     获取知识库列表的异步方法[1,5](@ref)
#     使用httpx替代requests实现异步请求
#     """
#     try:
#         async with httpx.AsyncClient(timeout=TIMEOUT) as client:
#             response = await client.get(KB_SERVICE_URL)
#             response.raise_for_status()
#             result = response.json()
#
#             if result.get("retcode") != 0:
#                 logger.error(f"知识库服务返回错误：{result.get('retmsg')}")
#                 raise HTTPException(
#                     status_code=502,
#                     detail=f"Upstream service error: {result.get('retmsg')}"
#                 )
#
#             return [
#                 {"id": kb["id"], "name": kb["name"]}
#                 for kb in result.get("data", [])
#                 if kb.get("id") and kb.get("name")
#             ]
#     except httpx.RequestError as e:
#         logger.error(f"请求知识库服务失败：{str(e)}")
#         raise HTTPException(
#             status_code=503,
#             detail="Knowledge base service unavailable"
#         )
#     except Exception as e:
#         logger.error(f"未预期的错误：{str(e)}")
#         raise HTTPException(
#             status_code=500,
#             detail="Internal server error"
#         )
