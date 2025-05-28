from fastapi import HTTPException
from fastapi.responses import StreamingResponse
import json
import logging
import time
import random
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# 模拟知识库检索结果
MOCK_DOCUMENTS = {
    "指挥控制系统": [
        {
            "doc_id": "doc001",
            "content": "指挥控制系统(C2)是军事领域的核心系统，用于指挥官获取态势感知、制定决策并向部队传达命令。现代C2系统整合了通信、计算机、情报和监视等多种技术，形成网络化的指挥控制体系。",
            "_reranker_score": 0.92
        },
        {
            "doc_id": "doc002",
            "content": "指挥控制系统的主要功能包括：态势感知、决策支持、任务规划、资源分配、命令传达和执行监控。高效的C2系统能够显著缩短OODA循环(观察-判断-决策-行动)，提升作战效能。",
            "_reranker_score": 0.87
        },
        {
            "doc_id": "doc003",
            "content": "网络中心战环境下的指挥控制系统强调信息共享和协同作战，通过分布式节点构建弹性网络，提高系统生存能力和作战效能，同时降低决策延迟和信息不对称。",
            "_reranker_score": 0.81
        }
    ],
    "军事装备": [
        {
            "doc_id": "doc101",
            "content": "现代军事装备是高科技与军事需求的结合，涵盖武器系统、通信设备、防护装备、后勤保障等多个方面。装备发展趋势包括智能化、网络化、模块化和无人化。",
            "_reranker_score": 0.89
        },
        {
            "doc_id": "doc102",
            "content": "军事装备的系统工程包括需求分析、方案设计、研制生产、试验评估、部署使用和维护升级等全生命周期环节，需要多学科协同和全链条管理。",
            "_reranker_score": 0.85
        }
    ],
    "人工智能": [
        {
            "doc_id": "doc201",
            "content": "军事领域的人工智能应用包括：智能态势感知、自主决策支持、无人系统控制、预测性维护和网络安全防护等，可显著提升信息处理能力和作战效能。",
            "_reranker_score": 0.94
        },
        {
            "doc_id": "doc202",
            "content": "人工智能在指挥控制系统中的应用主要体现在：大数据分析、态势理解、方案生成、决策辅助和任务规划等方面，能够辅助指挥员更快速准确地做出决策。",
            "_reranker_score": 0.91
        }
    ],
    "默认": [
        {
            "doc_id": "doc901",
            "content": "这是关于该主题的基础知识文档，包含了核心概念、应用场景和发展趋势等内容。该领域正在快速发展，技术创新和应用拓展不断涌现。",
            "_reranker_score": 0.75
        },
        {
            "doc_id": "doc902",
            "content": "该主题涉及多个学科交叉领域，包括技术实现、系统集成、应用部署和效能评估等方面。深入理解需要综合多维度知识和实践经验。",
            "_reranker_score": 0.72
        }
    ]
}

# 模拟搜索查询生成
MOCK_SEARCH_QUERIES = {
    "指挥控制系统": [
        "指挥控制系统的定义和组成",
        "现代指挥控制系统的主要功能",
        "网络中心战环境下的指挥控制系统特点"
    ],
    "军事装备": [
        "现代军事装备的发展趋势",
        "军事装备的系统工程流程"
    ],
    "人工智能": [
        "军事领域的人工智能应用场景",
        "人工智能在指挥控制系统中的应用"
    ],
    "默认": [
        "该主题的基本概念和应用场景",
        "该领域的技术实现和系统集成"
    ]
}


def retrieve_knowledge(query: str, kb_ids: List[str], size: int = 2, min_score: float = 0.5) -> dict:
    """模拟知识库检索（无需外部知识库服务）"""
    try:
        logger.info(f"模拟知识库检索: query={query}, kb_ids={kb_ids}")

        # 根据查询关键词选择合适的模拟文档集
        if "指挥控制" in query or "C2" in query:
            docs = MOCK_DOCUMENTS["指挥控制系统"]
        elif "军事装备" in query or "装备" in query:
            docs = MOCK_DOCUMENTS["军事装备"]
        elif "人工智能" in query or "AI" in query:
            docs = MOCK_DOCUMENTS["人工智能"]
        else:
            docs = MOCK_DOCUMENTS["默认"]

        # 随机调整相关性分数，增加多样性
        for doc in docs:
            doc["_reranker_score"] = round(doc["_reranker_score"] * random.uniform(0.95, 1.0), 2)

        # 按相关性排序并限制数量
        sorted_docs = sorted(docs, key=lambda x: x["_reranker_score"], reverse=True)[:size]

        # 构建上下文文本
        context = "\n\n".join([
            f"[来源 {doc['doc_id']}] {doc['content']}"
            for doc in sorted_docs
        ])

        # 模拟网络延迟
        time.sleep(0.5)

        return {
            "documents": sorted_docs,
            "context": context
        }

    except Exception as e:
        logger.error(f"模拟知识库检索异常: {str(e)}")
        # 返回默认文档，确保接口可用
        default_docs = MOCK_DOCUMENTS["默认"][:1]
        return {
            "documents": default_docs,
            "context": default_docs[0]["content"]
        }


def model_stream_generator(context: str, query: str):
    """模拟模式2流式生成器（无需外部vLLM服务）"""

    try:
        # 发送系统消息：知识库检索中
        yield json.dumps({
            "type": "system",
            "content": "正在分析知识库内容..."
        }) + "\n"

        time.sleep(0.3)  # 模拟分析延迟

        # 发送思考阶段头信息
        yield json.dumps({
            "type": "system",
            "content": "=" * 20 + "知识分析" + "=" * 20
        }) + "\n"

        # 模拟思考过程
        thinking_steps = [
            "分析知识库中的关键信息...",
            "提取与问题相关的核心概念...",
            "整合多个文档的信息...",
            "构建连贯的回答框架..."
        ]

        for step in thinking_steps:
            # 分段输出思考内容
            for i in range(0, len(step), 5):
                chunk = step[i:i + 5]
                yield json.dumps({
                    "type": "thinking",
                    "content": chunk
                }) + "\n"
                time.sleep(0.1)

            # 每个思考步骤后添加换行
            yield json.dumps({
                "type": "thinking",
                "content": "\n"
            }) + "\n"
            time.sleep(0.2)

        # 确定查询类型
        if "指挥控制" in query or "C2" in query:
            query_type = "指挥控制系统"
        elif "军事装备" in query or "装备" in query:
            query_type = "军事装备"
        elif "人工智能" in query or "AI" in query:
            query_type = "人工智能"
        else:
            query_type = "默认"

        # 获取该类型的模拟搜索查询
        search_queries = MOCK_SEARCH_QUERIES[query_type]

        # 发送搜索查询信息
        yield json.dumps({
            "type": "system",
            "content": "\n" + "=" * 20 + "知识库检索" + "=" * 20
        }) + "\n"

        # 发送第一个搜索查询
        search_query = search_queries[0]
        yield json.dumps({
            "type": "search_query",
            "turn": 1,
            "content": search_query
        }) + "\n"

        time.sleep(0.5)  # 模拟搜索延迟

        # 执行模拟检索
        search_results = retrieve_knowledge(search_query, ["kb001", "kb002"])

        # 发送搜索结果
        yield json.dumps({
            "type": "search_results",
            "turn": 1,
            "query": search_query,
            "documents": [
                {
                    "doc_id": doc["doc_id"],
                    "content": doc["content"][:300],
                    "_reranker_score": doc["_reranker_score"]
                }
                for doc in search_results["documents"]
            ]
        }) + "\n"

        # 如果有第二个搜索查询，也发送
        if len(search_queries) > 1:
            time.sleep(0.8)  # 模拟思考延迟

            search_query = search_queries[1]
            yield json.dumps({
                "type": "search_query",
                "turn": 2,
                "content": search_query
            }) + "\n"

            time.sleep(0.5)  # 模拟搜索延迟

            # 执行模拟检索
            search_results = retrieve_knowledge(search_query, ["kb001", "kb002"])

            # 发送搜索结果
            yield json.dumps({
                "type": "search_results",
                "turn": 2,
                "query": search_query,
                "documents": [
                    {
                        "doc_id": doc["doc_id"],
                        "content": doc["content"][:300],
                        "_reranker_score": doc["_reranker_score"]
                    }
                    for doc in search_results["documents"]
                ]
            }) + "\n"

        # 基于上下文和查询生成回答
        if "指挥控制" in query or "C2" in query:
            answer = "指挥控制系统(C2)是军事领域的核心系统，用于指挥官获取态势感知、制定决策并向部队传达命令。根据知识库内容，现代C2系统整合了通信、计算机、情报和监视等多种技术，形成网络化的指挥控制体系。其主要功能包括态势感知、决策支持、任务规划、资源分配、命令传达和执行监控。高效的C2系统能够显著缩短OODA循环(观察-判断-决策-行动)，提升作战效能。在网络中心战环境下，C2系统更强调信息共享和协同作战，通过分布式节点构建弹性网络，提高系统生存能力。"
        elif "军事装备" in query:
            answer = "根据知识库资料，现代军事装备是高科技与军事需求的结合，涵盖武器系统、通信设备、防护装备、后勤保障等多个方面。装备发展趋势包括智能化、网络化、模块化和无人化。军事装备的系统工程包括需求分析、方案设计、研制生产、试验评估、部署使用和维护升级等全生命周期环节，需要多学科协同和全链条管理。这种系统化的装备发展思路确保了装备性能与实际作战需求的紧密结合。"
        elif "人工智能" in query or "AI" in query:
            answer = "根据知识库内容，军事领域的人工智能应用包括：智能态势感知、自主决策支持、无人系统控制、预测性维护和网络安全防护等，可显著提升信息处理能力和作战效能。具体到指挥控制系统中，AI的应用主要体现在：大数据分析、态势理解、方案生成、决策辅助和任务规划等方面，能够辅助指挥员更快速准确地做出决策。这些应用正在改变传统的指挥控制模式，提高系统的智能化水平和响应速度。"
        else:
            answer = "根据知识库资料，关于\"{}\"的问题，我们可以从多个维度进行分析。该领域涉及多个学科交叉，包括技术实现、系统集成、应用部署和效能评估等方面。深入理解需要综合多维度知识和实践经验。目前该领域正在快速发展，技术创新和应用拓展不断涌现，为军事能力建设提供了新的可能性。".format(
                query)

        # 发送回答阶段分隔符
        yield json.dumps({
            "type": "system",
            "content": "\n" + "=" * 20 + "基于知识库的回答" + "=" * 20
        }) + "\n"

        # 模拟正式回答输出
        for i in range(0, len(answer), 10):
            chunk = answer[i:i + 10]
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
