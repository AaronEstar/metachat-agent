import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "docs" / "ai-reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(ROOT / ".env")

client = OpenAI(
    api_key=os.environ["METACHAT_API_KEY"],
    base_url=os.environ["METACHAT_BASE_URL"].rstrip("/"),
)

model = os.environ["METACHAT_MODEL"]

def run_command(command):
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result.stdout + "\n" + result.stderr
    except Exception as e:
        return f"执行失败：{e}"

def read_file(path, limit=30000):
    if not path.exists():
        return f"文件不存在：{path.name}"
    return path.read_text(encoding="utf-8", errors="ignore")[:limit]

def main():
    project = ROOT / "DSP_Controller.kicad_pro"
    schematic = ROOT / "DSP_Controller.kicad_sch"
    pcb = ROOT / "DSP_Controller.kicad_pcb"

    kicad_cli = os.getenv("KICAD_CLI", "kicad-cli")

    erc = run_command([
        kicad_cli, "sch", "erc",
        "-o", str(REPORT_DIR / "erc.rpt"),
        str(schematic),
    ])

    drc = run_command([
        kicad_cli, "pcb", "drc",
        "-o", str(REPORT_DIR / "drc.rpt"),
        str(pcb),
    ])

    pinmap = read_file(ROOT / "interface" / "pinmap.yaml")
    erc_report = read_file(REPORT_DIR / "erc.rpt")
    drc_report = read_file(REPORT_DIR / "drc.rpt")

    prompt = f"""
你是专业的 KiCad 硬件工程师，请审查以下工程资料。

要求：
1. 分析原理图结构和主要功能模块；
2. 分析 PCB 结构、器件和网络；
3. 分析 ERC 报告；
4. 分析 DRC 报告；
5. 对比 pinmap.yaml；
6. 输出发现的问题、风险和修改建议；
7. 不要直接修改文件；
8. 不确定的内容必须标记“待确认”；
9. 引用具体文件、器件编号或网络名称。

请使用 Markdown 输出，按以下结构：
# 工程审查报告
## 1. 总体结论
## 2. 原理图问题
## 3. PCB问题
## 4. ERC问题
## 5. DRC问题
## 6. 引脚映射问题
## 7. 修改建议
## 8. 必须人工确认的项目

pinmap.yaml：
{pinmap}

ERC执行结果：
{erc}

ERC报告：
{erc_report}

DRC执行结果：
{drc}

DRC报告：
{drc_report}

原理图文件摘要：
{read_file(schematic, 20000)}

PCB文件摘要：
{read_file(pcb, 20000)}
"""

    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "你是可靠的电子硬件设计审查工程师。",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    output = REPORT_DIR / "latest-review.md"
    output.write_text(
        response.choices[0].message.content,
        encoding="utf-8",
    )

    print(f"分析完成：{output}")

if __name__ == "__main__":
    main()
