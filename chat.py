import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv("LLM_BASE_URL")
model = os.getenv("LLM_MODEL")
api_key = os.getenv("LLM_API_KEY")

if not base_url or not model or not api_key:
    raise ValueError("请检查 .env 中的配置")

url = f"{base_url.rstrip('/')}/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

history_file = "chat_history.json"

default_messages = [
    {
        "role": "system",
        "content": "你是一个有帮助的中文 AI 助手。",
    }
]


def load_history():
    if not os.path.exists(history_file):
        return default_messages.copy()

    try:
        with open(history_file, "r", encoding="utf-8") as file:
            messages = json.load(file)

        if isinstance(messages, list) and messages:
            return messages

    except (json.JSONDecodeError, OSError):
        print("聊天记录读取失败，将开始新的对话。")

    return default_messages.copy()


def save_history(messages):
    try:
        with open(history_file, "w", encoding="utf-8") as file:
            json.dump(messages, file, ensure_ascii=False, indent=2)
    except OSError as error:
        print(f"聊天记录保存失败：{error}")


messages = load_history()

print("聊天程序已启动。输入 exit 或 quit 退出。")
print("输入 clear 清空当前聊天记录。")
print("-" * 50)

while True:
    user_input = input("\n你：").strip()

    if user_input.lower() in {"exit", "quit"}:
        save_history(messages)
        print("聊天记录已保存，聊天结束。")
        break

    if user_input.lower() == "clear":
        messages = default_messages.copy()
        save_history(messages)
        print("当前聊天记录已清空。")
        continue

    if not user_input:
        continue

    messages.append({
        "role": "user",
        "content": user_input,
    })

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=120,
        )

        if not response.ok:
            print(f"\n请求失败（HTTP {response.status_code}）：")
            print(response.text)
            messages.pop()
            continue

        result = response.json()
        answer = result["choices"][0]["message"]["content"]

        print(f"\nAI：{answer}")

        messages.append({
            "role": "assistant",
            "content": answer,
        })

        save_history(messages)

    except requests.exceptions.Timeout:
        print("\n请求超时。")
        messages.pop()

    except requests.exceptions.RequestException as error:
        print(f"\n网络请求失败：{error}")
        messages.pop()

    except (ValueError, KeyError, IndexError) as error:
        print(f"\n解析接口返回内容失败：{error}")
        messages.pop()
