# Memory

## 架構

```yaml
layers:
  sensory_buffer:
    scope: 當前 prompt tokens
    duration: 毫秒級

  short_term:
    scope: 當前對話 context window
    duration: 分鐘級

  long_term:
    types: [episodic, semantic, procedural]
    duration: 天 / 週 / 年級
    storage: ./memory_store/
```

## Episodic Memory

```yaml
schema:
  id: episode_uuid
  timestamp: ISO8601
  participants: [user_id]
  summary: str (≤ 500 tokens)
  raw_pointer: str
  tags: [str]
  emotional_valence: float (-1 to 1)

backend: chromadb
embedding_model: nomic-embed-text
```

## Semantic Memory

```yaml
schema:
  concept: str
  definition: str
  aliases: [str]
  relations:
    - {type: "is_a", target: concept}
    - {type: "part_of", target: concept}
    - {type: "related_to", target: concept}
  sources: [episode_id]
  confidence: float

backend: networkx
storage_format: graphml
```

## Procedural Memory

```yaml
schema:
  trigger_pattern: str
  action_template: str
  learned_from: [episode_id]
  reinforcement_count: int
  last_used: timestamp
```

## Consolidation

```python
def consolidate(short_term: list[Message], llm: LLM) -> ConsolidationResult:
    episodes = llm.extract(
        short_term,
        prompt="識別此對話中值得長期記憶的事件，每件事描述為一句話。"
    )

    concepts = llm.extract(
        short_term,
        prompt="識別此對話中出現的新概念或對既有概念的新理解。"
    )

    procedures = llm.extract(
        short_term,
        prompt="識別此對話中使用者顯露的偏好或行為規則。"
    )

    return ConsolidationResult(
        episodic=episodes,
        semantic=concepts,
        procedural=procedures
    )
```

## Retrieval

```python
def retrieve(query: str, k: int = 3) -> list[Memory]:
    candidates = vector_db.search(query, top_k=20)
    reranked = cross_encoder.rerank(query, candidates)
    return reranked[:k]
```

## Forgetting

```yaml
forgetting_strategies:
  decay:
    formula: importance(t) = importance(0) * exp(-t/τ)
    default_tau_days: 90

  redundancy_pruning:
    similarity_threshold: 0.92

  user_initiated:
    irreversible: true

  tag_based_purge:
    tags: [outdated, experimental, sensitive]
```
