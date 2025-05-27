import json
import logging
from pathlib import Path
from typing import List, Dict
import httpx
import requests
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Optional

# # 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置常量（建议使用环境变量）
KB_SERVICE_URL = "http://192.168.200.214:5480/v1/kb/list"
TIMEOUT = 30  # 秒


async def fetch_knowledge_bases() -> List[Dict]:
    """
    获取知识库列表的异步方法[1,5](@ref)
    使用httpx替代requests实现异步请求
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(KB_SERVICE_URL)
            response.raise_for_status()
            result = response.json()

            if result.get("retcode") != 0:
                logger.error(f"知识库服务返回错误：{result.get('retmsg')}")
                raise HTTPException(
                    status_code=502,
                    detail=f"Upstream service error: {result.get('retmsg')}"
                )

            return [
                {"id": kb["id"], "name": kb["name"]}
                for kb in result.get("data", [])
                if kb.get("id") and kb.get("name")
            ]
    except httpx.RequestError as e:
        logger.error(f"请求知识库服务失败：{str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Knowledge base service unavailable"
        )
    except Exception as e:
        logger.error(f"未预期的错误：{str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

# async def fetch_knowledge_bases(file_path: str = "knowledge_fixed_base.json") -> List[Dict]:
#     try:
#         # 验证文件存在性
#         if not Path(file_path).exists():
#             raise FileNotFoundError(f"知识库文件 {file_path} 不存在")
#
#         with open(file_path, 'r', encoding='utf-8') as f:
#             json_data = json.load(f)
#
#             # 增强型数据校验
#             data = json_data.get('data', [])
#             if not isinstance(data, list):  # 关键修正点
#                 logger.error("JSON格式错误：data字段应为列表类型")
#                 raise ValueError("知识库数据格式异常")
#
#             return [
#                 {"id": kb["id"], "name": kb["name"]}
#                 for kb in data
#                 if kb.get("id") and kb.get("name")
#             ]
#
#     except FileNotFoundError as e:
#         logger.error(f"文件读取失败：{str(e)}")
#         return []
#     except json.JSONDecodeError:
#         logger.error("JSON文件解析失败，请检查文件内容格式")
#         return []
#     except Exception as e:
#         logger.error(f"未预期的错误：{str(e)}")
#         return []
