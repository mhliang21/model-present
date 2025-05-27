from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from openai import OpenAI
import json
import requests
import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# 配置参数
KB_API_URL = "http://192.168.200.214:5480/v1/kb/chunk/retrieval"


def retrieve_knowledge(query: str, kb_ids: List[str], size: int = 2, min_score: float = 0.5) -> dict:
    """同步获取知识库内容"""
    try:
        response = requests.post(
            KB_API_URL,
            json={
                "question": query,
                "kb_ids": kb_ids,
                "size": size,
                "score_threshold": min_score
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()

        result = response.json()
        if result.get("retcode") != 0:
            logger.error(f"知识库错误：{result.get('retmsg')}")
            return None

        valid_data = [
                         item for item in result.get("data", [])
                         if item.get("_reranker_score", 0) >= min_score
                     ][:size]

        return {
            "documents": valid_data,
            "context": "\n".join(
                f"[来源 {item.get('doc_id', '未知')}] {item.get('content', '')}"
                for item in valid_data
            )
        }

    except Exception as e:
        logger.error(f"知识库检索异常：{str(e)}")
        return None


# 复用模式1的vLLM配置
VLLM_CONFIG = {
    "base_url": "http://192.168.200.218:12345/v1",
    "api_key": "EMPTY",
    "model_name": "QwQ32B-rag"
}


def model_stream_generator(context: str, query: str):
    """vLLM流式生成器（同步版本，需用线程池转换）"""
    client = OpenAI(
        api_key=VLLM_CONFIG["api_key"],
        base_url=VLLM_CONFIG["base_url"]
    )

    messages = [
        {
            "role": "system",
            "content": "你是指挥领域专业助手。请先分析知识库内容，再组织回答。思考过程直接输出自然语言。"
        },
        {
            "role": "user",
            "content": f"""基于以下知识库内容回答问题：
{context}

问题：{query}

回答要求：
1. 先分析知识库中的相关数据
2. 确定需要使用的信息
3. 组织语言形成最终回答"""
        }
    ]

    try:
        stream = client.chat.completions.create(
            model=VLLM_CONFIG["model_name"],
            messages=messages,
            stream=True,
            extra_body={"chat_template_kwargs": {"thinking": True}}
        )

        # 状态管理变量
        thinking_phase = True
        sent_thinking_header = False

        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            # 处理思考内容
            reasoning_content = getattr(delta, "reasoning_content", "")
            if reasoning_content:
                if thinking_phase and not sent_thinking_header:
                    yield json.dumps({
                        "type": "system",
                        "content": "=" * 20 + "知识分析" + "=" * 20
                    }) + "\n"
                    sent_thinking_header = True

                yield json.dumps({
                    "type": "thinking",
                    "content": reasoning_content
                }) + "\n"

            # 处理正式回答
            answer_content = getattr(delta, "content", "")
            if answer_content:
                if thinking_phase:
                    yield json.dumps({
                        "type": "system",
                        "content": "\n" + "=" * 20 + "正式回答" + "=" * 20
                    }) + "\n"
                    thinking_phase = False

                yield json.dumps({
                    "type": "answer",
                    "content": answer_content
                }) + "\n"

    except Exception as e:
        logger.error(f"vLLM流式异常: {str(e)}")
        yield json.dumps({
            "type": "error",
            "content": f"模型推理失败: {str(e)}"
        }) + "\n"
