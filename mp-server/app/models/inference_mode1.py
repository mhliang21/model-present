from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import OpenAI
from pydantic import BaseModel
import json
import logging
from typing import List, Dict, Optional
import asyncio

logger = logging.getLogger(__name__)

# vLLM服务配置（根据实际部署修改）
VLLM_CONFIG = {
    "base_url": "http://192.168.200.212:12345/v1",  # vLLM服务地址
    "api_key": "EMPTY",  # 如果未启用认证
    "model_name": "QwQ32B-rag"  # 部署的模型名称
}


def vllm_stream_generator(query: str):
    """同步流式响应生成器（修复状态管理）"""
    client = OpenAI(
        api_key=VLLM_CONFIG["api_key"],
        base_url=VLLM_CONFIG["base_url"]
    )

    messages = [{"role": "user", "content": query}]

    try:
        stream = client.chat.completions.create(
            model=VLLM_CONFIG["model_name"],
            messages=messages,
            stream=True,
            extra_body={"chat_template_kwargs": {"thinking": True}}
        )

        # 初始化状态变量
        thinking_phase = True
        sent_thinking_header = False
        sent_answer_header = False

        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            # 调试日志（可选）
            # logger.debug(f"Received chunk: {delta}")

            # 处理思考过程
            reasoning_content = getattr(delta, "reasoning_content", None)
            if reasoning_content:
                if thinking_phase:
                    # 发送思考阶段头信息（仅一次）
                    if not sent_thinking_header:
                        yield json.dumps({
                            "type": "system",
                            "content": "=" * 20 + "思考过程" + "=" * 20
                        }) + "\n"
                        sent_thinking_header = True  # 状态更新

                    # 发送思考内容
                    yield json.dumps({
                        "type": "thinking",
                        "content": reasoning_content
                    }) + "\n"

            # 处理正式回复
            content = getattr(delta, "content", None)
            if content:
                # 状态切换至回答阶段
                if thinking_phase:
                    thinking_phase = False
                    # 发送回答阶段分隔符
                    yield json.dumps({
                        "type": "system",
                        "content": "\n" + "=" * 20 + "正式回复" + "=" * 20
                    }) + "\n"

                # 发送回答内容
                yield json.dumps({
                    "type": "answer",
                    "content": content
                }) + "\n"

    except Exception as e:
        error_msg = f"[vLLM推理错误] {str(e)}"
        logger.error(error_msg)
        yield json.dumps({
            "type": "error",
            "content": error_msg
        }) + "\n"
