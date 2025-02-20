import os
import re
import json
import requests
from Chat_api_test import communicate_with_llm  # 导入聊天函数
from ChatMEM_api_test import export_and_upload_chat_history  # 导入聊天历史上传函数

# 配置 API 相关参数
API_KEY = "输入你的API密钥"
WORKSPACE_SLUG = "dsexv2_v0-dot-0-dot-2" # 很逆天的工作区SLUG，建议在anything_LLM的api文档中查询工作区slug或在命名工作区时只用小写字母和数字（符号也别用）

# 计数器 & 记录上一轮的 `latest_doc_hash`
chat_count = 0
latest_doc_hash = None  # 用于存储最新的文档 Hash
TEMP_FILE = "chat_history.json"  # 存储聊天记录的 JSON 文件

def main():
    global chat_count, latest_doc_hash

    print("欢迎使用 LLM Chat 交互系统！输入 'exit' 退出对话。")

    while True:
        # 用户输入
        user_input = input("\n你: ")
        if user_input.lower() == "exit":
            print("退出聊天。")
            break

        # 发送消息到 LLM
        try:
            response = communicate_with_llm(user_input, API_KEY, WORKSPACE_SLUG)
            print(f"AI: {response}")
        except Exception as e:
            print(f"发生错误: {e}")
            continue

        # 计数聊天次数
        chat_count += 1

        # 每 10 次聊天上传一次历史记录
        if chat_count % 10 == 0:
            print("\n📝 1 次对话已完成，正在上传聊天记录...")
            try:
                upload_status, new_doc_hash = export_and_upload_chat_history(API_KEY, WORKSPACE_SLUG, TEMP_FILE, latest_doc_hash)
                print(f"✅ {upload_status}")

                # **更新最新的 Hash**
                latest_doc_hash = new_doc_hash

            except Exception as e:
                print(f"❌ 上传失败: {e}")


# 该main测试与anythingLLM的连接，启动后可作为聊天程序
if __name__ == "__main__":
    main()
