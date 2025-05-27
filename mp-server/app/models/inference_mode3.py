import json
import re
import httpx
import requests
from pydantic import BaseModel
from openai import OpenAI, AsyncOpenAI
from typing import Dict, List, Optional

# 配置常量
VLLM_CONFIG = {
    "base_url": "http://192.168.200.212:12345/v1",
    "api_key": "EMPTY",
    "model_name": "QwQ32B-rag"
}
KB_API_URL = "http://192.168.200.214:5480/v1/kb/chunk/retrieval"
MAX_TURNS = 3
MAX_SEARCH_PER_TURN = 3


# 提示工程工具函数
def build_reasoning_prompt(state: dict) -> str:
    return f"""**任务说明**:
        你是一个智能推理助手，需要逐步解决用户的问题。你可以:
        1. 分析当前问题
        2. 如果需要，提出具体的搜索查询
        3. 根据搜索结果进行推理
        4. 最终给出完整答案

        **当前状态**:
        问题: {state['current_query']}
        历史推理: {format_history(state['history'])}
        已执行的搜索: {format_executed_searches(state['search_queries'])}
        搜索结果: {format_search_results(state['search_results'])}

        **你的任务**:
        - 如果需要更多信息，使用以下格式提出搜索查询:
        <|begin_search_query|>你的查询<|end_search_query|>
        - 如果有搜索结果，使用以下格式提供分析:
        <|begin_search_result|>分析结果<|end_search_result|>
        - 当你准备好给出最终答案时，直接回答:
        最终答案: 你的答案

        **注意**:
        - 每次只提出一个搜索查询
        - 确保搜索查询与当前问题直接相关
        - 避免重复搜索相同内容
"""


def format_history(history: list) -> str:
    return "\n".join([f"第{i + 1}轮推理：{h[:200]}..." for i, h in enumerate(history)])


def format_executed_searches(queries: list) -> str:
    return "\n".join([f"搜索 {i + 1}: {q}" for i, q in enumerate(queries)])


def format_search_results(results: list) -> str:
    if not results:
        return "暂无搜索结果"
    formatted = []
    for search_idx, search_group in enumerate(results, 1):
        formatted.append(f"=== 第{search_idx}次搜索 ===")
        for doc_idx, doc in enumerate(search_group, 1):
            formatted.append(f"文档{doc_idx}：{format_single_result(doc)}")
    return "\n\n".join(formatted)


def format_single_result(result: dict) -> str:
    return f"[文档 {result.get('doc_id', '未知')}] 相关性：{result.get('_reranker_score', 0):.2f}\n{result.get('content', '')[:300]}..."


# 模式3核心逻辑修改
def mode3_stream_generator(query: str, kb_ids: list):
    """支持多轮流式推理（修复历史记录类型问题）"""
    state = {
        "current_query": query,
        "history": [],  # 现在只存储字符串
        "search_queries": [],
        "search_results": [],
        "finished": False,
        "current_turn": 0
    }

    client = OpenAI(
        api_key=VLLM_CONFIG["api_key"],
        base_url=VLLM_CONFIG["base_url"]
    )

    try:
        while not state['finished'] and state['current_turn'] < MAX_TURNS:
            state['current_turn'] += 1
            print(f"\n🌀 进入第 {state['current_turn']} 轮推理")

            # 生成提示词
            prompt = build_reasoning_prompt(state)
            stream = client.chat.completions.create(
                model=VLLM_CONFIG["model_name"],
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                extra_body={
                    "chat_template_kwargs": {
                        "enable_special_tokens": True,
                        "thinking": True
                    }
                }
            )

            response_buffer = ""
            search_triggered = False
            thinking_phase = True
            sent_thinking_header = False

            try:
                for chunk in stream:
                    if not chunk.choices:
                        continue

                    delta = chunk.choices[0].delta

                    # 同时获取两个字段
                    reasoning_content = getattr(delta, "reasoning_content", "") or ""
                    answer_content = getattr(delta, "content", "") or ""
                    combined_content = reasoning_content + answer_content
                    response_buffer += combined_content

                    # 处理思考内容
                    if reasoning_content:
                        if thinking_phase and not sent_thinking_header:
                            yield json.dumps({
                                "type": "system",
                                "turn": state['current_turn'],
                                "content": "=" * 20 + "分析过程" + "=" * 20
                            }) + "\n"
                            sent_thinking_header = True

                        yield json.dumps({
                            "type": "thinking",
                            "turn": state['current_turn'],
                            "content": reasoning_content
                        }) + "\n"

                    # 处理正式回答
                    if answer_content:
                        if thinking_phase:
                            thinking_phase = False
                            yield json.dumps({
                                "type": "system",
                                "turn": state['current_turn'],
                                "content": "\n" + "=" * 20 + "综合回答" + "=" * 20
                            }) + "\n"

                        yield json.dumps({
                            "type": "answer",
                            "turn": state['current_turn'],
                            "content": answer_content
                        }) + "\n"

                    # 处理搜索请求
                    if "<|end_search_query|>" in response_buffer:
                        query_match = re.search(
                            r'<\|begin_search_query\|>(.*?)<\|end_search_query\|>',
                            response_buffer,
                            re.DOTALL
                        )
                        if query_match:
                            search_query = query_match.group(1).strip()
                            if search_query not in state['search_queries']:
                                print(f"\n触发搜索：{search_query}")
                                raw_results = execute_kb_search(search_query, kb_ids)

                                # 更新状态
                                state['search_queries'].append(search_query)
                                state['search_results'].append([
                                    {
                                        "doc_id": str(r.get("doc_id", "未知")),
                                        "content": str(r.get("content", "")),
                                        "_reranker_score": float(r.get("_reranker_score", 0))
                                    }
                                    for r in raw_results
                                ])

                                # 发送搜索结果
                                yield json.dumps({
                                    "type": "search_results",
                                    "turn": state['current_turn'],
                                    "query": search_query,
                                    "documents": [
                                        {
                                            "doc_id": str(r.get("doc_id", "未知")),
                                            "content": (r.get("content") or "")[:300],
                                            "_reranker_score": float(r.get("_reranker_score", 0))
                                        }
                                        for r in raw_results if isinstance(r, dict)
                                    ]
                                }) + "\n"

                                # 处理缓冲区
                                parts = response_buffer.split('<|end_search_query|>', 1)
                                response_buffer = parts[1] if len(parts) > 1 else ''

                                if response_buffer.strip():
                                    yield json.dumps({
                                        "type": "thinking",
                                        "turn": state['current_turn'],
                                        "content": response_buffer
                                    }) + "\n"
                                    response_buffer = ""

                                search_triggered = True
                                break

                    # 检测最终答案
                    final_answer_pattern = re.compile(
                        r'最终答案\s*:\s*((?:.|\n)*)',
                        re.IGNORECASE | re.DOTALL
                    )
                    if final_answer_pattern.search(response_buffer.lower()):
                        answer_match = final_answer_pattern.search(response_buffer)
                        if answer_match:
                            state['finished'] = True
                            remaining_content = answer_match.group(1).strip()

                            if remaining_content:
                                yield json.dumps({
                                    "type": "answer",
                                    "turn": state['current_turn'],
                                    "content": remaining_content
                                }) + "\n"

                            yield json.dumps({
                                "type": "final_answer",
                                "content": generate_final_answer(state),
                                "search_queries": state['search_queries'],
                                "search_results": [
                                    [format_single_result(r) for r in res]
                                    for res in state['search_results']
                                ]
                            }) + "\n"
                            return

            except StopIteration:
                pass  # 显式处理迭代终止

            # 记录本轮完整历史（字符串）
            state['history'].append(response_buffer)

            if search_triggered:
                print("🔄 搜索完成，准备新一轮推理")
                continue

        # 兜底处理
        if not state['finished']:
            print(f"\n⚠️ 达到最大轮数（{MAX_TURNS}），触发流式兜底回答")

            # 构建兜底提示词（与正常流程一致）
            fallback_prompt = build_reasoning_prompt(state) + "\n\n请基于已有信息直接给出最终答案："

            # 创建带思考功能的流式生成
            fallback_stream = client.chat.completions.create(
                model=VLLM_CONFIG["model_name"],
                messages=[{"role": "user", "content": fallback_prompt}],
                stream=True,
                extra_body={
                    "chat_template_kwargs": {
                        "enable_special_tokens": True,
                        "thinking": True
                    }
                }
            )

            # 状态管理变量
            fallback_buffer = ""
            is_thinking_phase = True
            final_answer_started = False

            try:
                for chunk in fallback_stream:
                    if not chunk.choices:
                        continue

                    delta = chunk.choices[0].delta

                    # 同时处理两个内容字段
                    reasoning_content = getattr(delta, "reasoning_content", "") or ""
                    answer_content = getattr(delta, "content", "") or ""
                    combined = reasoning_content + answer_content
                    fallback_buffer += combined

                    # 处理思考内容
                    if reasoning_content:
                        if is_thinking_phase:
                            yield json.dumps({
                                "type": "system",
                                "turn": state['current_turn'],
                                "content": "=" * 20 + "兜底分析" + "=" * 20
                            }) + "\n"
                            is_thinking_phase = False

                        yield json.dumps({
                            "type": "thinking",
                            "turn": state['current_turn'],
                            "content": reasoning_content
                        }) + "\n"

                    # 处理正式回答
                    if answer_content:
                        if not final_answer_started:
                            yield json.dumps({
                                "type": "system",
                                "turn": state['current_turn'],
                                "content": "\n" + "=" * 20 + "兜底回答" + "=" * 20
                            }) + "\n"
                            final_answer_started = True

                        yield json.dumps({
                            "type": "answer",
                            "turn": state['current_turn'],
                            "content": answer_content
                        }) + "\n"

                # 最终格式化
                yield json.dumps({
                    "type": "final_answer",
                    "content": fallback_buffer.strip(),
                    "search_queries": state['search_queries'],
                    "search_results": [
                        [format_single_result(r) for r in res]
                        for res in state['search_results']
                    ]
                }) + "\n"

            except Exception as e:
                yield json.dumps({
                    "type": "error",
                    "content": f"兜底流程错误: {str(e)}"
                }) + "\n"

    except Exception as e:
        import traceback
        traceback.print_exc()
        yield json.dumps({
            "type": "error",
            "content": f"处理失败：{str(e)}"
        }) + "\n"


# 生成最终答案（与模式2格式一致）
def generate_final_answer(state: dict) -> str:
    client = OpenAI(
        api_key=VLLM_CONFIG["api_key"],
        base_url=VLLM_CONFIG["base_url"]
    )

    context = "\n".join([
        f"第{i + 1}次搜索：{q}\n结果：{format_search_results([res])}"
        for i, (q, res) in enumerate(zip(
            state['search_queries'],
            state['search_results']
        ))
    ])

    response = client.chat.completions.create(
        model=VLLM_CONFIG["model_name"],
        messages=[{
            "role": "user",
            "content": f"问题：{state['current_query']}\n根据以下信息回答：\n{context}"
        }]
    )
    return response.choices[0].message.content


# 同步知识库检索
# 修改execute_kb_search确保数据结构正确
def execute_kb_search(query: str, kb_ids: list) -> list:
    """强化数据校验的知识库检索"""
    try:
        with httpx.Client() as client:
            response = client.post(
                KB_API_URL,
                json={
                    "question": query,
                    "kb_ids": kb_ids,
                    "size": MAX_SEARCH_PER_TURN,
                    "score_threshold": 0.5
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

        valid_results = []
        for item in data.get("data", [])[:MAX_SEARCH_PER_TURN]:
            if not isinstance(item, dict):
                continue

            sanitized = {
                "doc_id": str(item.get("doc_id", f"unk_{len(valid_results)}")),
                "content": str(item.get("content", "")),
                "_reranker_score": float(item.get("_reranker_score", 0))
            }

            if len(sanitized["content"]) > 10:
                valid_results.append(sanitized)

        print(f"✅ 检索到 {len(valid_results)} 条有效结果")
        return valid_results
    except Exception as e:
        print(f"❌ 检索失败: {str(e)}")
        return []
