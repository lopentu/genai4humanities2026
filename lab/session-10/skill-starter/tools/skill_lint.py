#!/usr/bin/env python3
"""skill_lint.py：檢查一份 Agent Skill 的 SKILL.md。

檢查分三層，對應講義的色彩語法：

  句法（syntax）    規格層級的錯誤。不通過，技能就無法載入。
  語意（semantics） 內文結構是否讓程序、標籤、輸出格式可以被找到。
  語用（pragmatics）description 是否說清楚「何時用、何時不用」。

只有句法層會讓程式以非零狀態結束；語意與語用層是寫作建議。

用法：
    python skill_lint.py path/to/skill-folder
    python skill_lint.py path/to/skill-folder --json

規格依據：https://agentskills.io/specification
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    import yaml  # PyYAML；沒有安裝時改用下方的簡易解析
except ImportError:  # pragma: no cover
    yaml = None

ALLOWED_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
WHEN_CUES = re.compile(r"使用者|凡|每當|如果|若|時[，,、]|情況|whenever|use (this )?when|when the user", re.I)
BOUNDARY_CUES = re.compile(r"不用於|不適用|不要|勿用|避免|不處理|do not|don't|not for", re.I)
IMPERATIVE = re.compile(r"\bMUST\b|\bNEVER\b|\bALWAYS\b|務必|必須|一定要|絕對")
REASON = re.compile(r"因為|以免|理由|原因|because|so that", re.I)


@dataclass
class Finding:
    layer: str      # syntax / semantics / pragmatics
    level: str      # error / warn / ok
    message: str


def parse_frontmatter(text: str) -> tuple[dict | None, str, str | None]:
    """回傳 (frontmatter, body, 錯誤訊息)。"""
    if not text.startswith("---"):
        return None, text, "檔案第一行必須是 ---，YAML frontmatter 才會被辨認"
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.S)
    if not m:
        return None, text, "找不到結尾的 ---，frontmatter 沒有關上"
    raw, body = m.group(1), m.group(2)
    if yaml is not None:
        try:
            data = yaml.safe_load(raw)
        except yaml.YAMLError as e:
            hint = "；若 description 含半形冒號加空格（: ），請整段加上引號" if ": " in raw else ""
            return None, body, f"YAML 無法解析：{e.__class__.__name__}{hint}"
    else:
        data = _tiny_yaml(raw)
    if not isinstance(data, dict):
        return None, body, "frontmatter 必須是「鍵: 值」的對照表"
    return data, body, None


def _tiny_yaml(raw: str) -> dict:
    """沒有 PyYAML 時的退路：只處理單行的頂層鍵，以及 > 或 | 的區塊值。"""
    data, key, block = {}, None, []
    for line in raw.splitlines():
        if key and (line.startswith("  ") or not line.strip()):
            block.append(line.strip())
            continue
        if key:
            data[key] = " ".join(x for x in block if x)
            key, block = None, []
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if not m:
            continue
        k, v = m.group(1), m.group(2).strip()
        if v in (">", "|", ">-", "|-", ""):
            key = k
        else:
            data[k] = v.strip("\"'")
    if key:
        data[key] = " ".join(x for x in block if x)
    return data


def check_syntax(folder: Path, fm: dict | None, err: str | None) -> list[Finding]:
    out: list[Finding] = []
    add = lambda lvl, msg: out.append(Finding("syntax", lvl, msg))

    extra = [p for p in folder.rglob("SKILL.md") if p.parent != folder and "evals" not in p.parts]
    if extra:
        add("error", f"一個技能只能有一份 SKILL.md；多出的：{', '.join(str(p.relative_to(folder)) for p in extra)}")
    if err:
        add("error", err)
        return out

    unknown = set(fm) - ALLOWED_KEYS
    if unknown:
        add("error", f"frontmatter 有規格以外的鍵：{', '.join(sorted(unknown))}（自訂資訊請放在 metadata 底下）")

    name = fm.get("name")
    if not isinstance(name, str) or not name.strip():
        add("error", "缺少 name")
    else:
        name = name.strip()
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
            add("error", f"name「{name}」只能用小寫英文字母、數字與單一連字號，且不可以連字號開頭或結尾")
        if len(name) > 64:
            add("error", f"name 共 {len(name)} 個字元，上限 64")
        if name != folder.name:
            add("error", f"name「{name}」與資料夾名稱「{folder.name}」不同")

    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        add("error", "缺少 description，模型無從判斷何時使用這個技能")
    else:
        if len(desc) > 1024:
            add("error", f"description 共 {len(desc)} 個字元，上限 1024")
        if "<" in desc or ">" in desc:
            add("error", "description 不可含角括號 < >")

    if not any(f.level == "error" for f in out):
        add("ok", "frontmatter 符合規格")
    return out


def check_semantics(folder: Path, body: str) -> list[Finding]:
    out: list[Finding] = []
    add = lambda lvl, msg: out.append(Finding("semantics", lvl, msg))

    fences = re.findall(r"^\s*```", body, re.M)
    if len(fences) % 2:
        add("warn", "有一個程式碼區塊沒有關上（``` 的數量是奇數），之後的內容都會被當成程式碼")
    # 標題分析前先移除程式碼區塊，避免把樣板裡的 # 當成標題
    prose = re.sub(r"^\s*```.*?^\s*```", "", body, flags=re.S | re.M)
    heads = [(len(m.group(1)), m.group(2).strip()) for m in re.finditer(r"^(#{1,6})\s+(.+)$", prose, re.M)]

    h1 = [h for h in heads if h[0] == 1]
    if len(h1) != 1:
        add("warn", f"一級標題應恰好一個，目前 {len(h1)} 個")
    for (a, ta), (b, tb) in zip(heads, heads[1:]):
        if b > a + 1:
            add("warn", f"標題跳級：「{ta}」(H{a}) 之後直接接「{tb}」(H{b})")

    if not re.search(r"^\s*\d+\.\s+\S", prose, re.M):
        add("warn", "沒有編號清單；程序的步驟有先後，建議用 1. 2. 3.")
    if not re.search(r"^\s*\|.+\|\s*$\n^\s*\|?\s*:?-{3,}", prose, re.M):
        add("warn", "沒有表格；標註類技能通常需要一張標籤定義表")
    if not fences:
        add("warn", "沒有程式碼區塊；輸出格式最好給一個可照抄的樣板")
    if re.search(r"<!--", body) or re.search(r"^\s*[-*]\s*$|^\s*\d+\.\s*$|^\|(\s*\|)+\s*$", prose, re.M):
        add("warn", "還有樣板殘留：註解、空白清單項或空白表格列")

    for ref in sorted(set(re.findall(r"`((?:references|scripts|assets)/[^`\s]+)`", body))):
        if not (folder / ref).exists():
            add("warn", f"內文提到 {ref}，但檔案不存在")
        elif ref.count("/") > 1:
            add("warn", f"{ref} 超過一層目錄；規格建議參考檔只放一層深")

    n = body.count("\n") + 1
    if n > 500:
        add("warn", f"內文 {n} 行，超過建議的 500 行；長篇細則請移到 references/")

    if not out:
        add("ok", "內文結構完整：標題、程序、標籤表、輸出樣板都在")
    return out


def check_pragmatics(fm: dict | None, body: str) -> list[Finding]:
    out: list[Finding] = []
    add = lambda lvl, msg: out.append(Finding("pragmatics", lvl, msg))
    desc = (fm or {}).get("description")
    if not isinstance(desc, str) or not desc.strip():
        return out

    if len(desc) < 50:
        add("warn", f"description 只有 {len(desc)} 字；太短容易觸發不足，請補上使用者會說的話")
    if not WHEN_CUES.search(desc):
        add("warn", "description 只說了做什麼，沒說何時用；觸發條件是語用資訊，必須寫在這裡")
    if not BOUNDARY_CUES.search(desc):
        add("warn", "description 沒有寫不適用的情況；相鄰任務容易誤觸發")
    if re.search(r"(^|[，。、\s])我(會|可以|將)", desc):
        add("warn", "description 用了第一人稱；它會和其他技能並列在系統提示裡，建議用「本技能」或直接描述任務")

    imperatives = len(IMPERATIVE.findall(body))
    if imperatives >= 5 and not REASON.search(body):
        add("warn", f"內文有 {imperatives} 個強制語（必須、務必、MUST…）卻沒有任何理由；說明原因比加重語氣有效")

    if not out:
        add("ok", "description 同時說明了做什麼、何時用、何時不用")
    return out


def lint(folder: Path) -> list[Finding]:
    skill_md = folder / "SKILL.md"
    if not skill_md.exists():
        return [Finding("syntax", "error", f"{folder} 底下找不到 SKILL.md（檔名須全大寫）")]
    text = skill_md.read_text(encoding="utf-8")
    fm, body, err = parse_frontmatter(text)
    return check_syntax(folder, fm, err) + check_semantics(folder, body) + check_pragmatics(fm, body)


LAYER_ZH = {"syntax": "句法", "semantics": "語意", "pragmatics": "語用"}
MARK = {"error": "✗", "warn": "△", "ok": "✓"}


def main() -> int:
    ap = argparse.ArgumentParser(description="檢查 SKILL.md 的句法、語意與語用三層")
    ap.add_argument("folder", type=Path, help="技能資料夾（裡面要有 SKILL.md）")
    ap.add_argument("--json", action="store_true", help="以 JSON 輸出")
    args = ap.parse_args()

    findings = lint(args.folder.resolve())
    if args.json:
        print(json.dumps([asdict(f) for f in findings], ensure_ascii=False, indent=2))
    else:
        for layer in ("syntax", "semantics", "pragmatics"):
            group = [f for f in findings if f.layer == layer]
            if not group:
                continue
            print(f"\n【{LAYER_ZH[layer]}】")
            for f in group:
                print(f"  {MARK[f.level]} {f.message}")
        n_err = sum(f.level == "error" for f in findings)
        n_warn = sum(f.level == "warn" for f in findings)
        print(f"\n錯誤 {n_err}，建議 {n_warn}")
    return 1 if any(f.level == "error" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
