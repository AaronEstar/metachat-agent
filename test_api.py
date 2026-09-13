import os
import requests
from dotenv import load_dotenv

# 加载 .env 配置
load_dotenv()

base_url = os.getenv("LLM_BASE_URL")
model = os.getenv("LLM_MODEL")
api_key = os.getenv("LLM_API_KEY")

# 检查配置是否完整
if not base_url:
    raise ValueError("缺少 LLM_BASE_URL 配置")

if not model:
    raise ValueError("缺少 LLM_MODEL 配置")

if not api_key:
    raise ValueError("缺少 LLM_API_KEY 配置")

url = f"{base_url.rstrip('/')}/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

payload = {
    "model": model,
    "messages": [
        {
            "role": "user",
            "content": "你好，请简单介绍一下你自己。",
        }
    ],
    "temperature": 0.7,
}

try:
    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=120,
    )

    print("HTTP 状态码:", response.status_code)

    if response.ok:
        result = response.json()
        answer = result["choices"][0]["message"]["content"]

        print("模型回答:")
        print(answer)
    else:
        print("接口返回内容:")
        print(response.text)

except requests.exceptions.Timeout:
    print("请求超时，请检查网络或接口地址。")

except requests.exceptions.RequestException as error:
    print("请求失败:", error)

except (ValueError, KeyError) as error:
    print("解析接口返回内容失败:", error)
