from fastapi import FastAPI, HTTPException,Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="智能问答系统API",
    description="基于FastAPI的智能问答系统后端（简化版）",
    version="1.0.0"
)

# 配置CORS
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

# 仅供测试使用，先将知识库的名称以列表的形式
kb_names = ["理论研究教材知识库", "军事理论学术论文", "认知心理学研究论文库", "指挥学论文库", "学术期刊论文集"]

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
mode3_inference_results1 = "推理结果1-----------------------------------"
mode3_inference_results2 = "推理结果2-----------------------------------"
mode3_inference_results3 = "推理结果3-----------------------------------"

# 仅测试使用，生成的最终答案
final_answer1 = "最终答案-----------------------------------"


# 请求模型
class InferenceRequest(BaseModel):
    mode: str
    query: str
    kb_names: List[str]


# 第一个服务是显示当前所有知识库的名称
@app.get("/api/get_knowledge_base_names")
async def get_knowledge_base_names():
    return {"message": kb_names}


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
            return {"error_message": "请至少选择一个知识库"}
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
            return {"error_message": "请至少选择一个知识库"}
        # 先不进行检索，还是由大模型经过推理以后生成检索的query
        # 返回的是3次推理结果，3次搜索词，3次检索结果，1次最终答案
        return {"inference_results": [mode3_inference_results1, mode3_inference_results2, mode3_inference_results3],
                "search_query": [search_query1, search_query2, search_query3],
                "search_results": [search_results1, search_results2, search_results3],
                "final_answer": final_answer1}
    else:
        return {"error_message": f"不支持的推理模式: {mode}"}


# 聊天消息模型
class ChatMessageRequest(BaseModel):
    content: str
    mode: str = "1"  # 默认使用模式1
    kb_names: List[str] = []  # 默认不使用知识库


# 兼容原有的聊天接口，但内部调用新的推理接口
@app.post("/api/chat/message")
async def send_message(message: ChatMessageRequest):
    # 调用推理接口
    inference_request = InferenceRequest(
        mode=message.mode,
        query=message.content,
        kb_names=message.kb_names
    )

    result = await inference(inference_request)

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
        return {"response": "不支持的推理模式"}


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
        log_level="debug"  # 新增
    )
