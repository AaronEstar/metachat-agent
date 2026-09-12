import json
import os
from datetime import datetime

import requests
from dotenv import load_dotenv


load_dotenv()

BASE_URL = os.getenv("LLM_BASE_URL")
MODEL = os.getenv("LLM_MODEL")
API_KEY = os.getenv("LLM_API_KEY")

if not BASE_URL:
    raise ValueError("未配置 LLM_BASE_URL")

if not MODEL:
    raise ValueError("未配置 LLM_MODEL")

if not API_KEY:
    raise ValueError("未配置 LLM_API_KEY")


# 确保地址以 /v1/chat/completions 结尾
if BASE_URL.endswith("/"):
    BASE_URL = BASE_URL[:-1]

if not BASE_URL.endswith("/v1/chat/completions"):
    API_URL = BASE_URL + "/v1/chat/completions"
else:
    API_URL = BASE_URL


headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


# 保存完整对话上下文
messages = [
    {
        "role": "system",
        "content": "你是一个友好、准确、有帮助的中文 AI 助手。",
    }
]

chat_history = []


def ask_ai():
    """将完整上下文发送给 AI"""

    data = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=data,
        timeout=120,
    )

    response.raise_for_status()

    result = response.json()
    answer = result["choices"][0]["message"]["content"]

    return answer


def show_history():
    """显示本次运行中的聊天记录"""

    if not chat_history:
        print("当前还没有聊天记录。\n")
        return

    print("\n===== 聊天记录 =====")

    for item in chat_history:
        print(f"\n[{item['time']}]")
        print(f"你：{item['user']}")
        print(f"AI：{item['assistant']}")

    print("\n====================\n")


def show_help():
    """显示可用命令"""

    print("""
可用命令：

  help       查看帮助
  history    查看本次聊天记录
  model      查看当前使用的模型
  clear      清空当前对话上下文
  exit       保存记录并退出
""")

def show_model():
    """显示当前模型和 API 地址"""

    print(f"\n当前模型：{MODEL}")
    print(f"API 地址：{API_URL}\n")


    with open("chat_history.json", "w", encoding="utf-8") as file:
        json.dump(chat_history, file, ensure_ascii=False, indent=2)


print("MetaChat Agent 已启动")
print("输入 help 查看命令")
print("输入 exit 退出，输入 clear 清空当前对话")
print("-" * 50)


while True:
    try:
        user_input = input("你：").strip()

        if not user_input:
            continue

        command = user_input.lower()

        if command == "exit":
            save_history()
            print("聊天记录已保存，聊天结束。")
            break

        if command == "help":
            show_help()
            continue

        if command == "history":
            show_history()
            continue

        if command == "model":
            show_model()
            continue

        if command == "clear":
            messages = [
                {
                    "role": "system",
                    "content": "你是一个友好、准确、有帮助的中文 AI 助手",
                }
            ]
            print("当前对话上下文已清空。\n")
            continue

        messages.append({
            "role": "user",
            "content": user_input,
        })

        try:
            answer = ask_ai()

            messages.append({
                "role": "assistant",
                "content": answer,
            })

            chat_history.append({
                "time": datetime.now().isoformat(timespec="seconds"),
                "user": user_input,
                "assistant": answer,
            })

            print(f"\nAI：{answer}\n")

        except requests.exceptions.Timeout:
            messages.pop()
            print("请求超时，请检查网络后重试。\n")

        except requests.exceptions.RequestException as error:
            messages.pop()
            print(f"API 请求失败：{error}\n")

        except (KeyError, IndexError, TypeError, ValueError):
            messages.pop()
            print("API 返回格式异常，请检查模型接口配置。\n")

    except KeyboardInterrupt:
        save_history()
        print("\n聊天记录已保存，聊天结束。")
        break
