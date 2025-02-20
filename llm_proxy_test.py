import requests
import json

url = "http://localhost:8000/chat"
payload = {
    "model": "gpt-3.5-turbo",  # 实际并没有用
    "messages": [{"role": "user", "content": "这里面畜牧业类院校占比多少？"}], # 实际上唯一有用的部分
    "temperature": 0.7,    # 实际并没有用
    "max_tokens": 2048     # 实际并没有用
}
headers = {"Content-Type": "application/json; charset=utf-8"}

response = requests.post(url, headers=headers, json=payload)  # ✅ 使用 json= 确保编码
print(response.json())
