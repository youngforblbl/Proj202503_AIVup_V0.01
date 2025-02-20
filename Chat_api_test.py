import requests
import json

def communicate_with_llm(message, api_key, workspace_slug, mode='chat'):
    """
    与 AnythingLLM 的 API 进行交互，发送消息并获取回复。

    参数：
    - message (str): 要发送给 LLM 的消息。
    - api_key (str): 您的 AnythingLLM API 密钥。
    - workspace_slug (str): 工作区名称（应为小写字母）。
    - mode (str): 对话模式，可选 'chat' 或 'query'。默认为 'chat'。

    返回：
    - str: LLM 的回复消息。
    """
    # 定义请求头
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
        'accept': 'application/json'
    }

    # 构建请求数据
    json_data = {
        'message': message,
        'mode': mode,
    }

    # 发送 POST 请求
    response = requests.post(
        f'http://localhost:3001/api/v1/workspace/{workspace_slug}/chat',
        headers=headers,
        json=json_data
    )

    # 处理响应
    if response.status_code == 200:
        answer_dict = response.json()
        answer = answer_dict.get('textResponse', '')
        # 去除思考过程的标记
        final_answer = answer.split('</think>')[-1].strip()
        return final_answer
    else:
        raise Exception(f"请求失败，状态码：{response.status_code}, 响应内容：{response.text}")

