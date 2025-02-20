import requests
import os

api_url = f"http://localhost:3001/api/v1/document/upload"
api_key = '[你的anythingllm API_key]'
headers = {
    "Authorization": f'Bearer {api_key}',
    "accept": "application/json"
}

pdf_filename = "test_pdf.pdf"
files = {'file': open(pdf_filename, 'rb')}
print(f"Sending files: {pdf_filename}")
response = requests.post(api_url, headers=headers, files=files)
if response.status_code == 200:
    print(f"PDF successfully uploaded to the API, Response: {response.text}")
else:
    print(f"Failed. Status code: {response.status_code}, Response: {response.text}")

# location:custom-documents/test_pdf.pdf-e143a6df-db15-40a2-b2b0-80876cac963a.json