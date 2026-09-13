import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / ".env"

load_dotenv(ENV_FILE)

api_key = os.getenv("METACHAT_API_KEY")
base_url = os.getenv("METACHAT_BASE_URL")
model = os.getenv("METACHAT_MODEL")

if not api_key or api_key.startswith("请在这里"):
    raise RuntimeError("请先在 .env 中填写 METACHAT_API_KEY")

if not base_url:
    raise RuntimeError("缺少 METACHAT_BASE_URL")

if not model:
    raise RuntimeError("缺少 METACHAT_MODEL")

client = OpenAI(
    api_key=api_key,
    base_url=base_url.rstrip("/"),
)

response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "system",
            "content": "你是专业的电子硬件和嵌入式软件工程助手。",
        },
        {
            "role": "user",
            "content": "请只回复：MetaChat API 连接成功。",
        },
    ],
    temperature=0,
)

print(response.choices[0].message.content)
