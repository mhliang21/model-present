from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import logging
import json
import os
import asyncio

# 导入知识库获取方法
from app.method import fetch_knowledge_bases

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


# 仅测试使用，将检索结果以列表的形式返回
search_results = [{"文档1": "内容1-----------------------------------"},
                  {"文档2": "内容2-----------------------------------"},
                  {"文档3": "内容3"}]

# 仅测试使用，将推理结果以列表的形式返回
inference_results1 = "推理结果1-----------------------------------"
inference_results2 = "推理结果2-----------------------------------"

# 推理模式3
# 仅测试使用，生成自己检索的query
search_query1 = "检索的query1-----------------------------------"
search_query2 = "检索的query2-----------------------------------"
search_query3 = "检索的query3-----------------------------------"

# 生成检索结果
search_results1 = [{"文档1": "内容1-----------------------------------"},
                   {"文档2": "内容2-----------------------------------"},
                   {"文档3": "内容3----------------------------------"}]
search_results2 = [{"文档1": "内容1-----------------------------------"},
                   {"文档2": "内容2-----------------------------------"},
                   {"文档3": "内容3"}]
search_results3 = [{"文档1": "内容1-----------------------------------"},
                   {"文档2": "内容2-----------------------------------"},
                   {"文档3": "内容3-----------------------------------"}]

# 3次推理
mode3_thinking_results1 = "推理结果1-----------------------------------"
mode3_thinking_results2 = "推理结果2-----------------------------------"
mode3_thinking_results3 = "推理结果3-----------------------------------"

# 仅测试使用，生成的最终答案
final_answer1 = "最终答案-----------------------------------"


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
        kb_list = await fetch_knowledge_bases.fetch_knowledge_bases("knowledge_fixed_base.json")

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
        kb_list = await fetch_knowledge_bases.fetch_knowledge_bases("knowledge_fixed_base.json")

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
        kb_list = await fetch_knowledge_bases.fetch_knowledge_bases("knowledge_fixed_base.json")

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


# 第二个服务根据用户选择的推理模式，来使用不同推理类
@app.post("/api/inference")
async def inference(request: InferenceRequest):
    mode = request.mode
    query = request.query
    kb_names_list = request.kb_names

    logger.info(f"inference: mode={mode}, query={query}, kb_names={kb_names_list}")

    if mode == "1":
        # 不使用知识库，直接使用大模型进行推理
        return {"inference_results": inference_results1}
    elif mode == "2":
        # 使用知识库，进行一次性推理
        # 假如使用了推理模式2，前端需要要求用户必须至少选择一个知识库
        # 假如用户没有选择知识库，则返回错误信息
        if not kb_names_list:
            return {"error": "请至少选择一个知识库"}  # 修改：统一使用error字段
        # 先根据用户选择的知识库，进行检索
        # 再根据检索结果，进行推理
        # 最后返回检索结果和推理结果
        return {"search_results": search_results,
                "inference_results": inference_results2}
    elif mode == "3":
        # 使用知识库，进行边推理边检索
        # 假如使用了推理模式3，前端需要要求用户必须至少选择一个知识库
        # 假如用户没有选择知识库，则返回错误信息
        if not kb_names_list:
            return {"error": "请至少选择一个知识库"}  # 修改：统一使用error字段
        # 先不进行检索，还是由大模型经过推理以后生成检索的query
        # 返回的是3次推理思考结果，3次搜索词，3次检索结果，1次最终答案
        return {"thinking_results": [mode3_thinking_results1, mode3_thinking_results2, mode3_thinking_results3],
                "search_query": [search_query1, search_query2, search_query3],
                "search_results": [search_results1, search_results2, search_results3],
                "final_answer": final_answer1}
    else:
        return {"error": f"不支持的推理模式: {mode}"}  # 修改：统一使用error字段


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

    result = await inference(inference_request)

    # 检查是否有错误
    if "error" in result:
        return {"error": result["error"]}

    # 根据推理模式返回不同的响应格式
    if message.mode == "1":
        return {"response": result.get("inference_results", "无法获取推理结果")}
    elif message.mode == "2":
        return {
            "response": result.get("inference_results", "无法获取推理结果"),
            "search_results": result.get("search_results", [])
        }
    elif message.mode == "3":
        return {
            "response": result.get("final_answer", "无法获取最终答案"),
            "inference_steps": result.get("inference_results", []),
            "search_queries": result.get("search_query", []),
            "search_results": result.get("search_results", [])
        }
    else:
        return {"error": "不支持的推理模式"}


# 流式聊天接口 - 新增前端需要的接口
@app.post("/api/chat/stream")
async def stream_message(message: ChatMessageRequest):
    """
    发送聊天消息并获取流式回复
    """
    logger.info(f"接收到流式聊天消息: {message}")

    # 检查推理模式2和3是否选择了知识库
    if (message.mode == "2" or message.mode == "3") and not message.kb_names:
        return {"error": "请至少选择一个知识库"}

    async def generate_stream():
        # 模拟流式响应
        if message.mode == "1":
            # 模式1：直接推理
            response_text = inference_results1
        elif message.mode == "2":
            # 模式2：知识库增强
            response_text = inference_results2
        else:
            # 模式3：迭代推理
            response_text = final_answer1

        # 将响应文本分成多个块进行流式传输
        chunk_size = 10  # 每个块的字符数
        for i in range(0, len(response_text), chunk_size):
            chunk = response_text[i:i + chunk_size]
            yield chunk
            await asyncio.sleep(0.1)  # 模拟处理延迟

    return StreamingResponse(generate_stream(), media_type="text/plain")


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
