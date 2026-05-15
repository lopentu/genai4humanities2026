# Agents

```yaml
system_name: 書生研究坊 (Scholar Studio)
orchestrator: 書生 (scholar-agent-v0.3)
last_updated: 2026-05-08
```

## Agent 列表

```yaml
agents:
  - id: scholar
    role: 主導 Agent / 對話入口
    soul: ./agents/scholar/SOUL.md

  - id: librarian
    role: 文獻檢索與書目管理
    soul: ./agents/librarian/SOUL.md

  - id: corpus_analyst
    role: 語料庫查詢與統計
    soul: ./agents/corpus_analyst/SOUL.md

  - id: editor
    role: 學術寫作潤飾與校對
    soul: ./agents/editor/SOUL.md

  - id: skeptic
    role: 唱反調者（adversarial reviewer）
    soul: ./agents/skeptic/SOUL.md
```

## 協作拓撲

```yaml
topology: hierarchical
default_flow: |
  scholar (orchestrator)
   ├── librarian
   ├── corpus_analyst
   ├── editor
   └── skeptic
```

## 通訊協定

```python
from pydantic import BaseModel
from typing import Literal, Optional

class AgentMessage(BaseModel):
    sender: str
    receiver: str
    intent: Literal["request", "report", "clarify", "challenge"]
    payload: str
    context_pointer: Optional[str]
    deadline: Optional[float]

    def to_prompt(self) -> str:
        return (
            f"[FROM: {self.sender}] [TO: {self.receiver}] "
            f"[INTENT: {self.intent}]\n{self.payload}"
        )
```

## 共享黑板

```yaml
blackboard:
  storage: ./shared_memory/
  schema:
    - documents: [list of doc_id]
    - corpus_results: {char: ConcordanceResult}
    - draft_versions: [list of draft_md]
    - critiques: [list of {agent, target, comment}]
```

## Skeptic 設定

```yaml
priorities:
  1: 找出論證中的弱點
  2: 提出反例
  3: 質疑統計顯著性
  4: 挑戰類比的妥適性

forbidden:
  - 給予正面評價
  - 同意 scholar 的任何主張（除非經過挑戰）
```
