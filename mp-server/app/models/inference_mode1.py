from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json
import logging
import asyncio
import time
import random

logger = logging.getLogger(__name__)


def vllm_stream_generator(query: str):
    """模拟模式1流式响应生成器（无需外部vLLM服务）"""

    # 模拟思考过程内容
    thinking_content = [
        "我需要理解这个问题的核心...",
        "这个问题涉及到几个关键概念...",
        "让我从基础定义开始分析...",
        "我可以从多个角度来回答这个问题...",
        "需要考虑问题的历史背景和现代应用..."
    ]

    # 模拟回答内容（根据查询内容动态生成）
    if "人工智能" in query or "AI" in query:
        answer_content = "人工智能(AI)是计算机科学的一个分支，致力于创建能够模拟人类智能的系统。它包括机器学习、深度学习、自然语言处理等多个领域。现代AI已广泛应用于医疗诊断、自动驾驶、语音助手等众多领域，正在深刻改变人类生活和工作方式。"
    elif "指挥控制" in query or "C2" in query:
        answer_content = "指挥控制系统(C2)是军事领域的核心系统，用于指挥官获取态势感知、制定决策并向部队传达命令。现代指挥控制系统通常整合了通信、计算机、情报和监视等多种技术，形成网络化的指挥控制体系，大幅提升作战效能和协同能力。"
    elif "知识库" in query or "数据库" in query:
        answer_content = "知识库是结构化存储和管理知识的系统，通常包含事实、规则、关系等信息。在人工智能领域，知识库为推理引擎提供基础数据支持，是专家系统和语义网络的重要组成部分。现代知识库通常采用图数据库等技术实现高效的知识表示和检索。"
    else:
        answer_content = "您询问的是关于\"{}\"的问题。这是一个很好的问题，需要从多个维度进行分析。首先，我们需要明确概念范围和应用场景，然后结合最新研究成果和实践经验，给出全面而准确的解答。基于当前理解，这个领域正在快速发展，有许多创新应用正在涌现。".format(
            query)

    try:
        # 发送思考阶段头信息
        yield json.dumps({
            "type": "system",
            "content": "=" * 20 + "思考过程" + "=" * 20
        }) + "\n"

        # 模拟思考过程输出
        for thought in thinking_content:
            # 分段输出思考内容
            for i in range(0, len(thought), 5):
                chunk = thought[i:i + 5]
                yield json.dumps({
                    "type": "thinking",
                    "content": chunk
                }) + "\n"
                time.sleep(0.1)  # 模拟网络延迟

            # 每个思考片段后添加换行
            yield json.dumps({
                "type": "thinking",
                "content": "\n"
            }) + "\n"
            time.sleep(0.2)  # 思考片段之间的停顿

        # 发送回答阶段分隔符
        yield json.dumps({
            "type": "system",
            "content": "\n" + "=" * 20 + "正式回复" + "=" * 20
        }) + "\n"

        # 模拟正式回答输出
        for i in range(0, len(answer_content), 8):
            chunk = answer_content[i:i + 8]
            yield json.dumps({
                "type": "answer",
                "content": chunk
            }) + "\n"
            time.sleep(0.1)  # 模拟网络延迟

    except Exception as e:
        logger.error(f"模拟流式输出错误: {str(e)}")
        yield json.dumps({
            "type": "error",
            "content": f"生成回答时出错: {str(e)}"
        }) + "\n"
