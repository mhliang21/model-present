from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import logging
import json
import os
import asyncio
from starlette.concurrency import iterate_in_threadpool

# 导入知识库获取方法和推理模式
from app.method import fetch_knowledge_bases
from app.models import inference_mode1, inference_mode2, inference_mode3

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


@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"→ 收到请求: {request.method} {request.url}")
    try:
        response = await call_next(request)
    finally:
        print(f"← 响应完成: {request.method} {request.url}")
    return response


# 请求模型
class InferenceRequest(BaseModel):
    mode: str
    query: str
    kb_names: List[str]


# 聊天消息模型
class ChatMessageRequest(BaseModel):
    content: str  # 修改：使用content替代message，与前端一致
    mode: str = "1"  # 默认使用模式1
    kb_names: List[str] = []  # 默认不使用知识库


# 获取知识库列表 - 修改路径以匹配前端
@app.get("/api/knowledge/list")
async def get_knowledge_base_names():
    """
    获取所有知识库名称的API端点
    返回格式示例：
    {"message": ["知识库1", "知识库2"]}
    """
    try:
        # 使用fetch_knowledge_bases方法获取知识库列表
        kb_list = await fetch_knowledge_bases.fetch_knowledge_bases()

        # 提取知识库名称
        kb_names = [kb["name"] for kb in kb_list]

        return {"message": kb_names}
    except Exception as e:
        logger.error(f"获取知识库列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取知识库列表失败: {str(e)}")


# 知识库API - 添加前端需要的接口
@app.get("/api/knowledge")
async def get_knowledge_bases():
    """
    获取所有知识库的API端点
    """
    try:
        # 使用fetch_knowledge_bases方法获取知识库列表
        kb_list = await fetch_knowledge_bases.fetch_knowledge_bases()

        # 增强知识库信息
        knowledge_bases = []
        for kb in kb_list:
            knowledge_bases.append({
                "id": kb["id"],
                "name": kb["name"],
                "description": f"{kb['name']}的描述"
            })

        return {"data": knowledge_bases}
    except Exception as e:
        logger.error(f"获取知识库列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取知识库列表失败: {str(e)}")


@app.get("/api/knowledge/{knowledge_id}")
async def get_knowledge_base(knowledge_id: str):
    """
    获取特定知识库详情的API端点
    """
    try:
        # 使用fetch_knowledge_bases方法获取知识库列表
        kb_list = await fetch_knowledge_bases.fetch_knowledge_bases()

        # 查找指定ID的知识库
        kb = next((kb for kb in kb_list if kb["id"] == knowledge_id), None)

        if not kb:
            raise HTTPException(status_code=404, detail="知识库不存在")

        return {
            "data": {
                "id": kb["id"],
                "name": kb["name"],
                "description": f"{kb['name']}的详细描述",
                "document_count": 100,
                "created_at": "2025-01-01T00:00:00Z"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取知识库详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取知识库详情失败: {str(e)}")


# 推理接口 - 根据用户选择的推理模式，使用不同推理类
@app.post("/api/inference")
async def inference(request: InferenceRequest):
    mode = request.mode
    query = request.query
    kb_names_list = request.kb_names

    logger.info(f"inference: mode={mode}, query={query}, kb_names={kb_names_list}")

    try:
        if mode == "1":
            # 模式1：直接推理
            # 使用同步生成器，需要转换为异步
            async def async_generator():
                for chunk in inference_mode1.vllm_stream_generator(query):
                    yield chunk

            return StreamingResponse(async_generator(), media_type="application/x-ndjson")

        elif mode == "2":
            # 模式2：知识库增强
            if not kb_names_list:
                return {"error": "请至少选择一个知识库"}

            # 先获取知识库内容
            kb_result = inference_mode2.retrieve_knowledge(query, kb_names_list)
            if not kb_result:
                return {"error": "知识库检索失败"}

            # 使用同步生成器，需要转换为异步
            async def async_generator():
                for chunk in inference_mode2.model_stream_generator(kb_result["context"], query):
                    yield chunk

            return StreamingResponse(async_generator(), media_type="application/x-ndjson")

        elif mode == "3":
            # 模式3：迭代推理
            if not kb_names_list:
                return {"error": "请至少选择一个知识库"}

            # 使用同步生成器，需要转换为异步
            async def async_generator():
                for chunk in inference_mode3.mode3_stream_generator(query, kb_names_list):
                    yield chunk

            return StreamingResponse(async_generator(), media_type="application/x-ndjson")

        else:
            return {"error": f"不支持的推理模式: {mode}"}

    except Exception as e:
        logger.error(f"推理过程发生错误: {str(e)}")
        return {"error": f"推理失败: {str(e)}"}


# 聊天接口 - 修改路径以匹配前端
@app.post("/api/chat")
async def send_message(message: ChatMessageRequest):
    """
    发送聊天消息并获取回复
    """
    logger.info(f"接收到聊天消息: {message}")

    # 调用推理接口
    inference_request = InferenceRequest(
        mode=message.mode,
        query=message.content,
        kb_names=message.kb_names
    )

    # 由于推理接口现在返回流式响应，需要收集完整响应
    try:
        response = await inference(inference_request)

        # 检查是否有错误（非流式响应）
        if isinstance(response, dict) and "error" in response:
            return {"error": response["error"]}

        # 处理流式响应
        if isinstance(response, StreamingResponse):
            # 收集完整响应
            full_response = ""
            search_results = []
            search_queries = []
            inference_steps = []
            final_answer = ""

            async for chunk in response.body_iterator:
                try:
                    chunk_str = chunk.decode('utf-8').strip()
                    if not chunk_str:
                        continue

                    # 处理换行分隔的JSON
                    for line in chunk_str.split('\n'):
                        if not line.strip():
                            continue

                        data = json.loads(line)

                        # 根据类型处理
                        if data["type"] == "answer":
                            full_response += data.get("content", "")
                        elif data["type"] == "final_answer":
                            final_answer = data.get("content", "")
                        elif data["type"] == "search_results":
                            if "documents" in data:
                                search_results.append(data["documents"])
                        elif data["type"] == "search_query":
                            search_queries.append(data.get("content", ""))
                        elif data["type"] == "thinking":
                            if "turn" in data:
                                # 确保有足够的元素
                                while len(inference_steps) < data["turn"]:
                                    inference_steps.append("")
                                inference_steps[data["turn"] - 1] += data.get("content", "")

                except Exception as e:
                    logger.error(f"处理流式响应块时出错: {str(e)}")

            # 根据推理模式返回不同的响应格式
            if message.mode == "1":
                return {"response": full_response or "无法获取推理结果"}
            elif message.mode == "2":
                return {
                    "response": full_response or "无法获取推理结果",
                    "search_results": search_results[0] if search_results else []
                }
            elif message.mode == "3":
                return {
                    "response": final_answer or full_response or "无法获取最终答案",
                    "inference_steps": inference_steps,
                    "search_queries": search_queries,
                    "search_results": search_results
                }

        # 兜底返回
        return {"error": "处理响应时出错"}

    except Exception as e:
        logger.error(f"处理聊天消息时出错: {str(e)}")
        return {"error": f"处理失败: {str(e)}"}


# 流式聊天接口
@app.post("/api/chat/stream")
async def stream_message(message: ChatMessageRequest):
    """
    发送聊天消息并获取流式回复
    """
    logger.info(f"接收到流式聊天消息: {message}")

    # 检查推理模式2和3是否选择了知识库
    if (message.mode == "2" or message.mode == "3") and not message.kb_names:
        return {"error": "请至少选择一个知识库"}

    try:
        # 直接调用推理接口，返回流式响应
        inference_request = InferenceRequest(
            mode=message.mode,
            query=message.content,
            kb_names=message.kb_names
        )

        response = await inference(inference_request)

        # 检查是否有错误（非流式响应）
        if isinstance(response, dict) and "error" in response:
            return {"error": response["error"]}

        # 返回流式响应
        if isinstance(response, StreamingResponse):
            return response

        # 兜底返回
        return {"error": "无法获取流式响应"}

    except Exception as e:
        logger.error(f"流式聊天处理失败: {str(e)}")
        return {"error": f"流式处理失败: {str(e)}"}


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
