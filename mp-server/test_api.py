# API端点验证测试脚本

import requests
import json
import time

BASE_URL = "http://localhost:8000"


def test_knowledge_endpoints():
    """测试知识库相关API端点"""
    print("\n===== 测试知识库API端点 =====")

    # 测试知识库列表
    try:
        response = requests.get(f"{BASE_URL}/api/knowledge")
        print(f"知识库列表状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"知识库数量: {len(data.get('data', []))}")
            print(f"知识库示例: {data.get('data', [])[0] if data.get('data') else '无数据'}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"知识库列表请求异常: {str(e)}")

    # 测试知识库名称列表
    try:
        response = requests.get(f"{BASE_URL}/api/knowledge/list")
        print(f"知识库名称列表状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"知识库名称: {data.get('message', [])}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"知识库名称列表请求异常: {str(e)}")

    return True


def test_inference_mode1():
    """测试模式1推理API"""
    print("\n===== 测试模式1推理API =====")

    try:
        response = requests.post(
            f"{BASE_URL}/api/inference",
            json={
                "mode": "1",
                "query": "什么是人工智能?",
                "kb_names": []
            }
        )

        print(f"模式1推理状态码: {response.status_code}")
        if response.status_code == 200:
            # 检查是否为流式响应
            content_type = response.headers.get('content-type', '')
            if 'application/x-ndjson' in content_type:
                print("成功: 收到流式响应")

                # 解析流式响应
                line_count = 0
                for line in response.iter_lines():
                    if line:
                        line_count += 1
                        try:
                            data = json.loads(line.decode())
                            print(f"类型: {data.get('type')}, 内容长度: {len(data.get('content', ''))}")
                        except:
                            print(f"无法解析行: {line.decode()[:50]}...")

                print(f"总计接收 {line_count} 行数据")
            else:
                print(f"响应内容: {response.json()}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"模式1推理请求异常: {str(e)}")

    return True


def test_inference_mode2():
    """测试模式2推理API"""
    print("\n===== 测试模式2推理API =====")

    # 先获取知识库列表
    try:
        kb_response = requests.get(f"{BASE_URL}/api/knowledge/list")
        kb_names = kb_response.json().get('message', [])

        if not kb_names:
            print("无可用知识库，跳过模式2测试")
            return False

        # 使用第一个知识库进行测试
        test_kb = kb_names[0]
        print(f"使用知识库: {test_kb}")

        response = requests.post(
            f"{BASE_URL}/api/inference",
            json={
                "mode": "2",
                "query": "什么是指挥控制系统?",
                "kb_names": [test_kb]
            }
        )

        print(f"模式2推理状态码: {response.status_code}")
        if response.status_code == 200:
            # 检查是否为流式响应
            content_type = response.headers.get('content-type', '')
            if 'application/x-ndjson' in content_type:
                print("成功: 收到流式响应")

                # 解析流式响应
                line_count = 0
                search_results_found = False

                for line in response.iter_lines():
                    if line:
                        line_count += 1
                        try:
                            data = json.loads(line.decode())
                            print(f"类型: {data.get('type')}, 内容长度: {len(data.get('content', ''))}")

                            if data.get('type') == 'search_results':
                                search_results_found = True
                                print(f"检索到 {len(data.get('documents', []))} 条结果")
                        except:
                            print(f"无法解析行: {line.decode()[:50]}...")

                print(f"总计接收 {line_count} 行数据")
                print(f"检索结果状态: {'已找到' if search_results_found else '未找到'}")
            else:
                print(f"响应内容: {response.json()}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"模式2推理请求异常: {str(e)}")

    return True


def test_inference_mode3():
    """测试模式3推理API"""
    print("\n===== 测试模式3推理API =====")

    # 先获取知识库列表
    try:
        kb_response = requests.get(f"{BASE_URL}/api/knowledge/list")
        kb_names = kb_response.json().get('message', [])

        if not kb_names:
            print("无可用知识库，跳过模式3测试")
            return False

        # 使用第一个知识库进行测试
        test_kb = kb_names[0]
        print(f"使用知识库: {test_kb}")

        response = requests.post(
            f"{BASE_URL}/api/inference",
            json={
                "mode": "3",
                "query": "什么是指挥控制系统的主要功能?",
                "kb_names": [test_kb]
            }
        )

        print(f"模式3推理状态码: {response.status_code}")
        if response.status_code == 200:
            # 检查是否为流式响应
            content_type = response.headers.get('content-type', '')
            if 'application/x-ndjson' in content_type:
                print("成功: 收到流式响应")

                # 解析流式响应
                line_count = 0
                search_results_found = False
                final_answer_found = False
                turns = set()

                for line in response.iter_lines():
                    if line:
                        line_count += 1
                        try:
                            data = json.loads(line.decode())
                            turn = data.get('turn', 0)
                            if turn:
                                turns.add(turn)

                            print(f"类型: {data.get('type')}, 轮次: {turn}, 内容长度: {len(data.get('content', ''))}")

                            if data.get('type') == 'search_results':
                                search_results_found = True
                            elif data.get('type') == 'final_answer':
                                final_answer_found = True
                        except:
                            print(f"无法解析行: {line.decode()[:50]}...")

                print(f"总计接收 {line_count} 行数据")
                print(f"检索结果状态: {'已找到' if search_results_found else '未找到'}")
                print(f"最终答案状态: {'已找到' if final_answer_found else '未找到'}")
                print(f"检测到的轮次: {sorted(list(turns))}")
            else:
                print(f"响应内容: {response.json()}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"模式3推理请求异常: {str(e)}")

    return True


def test_chat_stream_api():
    """测试流式聊天API"""
    print("\n===== 测试流式聊天API =====")

    try:
        response = requests.post(
            f"{BASE_URL}/api/chat/stream",
            json={
                "content": "什么是人工智能?",
                "mode": "1",
                "kb_names": []
            },
            stream=True
        )

        print(f"流式聊天状态码: {response.status_code}")
        if response.status_code == 200:
            # 检查是否为流式响应
            content_type = response.headers.get('content-type', '')
            if 'application/x-ndjson' in content_type:
                print("成功: 收到流式响应")

                # 解析流式响应
                line_count = 0
                for line in response.iter_lines():
                    if line:
                        line_count += 1
                        try:
                            data = json.loads(line.decode())
                            print(f"类型: {data.get('type')}, 内容长度: {len(data.get('content', ''))}")
                        except:
                            print(f"无法解析行: {line.decode()[:50]}...")

                print(f"总计接收 {line_count} 行数据")
            else:
                print(f"响应内容: {response.text[:200]}...")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"流式聊天请求异常: {str(e)}")

    return True


def run_all_tests():
    """运行所有测试"""
    print("开始API端点验证测试...")

    # 测试根端点
    try:
        response = requests.get(BASE_URL)
        print(f"根端点状态码: {response.status_code}")
        print(f"根端点响应: {response.json()}")
    except Exception as e:
        print(f"根端点请求异常: {str(e)}")
        print("服务可能未启动，请先启动服务")
        return

    # 运行各项测试
    test_knowledge_endpoints()
    test_inference_mode1()
    test_inference_mode2()
    test_inference_mode3()
    test_chat_stream_api()

    print("\n所有测试完成!")


if __name__ == "__main__":
    run_all_tests()
