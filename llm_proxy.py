import json
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from Chat_api_test import communicate_with_llm  # 导入 LLM 交互函数
from ChatMEM_api_test import export_and_upload_chat_history  # 导入聊天历史上传函数

# 该程序测试Open-LLM-VTuber的后端API，使用openapi。cmd打开该程序端口后用llm_proxy_test.py作为api输入。
# 使用方法（cmd)：uvicorn llm_proxy:app --host 0.0.0.0 --port 8000 --reload

# 创建 FastAPI 应用
app = FastAPI()

# 配置 API 相关参数
API_KEY = "[你的anythingllm API_key]"  #
WORKSPACE_SLUG = "anythingllm_test"

# ✅ 统一管理全局变量（线程安全）
app.state.chat_count = 0  # 计数器 & 记录上一轮的 `latest_doc_hash`
app.state.latest_doc_hash = None # 用于存储最新的文档 Hash
TEMP_FILE = "chat_history.json"  # 存储聊天记录的 JSON 文件


# OpenAI Chat Completion 请求格式
class ChatRequest(BaseModel):
    model: str
    messages: list  # [{"role": "user", "content": "你的问题？"}]
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 1.0
    stream: bool = False


@app.post("/chat")
async def chat_with_llm(request: ChatRequest):
    """
    监听 OpenAI Chat Completion 格式的 API 请求，并将其转换为 LLM 交互。

    - 解析用户输入（弹幕内容）
    - 调用 `communicate_with_llm`
    - 以 OpenAI 兼容格式返回 LLM 响应
    """

    try:
        # 获取最新的用户输入
        user_messages = [msg for msg in request.messages if msg["role"] == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="没有找到用户输入消息！")

        user_input = user_messages[-1]["content"].strip()
        if not user_input:
            raise HTTPException(status_code=400, detail="用户输入为空！")

        # ✅ 强制转换字符串编码
        user_input = user_input.encode("utf-8").decode("utf-8")

        print(f"📥 收到弹幕输入: {user_input}")

        # 调用 LLM 进行处理
        response = communicate_with_llm(user_input, API_KEY, WORKSPACE_SLUG)
        response = response.encode("utf-8").decode("utf-8")  # ✅ 确保返回也是 UTF-8

        # 计数聊天次数
        app.state.chat_count += 1
        print(app.state.chat_count, app.state.latest_doc_hash)
        # 每 1 次聊天上传一次历史记录
        if app.state.chat_count % 1 == 0:
            print("\n📝 1 次对话已完成，正在上传聊天记录...")
            try:
                upload_status, new_doc_hash = export_and_upload_chat_history(API_KEY, WORKSPACE_SLUG, TEMP_FILE, app.state.latest_doc_hash)
                print(f"✅AAA {upload_status}")

                # **更新最新的 Hash**
                app.state.latest_doc_hash = new_doc_hash

            except Exception as e:
                print(f"❌ 上传失败: {e}")


        print(f"📤 LLM 响应: {response}")

        # 组装 OpenAI Chat Completion API 兼容格式的返回值
        response_payload = {
            "id": "chatcmpl-123",  # 假设 ID，可根据需求修改
            "object": "chat.completion",
            "created": 1700000000,  # 生成时间戳
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(user_input),  # 粗略估算
                "completion_tokens": len(response),  # 粗略估算
                "total_tokens": len(user_input) + len(response)
            }
        }

        return response_payload

    except Exception as e:
        print(f"❌ 发生错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))
