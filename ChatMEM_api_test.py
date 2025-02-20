import requests
import json
import re


def export_and_upload_chat_history(api_key, workspace_slug, temp_file='chat_history.json', previous_doc_hash=None):
    """
    导出聊天历史记录，并上传至 AnythingLLM 作为长期记忆，同时卸载上一轮的文档（如果有）。

    参数：
    - api_key (str): AnythingLLM 的 API 密钥。
    - workspace_slug (str): 工作区的标识符。
    - temp_file (str): 存储聊天记录的 JSON 文件路径。
    - previous_doc_hash (str): 上一次嵌入的文档 Hash，若无则为 None。

    返回：
    - str: 上传文档的响应信息 & 最新的文档 Hash
    """
    # 定义请求头
    headers = {
        'Authorization': f'Bearer {api_key}',
        'accept': 'application/json'
    }

    headers_json = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
        'accept': 'application/json'
    }

    # 1️⃣ **导出聊天历史记录**
    export_url = f'http://localhost:3001/api/v1/workspace/{workspace_slug}/chats'
    response = requests.get(export_url, headers=headers)

    if response.status_code == 200:
        chat_history = response.json()

        # **处理聊天记录**
        processed_history = []
        for message in chat_history.get('history', []):
            if 'role' in message and 'content' in message:
                role = message['role']
                content = message['content']

                # **删除 <think> ... </think>**
                if role == 'assistant':
                    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)

                processed_history.append({'role': role, 'content': content})

        # **保存 JSON 文件**
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(processed_history, f, ensure_ascii=False, indent=4)
        print(f"✅ 聊天历史记录已保存至 {temp_file}")

    else:
        return f"❌ 导出失败，状态码：{response.status_code}, 响应：{response.text}", None

    # 2️⃣ **上传文档**
    upload_url = "http://localhost:3001/api/v1/document/upload"
    files = {'file': open(temp_file, 'rb')}
    print(f"📤 上传文件: {temp_file}")
    response = requests.post(upload_url, headers=headers, files=files)

    if response.status_code == 200:
        response_data = response.json()
        file_locations = [doc['location'] for doc in response_data.get('documents', [])]
        print(f"✅ 文档上传成功, 获取文档 Hash 位置: {file_locations}")
    else:
        return f"❌ 文档上传失败. 状态码: {response.status_code}, 响应: {response.text}", None

    # 3️⃣ **更新嵌入**
    update_url = f'http://localhost:3001/api/v1/workspace/{workspace_slug}/update-embeddings'
    update_data = {"adds": file_locations, "deletes": [previous_doc_hash] if previous_doc_hash else []}

    response = requests.post(update_url, headers=headers_json, json=update_data)

    if response.status_code == 200:
        update_response = response.json()

        # **提取最新的嵌入文档 Hash**
        latest_doc_hash = None
        if 'workspace' in update_response and 'documents' in update_response['workspace']:
            docs = update_response['workspace']['documents']
            if docs:
                latest_doc_hash = docs[-1].get('docpath')  # 取最新文档的 docId 作为 Hash
                print(f"✅ 本次嵌入后文档 Hash 位置: {latest_doc_hash}")

        return (f"✅ 嵌入成功，最新文档 Hash: {latest_doc_hash}", latest_doc_hash) if latest_doc_hash else (
        "✅ 嵌入成功，但未找到文档 Hash", None)
    else:
        return f"❌ 嵌入更新失败，状态码: {response.status_code}, 响应: {response.text}", None
