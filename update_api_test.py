import requests
import os

api_url = f"http://localhost:3001/api/v1/document/upload"
api_key = '6EP8W3J-66CMJ74-MKWXQ9F-YWH94P4'
headers = {
    'Content-Type': 'application/json',
    "Authorization": f'Bearer {api_key}',
    "accept": "application/json"
}
workspace_slug = 'anythingllm_test'

# 更新嵌入
add_file = "custom-documents/test_pdf.pdf-e143a6df-db15-40a2-b2b0-80876cac963a.json"
print(f"开始更新{add_file}")
update_data = {      # 构建 update-embeddings 请求数据
    "adds": [add_file],     # 添加的文档路径
    "deletes": []         # 要删除的文档路径列表
}

update_url = f'http://localhost:3001/api/v1/workspace/{workspace_slug}/update-embeddings'
headers['Content-Type'] = 'application/json'
response = requests.post(update_url, headers=headers, json=update_data)

    # 删除临时文件
    # os.remove(temp_file)

if response.status_code == 200:
    print(f"嵌入更新成功，响应内容：{response.json()}")
else:
    print(f"嵌入更新失败，状态码：{response.status_code}, 响应内容：{response.text}")