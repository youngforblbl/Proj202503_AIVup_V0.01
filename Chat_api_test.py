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

# 主程序示例
if __name__ == '__main__':
    # 设置 API 密钥和工作区名称
    API_KEY = '6EP8W3J-66CMJ74-MKWXQ9F-YWH94P4'
    WORKSPACE_SLUG = 'anythingllm_test'  # 请确保为小写字母

    # 从用户输入获取消息
    user_message = input("请输入要发送的消息：")

    try:
        # 调用函数获取 LLM 的回复
        llm_response = communicate_with_llm(user_message, API_KEY, WORKSPACE_SLUG)
        print("LLM 的回复：", llm_response)
    except Exception as e:
        print("发生错误：", str(e))
