from pathlib import Path
import os
from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

client = OpenAI(
    api_key=os.environ["METACHAT_API_KEY"],
    base_url=os.environ["METACHAT_BASE_URL"].rstrip("/"),
)

report_file = ROOT / "docs/ai-reports/latest-review.md"

if not report_file.exists():
    raise FileNotFoundError(f"找不到报告：{report_file}")

report = report_file.read_text(encoding="utf-8", errors="ignore")

prompt = f"""
你是专业 KiCad PCB 工程师。

请根据以下审查报告生成 PCB 修改计划。

要求：
1. 只提出修改计划，不直接修改文件；
2. 每项包含：编号、文件、位置、问题、修改动作、风险、验证方法；
3. 区分“可以自动执行”和“必须人工确认”；
4. 不得虚构器件、网络或坐标；
5. 不确定内容标记为“待确认”；
6. 输出 Markdown。

审查报告：
{report}
"""

response = client.chat.completions.create(
    model=os.environ["METACHAT_MODEL"],
    temperature=0,
    messages=[
        {"role": "system", "content": "你是可靠的 PCB 设计审查工程师。"},
        {"role": "user", "content": prompt},
    ],
)

content = response.choices[0].message.content or ""

output = ROOT / "docs/ai-reports/pcb-change-plan.md"
output.write_text(content, encoding="utf-8")

print(f"修改计划已生成：{output}")
