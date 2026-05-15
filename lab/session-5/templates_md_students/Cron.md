# Cron

```yaml
agent: scholar-agent-v0.3
timezone: Asia/Taipei
last_updated: 2026-05-08
```

## 排程任務

```yaml
scheduled_tasks:

  - name: weekly_report
    schedule: "0 9 * * 1"
    description: 整理上週對話與專案進展，生成週報
    handler: tasks.weekly_report.generate
    output: ./reports/{YYYY-WW}.md
    notify: scholar.shu@ntu.edu.tw

  - name: memory_consolidation
    schedule: "0 3 * * *"
    description: 將 short-term memory 整理進 long-term store
    handler: tasks.memory.consolidate

  - name: literature_alert
    schedule: "0 8 * * 2,5"
    description: 檢查 arXiv 與 ACL Anthology 的新論文
    handler: tasks.alerts.check_arxiv
    keywords: [computational linguistics, semantic shift, LLM interpretability]

  - name: birthday_reminder
    schedule: "0 7 * * *"
    description: 檢查是否有需要的紀念日提醒
    handler: tasks.calendar.check_birthdays

  - name: deep_clean
    schedule: "0 4 1 * *"
    description: 清理過期快取、壓縮日誌
    handler: tasks.maintenance.deep_clean
```

## Handler 範例

```python
from datetime import datetime, timedelta
from pathlib import Path

def generate(context: AgentContext) -> Path:
    today = datetime.now()
    iso_year, iso_week, _ = today.isocalendar()
    output_path = Path(f"./reports/{iso_year}-W{iso_week:02d}.md")

    if output_path.exists():
        return output_path

    week_ago = today - timedelta(days=7)
    convs = context.memory.query_conversations(since=week_ago)

    summary = context.llm.summarize(
        convs,
        prompt="生成本週重點，使用繁體中文，以類比、公式、實例的順序組織。"
    )

    output_path.write_text(summary, encoding="utf-8")
    return output_path
```

## 失敗處理策略

```yaml
overlap_policy:
  default: skip
  options:
    - skip:    上次未完成則跳過此次
    - queue:   排入佇列依序執行
    - kill:    終止上次執行此次

retry_policy:
  max_attempts: 3
  backoff: exponential
  base_delay_sec: 60
```
