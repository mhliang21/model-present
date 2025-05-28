import json
import re
import time
import random
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# 模拟知识库检索结果 - 复用模式2的部分数据结构
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

# 模拟思考过程内容
MOCK_THINKING_CONTENT = {
    "指挥控制系统": [
        "首先，我需要理解指挥控制系统的基本概念和组成部分。指挥控制系统是军事领域的核心系统，用于支持指挥决策和行动控制。",
        "接下来，我应该探索现代指挥控制系统的主要功能，包括态势感知、决策支持、任务规划等方面。",
        "最后，我需要分析网络中心战环境下指挥控制系统的特点，如何实现信息共享和协同作战。"
    ],
    "军事装备": [
        "我需要了解现代军事装备的范围和类型，包括武器系统、通信设备、防护装备等。",
        "然后，分析军事装备的发展趋势，如智能化、网络化、模块化和无人化等方向。",
        "最后，探讨军事装备的全生命周期管理，从需求分析到维护升级的系统工程流程。"
    ],
    "人工智能": [
        "首先分析人工智能在军事领域的应用场景，包括态势感知、决策支持、无人系统等。",
        "然后探讨AI如何具体应用于指挥控制系统，提升信息处理和决策效能。",
        "最后，考虑AI应用的技术挑战和发展方向，如何更好地支持军事任务。"
    ],
    "默认": [
        "我需要先理解这个问题的核心关注点和应用背景。",
        "然后分析相关的技术实现和系统集成方案。",
        "最后，总结当前发展状况和未来趋势。"
    ]
}

# 模拟最终答案
MOCK_FINAL_ANSWERS = {
    "指挥控制系统": "基于多轮分析和知识库检索，指挥控制系统(C2)是军事领域的核心系统，用于指挥官获取态势感知、制定决策并向部队传达命令。现代C2系统整合了通信、计算机、情报和监视等多种技术，形成网络化的指挥控制体系。其主要功能包括态势感知、决策支持、任务规划、资源分配、命令传达和执行监控。高效的C2系统能够显著缩短OODA循环(观察-判断-决策-行动)，提升作战效能。在网络中心战环境下，C2系统更强调信息共享和协同作战，通过分布式节点构建弹性网络，提高系统生存能力和作战效能，同时降低决策延迟和信息不对称。",

    "军事装备": "通过多轮分析和知识检索，现代军事装备是高科技与军事需求的结合，涵盖武器系统、通信设备、防护装备、后勤保障等多个方面。装备发展趋势包括智能化、网络化、模块化和无人化。军事装备的系统工程包括需求分析、方案设计、研制生产、试验评估、部署使用和维护升级等全生命周期环节，需要多学科协同和全链条管理。这种系统化的装备发展思路确保了装备性能与实际作战需求的紧密结合，提升整体作战效能。",

    "人工智能": "经过多轮分析和知识库检索，军事领域的人工智能应用包括：智能态势感知、自主决策支持、无人系统控制、预测性维护和网络安全防护等，可显著提升信息处理能力和作战效能。具体到指挥控制系统中，AI的应用主要体现在：大数据分析、态势理解、方案生成、决策辅助和任务规划等方面，能够辅助指挥员更快速准确地做出决策。这些应用正在改变传统的指挥控制模式，提高系统的智能化水平和响应速度，是军事智能化发展的重要方向。",

    "默认": "基于多轮分析和知识检索，关于这个问题，我们可以从多个维度进行理解。该领域涉及多个学科交叉，包括技术实现、系统集成、应用部署和效能评估等方面。深入理解需要综合多维度知识和实践经验。目前该领域正在快速发展，技术创新和应用拓展不断涌现，为军事能力建设提供了新的可能性。未来发展将更加注重系统集成和实战应用，推动军事能力的整体提升。"
}


# 模拟知识库检索
def execute_kb_search(query: str, kb_ids: list) -> list:
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
        sorted_docs = sorted(docs, key=lambda x: x["_reranker_score"], reverse=True)[:2]

        # 模拟网络延迟
        time.sleep(0.3)

        return sorted_docs

    except Exception as e:
        logger.error(f"模拟知识库检索异常: {str(e)}")
        # 返回默认文档，确保接口可用
        return MOCK_DOCUMENTS["默认"][:1]


# 模式3核心逻辑 - 模拟实现
def mode3_stream_generator(query: str, kb_ids: list):
    """模拟模式3多轮迭代推理流式生成器（无需外部vLLM服务）"""

    # 确定查询类型
    if "指挥控制" in query or "C2" in query:
        query_type = "指挥控制系统"
    elif "军事装备" in query or "装备" in query:
        query_type = "军事装备"
    elif "人工智能" in query or "AI" in query:
        query_type = "人工智能"
    else:
        query_type = "默认"

    # 获取该类型的模拟数据
    search_queries = MOCK_SEARCH_QUERIES[query_type]
    thinking_contents = MOCK_THINKING_CONTENT[query_type]
    final_answer = MOCK_FINAL_ANSWERS[query_type]

    # 确定轮次数量
    num_turns = min(len(search_queries), len(thinking_contents))

    try:
        # 多轮迭代推理
        for turn in range(1, num_turns + 1):
            # 发送当前轮次的思考过程头信息
            yield json.dumps({
                "type": "system",
                "turn": turn,
                "content": f"=" * 20 + f"第{turn}轮分析" + "=" * 20
            }) + "\n"

            # 模拟思考过程
            thinking_text = thinking_contents[turn - 1]
            for i in range(0, len(thinking_text), 8):
                chunk = thinking_text[i:i + 8]
                yield json.dumps({
                    "type": "thinking",
                    "turn": turn,
                    "content": chunk
                }) + "\n"
                time.sleep(0.1)  # 模拟网络延迟

            # 发送搜索查询
            search_query = search_queries[turn - 1]
            yield json.dumps({
                "type": "search_query",
                "turn": turn,
                "content": search_query
            }) + "\n"

            time.sleep(0.5)  # 模拟搜索延迟

            # 执行模拟检索
            search_results = execute_kb_search(search_query, kb_ids)

            # 发送搜索结果
            yield json.dumps({
                "type": "search_results",
                "turn": turn,
                "query": search_query,
                "documents": [
                    {
                        "doc_id": doc["doc_id"],
                        "content": doc["content"][:300],
                        "_reranker_score": doc["_reranker_score"]
                    }
                    for doc in search_results
                ]
            }) + "\n"

            # 如果不是最后一轮，添加分隔符
            if turn < num_turns:
                yield json.dumps({
                    "type": "system",
                    "content": "-" * 40
                }) + "\n"
                time.sleep(0.5)  # 轮次间隔

        # 发送最终答案分隔符
        yield json.dumps({
            "type": "system",
            "content": "\n" + "=" * 20 + "最终回答" + "=" * 20
        }) + "\n"

        # 发送最终答案
        for i in range(0, len(final_answer), 10):
            chunk = final_answer[i:i + 10]
            yield json.dumps({
                "type": "final_answer",
                "content": chunk
            }) + "\n"
            time.sleep(0.1)  # 模拟网络延迟

    except Exception as e:
        logger.error(f"模拟流式输出错误: {str(e)}")
        yield json.dumps({
            "type": "error",
            "content": f"生成回答时出错: {str(e)}"
        }) + "\n"


# 生成最终答案 - 模拟实现
def generate_final_answer(state: dict) -> str:
    """模拟生成最终答案（无需外部vLLM服务）"""
    query = state.get("current_query", "")

    # 根据查询类型返回对应的最终答案
    if "指挥控制" in query or "C2" in query:
        return MOCK_FINAL_ANSWERS["指挥控制系统"]
    elif "军事装备" in query or "装备" in query:
        return MOCK_FINAL_ANSWERS["军事装备"]
    elif "人工智能" in query or "AI" in query:
        return MOCK_FINAL_ANSWERS["人工智能"]
    else:
        return MOCK_FINAL_ANSWERS["默认"]
