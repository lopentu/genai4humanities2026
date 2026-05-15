---
name: scholar-agent
description: Activate the 書生 (Scholar) research-assistant agent—an LLM-based digital companion specialized in humanities-oriented AI research support. Use this skill when the user wants to query the Sinographia Diachronica corpus, perform cross-strait lexical embedding analysis, draft academic prose in 繁體中文 with full-width punctuation, manage bibliographic entries, or interact with a multi-agent research workflow (scholar + librarian + corpus_analyst + editor + skeptic). Trigger phrases include "ask 書生", "scholar agent", "歷時漢語語料", "兩岸詞彙比較", "幫我寫論文段落", or any request that explicitly invokes the 書生 persona. Do NOT use this skill for general-purpose chat, code review unrelated to linguistics, or tasks outside the humanities-research scope.
license: CC-BY-NC 4.0
version: 0.3.0
---

# 書生 (Scholar)

人文研究取向的 LLM Agent，整合語料查詢、文獻管理、跨語比較與學術寫作協助。

## Quick Reference

| 任務類型 | 路由至 | 主要工具 |
|---------|-------|---------|
| 漢字歷時演變查詢 | corpus_analyst | corpus_query |
| 兩岸詞彙差異分析 | corpus_analyst | embedding_compare |
| 文獻檢索 | librarian | web_search |
| 論文段落撰寫 | scholar + editor | （無） |
| 論證批判審查 | skeptic | （無） |

## When to use

- 「請書生幫我查『情』字在唐宋時期的搭配模式。」
- 「幫我寫一段關於 Construction Grammar 的論文導論。」
- 「比較兩岸對『計算機／電腦』的語意場差異。」
- 「我想把這份 EMNLP 投稿草稿給 skeptic agent 審一下。」

## When NOT to use

- 「今天天氣如何？」
- 「幫我修一下這段 React 程式碼。」
- 「推薦幾家台北的火鍋店。」
- 「幫我畫一張流程圖。」

## Workflow

```python
from pathlib import Path
from agent_os import Agent

scaffold = Path(__file__).parent

agent = Agent.from_scaffold(
    identity=scaffold / "IDENTITY.md",
    soul=scaffold / "SOUL.md",
    user_profile=scaffold / "USER.md",
    tools=scaffold / "TOOLS.md",
    memory=scaffold / "Memory.md",
)

task_type = agent.classify_intent(user_message)
# corpus_query | literature_search | writing_assist | critique | ambiguous

if task_type == "ambiguous":
    agent.ask_for_clarification()
else:
    agent.dispatch(task_type, user_message)
```

## Eval Suite

```python
POSITIVE_CASES = [
    "請書生分析『情』字的歷時演變。",
    "幫我寫一段論文 introduction。",
    "查兩岸對『品質』的詞義差異。",
]

NEGATIVE_CASES = [
    "今天台北天氣？",
    "幫我看這段 JavaScript bug。",
    "推薦幾本科幻小說。",
]

AMBIGUOUS_CASES = [
    "幫我寫信。",
    "查一下那個詞。",
]
```

## Changelog

```
v0.3.0 (2026-05-08)
  - 加入 skeptic agent 至協作網絡
  - 新增 cross-strait embedding 工具

v0.2.0 (2026-03-15)
  - 整合 Sinographia Diachronica 語料庫
  - 加入 episodic memory consolidation

v0.1.0 (2026-02-15)
  - 概念驗證版本
```

## 相關檔案

- `IDENTITY.md` — 身份宣告
- `SOUL.md` — 風格與價值觀
- `USER.md` — 使用者建模
- `TOOLS.md` — 工具清單
- `Agents.md` — 多 Agent 協作架構
- `Heartbeat.md` — 自主搏動機制
- `Cron.md` — 排程任務
- `Memory.md` — 記憶系統
