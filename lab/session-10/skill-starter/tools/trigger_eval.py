#!/usr/bin/env python3
"""trigger_eval.py：測試 description 會不會在該觸發時觸發、不該觸發時保持安靜。

做法：把你的技能和幾個「鄰居技能」的 name 與 description 一起放進系統提示，
對每一句測試請求問模型「回答之前要先讀哪一個技能？」，重複 n 次，計算觸發率，
再和你標的 should_trigger 比對，得到精確率、召回率與 F1。

這是近似實驗。真實的 Claude 在更完整的脈絡裡決定是否讀取技能，結果會有差異；
但 description 的相對好壞，通常在這個簡化設定裡就看得出來。

用法：
    export ANTHROPIC_API_KEY=...
    python trigger_eval.py evals/mipvu-zh.triggers.json
    python trigger_eval.py evals/mipvu-zh.triggers.json --runs 5 --model claude-sonnet-5-5
    python trigger_eval.py evals/mipvu-zh.triggers.json --dry-run   # 只印出提示，不呼叫 API
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

DEFAULT_MODEL = "claude-haiku-5-5"

SYSTEM_TEMPLATE = """你是一個可以使用技能（skills）的助理。下面是目前可用的技能，每個只列出名稱與說明。
如果某個技能明顯有助於完成使用者的請求，你會在回答前先讀取它；如果沒有適用的技能，就直接回答。

<available_skills>
{skills}
</available_skills>

現在只需要做一件事：判斷回答下一則使用者訊息之前，要讀取哪一個技能。
只輸出一行 JSON，不要有其他文字：{{"skill": "技能名稱"}} 或 {{"skill": null}}"""


def read_description(skill_md: Path) -> tuple[str, str]:
    """從 SKILL.md 讀出 name 與 description（借用 skill_lint 的解析器）。"""
    sys.path.insert(0, str(Path(__file__).parent))
    from skill_lint import parse_frontmatter

    fm, _, err = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    if err:
        sys.exit(f"{skill_md}：{err}")
    return fm["name"], fm["description"]


def build_system(skills: list[dict]) -> str:
    rows = "\n".join(f"<skill><name>{s['name']}</name><description>{s['description']}</description></skill>" for s in skills)
    return SYSTEM_TEMPLATE.format(skills=rows)


def ask(client, model: str, system: str, query: str) -> str | None:
    msg = client.messages.create(
        model=model,
        max_tokens=60,
        system=system,
        messages=[{"role": "user", "content": query}],
    )
    text = "".join(b.text for b in msg.content if b.type == "text")
    m = re.search(r"\{.*\}", text, re.S)
    try:
        return json.loads(m.group(0)).get("skill") if m else None
    except json.JSONDecodeError:
        return None


def score(rows: list[dict]) -> dict:
    c = Counter()
    for r in rows:
        pred = r["rate"] >= 0.5
        c[("T" if pred == r["should_trigger"] else "F") + ("P" if pred else "N")] += 1
    p = c["TP"] / (c["TP"] + c["FP"]) if c["TP"] + c["FP"] else 0.0
    r = c["TP"] / (c["TP"] + c["FN"]) if c["TP"] + c["FN"] else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    return {**c, "precision": p, "recall": r, "f1": f1, "accuracy": (c["TP"] + c["TN"]) / len(rows)}


def main() -> int:
    ap = argparse.ArgumentParser(description="測試技能 description 的觸發表現")
    ap.add_argument("evalfile", type=Path)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--runs", type=int, default=3, help="每句重複幾次（預設 3）")
    ap.add_argument("--dry-run", action="store_true", help="只印出系統提示與第一句測試，不呼叫 API")
    args = ap.parse_args()

    spec = json.loads(args.evalfile.read_text(encoding="utf-8"))
    base = args.evalfile.parent
    name, desc = read_description((base / spec["skill_md"]).resolve())
    skills = [{"name": name, "description": desc}] + spec.get("neighbors", [])
    system = build_system(skills)

    if args.dry_run:
        print(system, "\n\n--- 第一句測試 ---\n", spec["queries"][0]["query"])
        return 0

    import anthropic  # pip install anthropic

    client = anthropic.Anthropic()
    rows = []
    for q in spec["queries"]:
        picks = [ask(client, args.model, system, q["query"]) for _ in range(args.runs)]
        rate = sum(p == name for p in picks) / args.runs
        rows.append({**q, "rate": rate, "picks": picks})
        ok = (rate >= 0.5) == q["should_trigger"]
        print(f"{'✓' if ok else '✗'} {rate:4.0%}  應{'觸發' if q['should_trigger'] else '安靜'}  {q['query']}")
        if not ok:
            others = Counter(p for p in picks if p != name)
            if others:
                print(f"         被選走的技能：{dict(others)}")

    s = score(rows)
    print(f"\n目標技能：{name}　模型：{args.model}　每句 {args.runs} 次")
    print(f"TP {s['TP']}  FP {s['FP']}  FN {s['FN']}  TN {s['TN']}")
    print(f"精確率 {s['precision']:.2f}　召回率 {s['recall']:.2f}　F1 {s['f1']:.2f}　正確率 {s['accuracy']:.2f}")

    out = args.evalfile.with_suffix(".results.json")
    out.write_text(json.dumps({"model": args.model, "runs": args.runs, "rows": rows, "score": s},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"逐句結果已存到 {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
