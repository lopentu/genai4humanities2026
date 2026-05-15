# Heartbeat

## 設定

```yaml
profile: research_companion
interval_sec: 60
enabled: true
```

## 實作

```python
import time
from typing import Callable

class Heartbeat:
    def __init__(self, interval_sec: float = 60.0):
        self.interval = interval_sec
        self.tick_count = 0
        self.subscribers: list[Callable] = []

    def subscribe(self, callback: Callable[[int], None]):
        self.subscribers.append(callback)

    def beat(self):
        self.tick_count += 1
        for callback in self.subscribers:
            try:
                callback(self.tick_count)
            except Exception as e:
                print(f"[Heartbeat] subscriber failed: {e}")

    def run_forever(self):
        while True:
            self.beat()
            time.sleep(self.interval)
```

## 訂閱者

```python
hb = Heartbeat(interval_sec=60.0)

# 環境感知（每跳）
hb.subscribe(lambda t: env_monitor.check_inbox())

# 記憶整理（每 10 分鐘）
hb.subscribe(
    lambda t: memory_consolidator.run() if t % 10 == 0 else None
)

# 長期記憶歸檔（每 1 小時）
hb.subscribe(
    lambda t: long_term_archiver.archive() if t % 60 == 0 else None
)

# 自我狀態檢查（每跳）
hb.subscribe(lambda t: self_diagnostic.check())
```

## 時間自我模型

```python
class TemporalSelfModel:
    def __init__(self):
        self.birth_time = time.time()
        self.last_user_interaction = None
        self.tick_count = 0

    def on_heartbeat(self, tick: int):
        self.tick_count = tick

    @property
    def age_seconds(self) -> float:
        return time.time() - self.birth_time

    @property
    def time_since_user(self) -> float | None:
        if self.last_user_interaction is None:
            return None
        return time.time() - self.last_user_interaction
```

## 關閉模式

```yaml
shutdown_modes:
  pause:
    recoverable: true
    state_preserved: full

  hibernate:
    recoverable: true
    state_preserved: serialized

  terminate:
    recoverable: false
    state_preserved: none
```
