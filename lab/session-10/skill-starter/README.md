# Session 10 起手包：用 Markdown 寫 Skill

```
skill-starter/
├── mipvu-zh/                     範例技能：中文隱喻標註（簡化 MIPVU）
│   ├── SKILL.md
│   └── references/
│       ├── guideline.md          中文切分與判定細則
│       └── examples.md           十個已標註例句與常見分歧
├── templates/
│   └── SKILL.template.md         空白樣板
└── tools/
    ├── skill_lint.py             檢查句法、語意、語用三層
    ├── trigger_eval.py           測試 description 的觸發表現
    └── evals/
        └── mipvu-zh.triggers.json
```

## 三個步驟

**1. 建立資料夾。** 資料夾名稱就是技能的 `name`，只能用小寫英文、數字與連字號。

```bash
mkdir -p my-annotation-skill
cp templates/SKILL.template.md my-annotation-skill/SKILL.md
```

**2. 寫完之後檢查。** 只需要 Python 3.9 以上；裝了 PyYAML 會解析得更嚴格。

```bash
python tools/skill_lint.py my-annotation-skill
```

句法層出現 ✗ 代表技能無法載入，必須修正；語意與語用層的 △ 是寫作建議。

**3. 測試觸發。** 複製 `tools/evals/mipvu-zh.triggers.json`，把 `skill_md` 指向你的技能，改寫 `queries`。至少 10 句，其中至少 4 句是不應觸發的鄰近任務。

```bash
pip install anthropic
export ANTHROPIC_API_KEY=...
python tools/trigger_eval.py tools/evals/my-annotation-skill.triggers.json --dry-run   # 先看提示
python tools/trigger_eval.py tools/evals/my-annotation-skill.triggers.json --runs 3
```

`--dry-run` 不呼叫 API，沒有金鑰也能用來檢查提示內容。

## 繳交

見 Lab 主頁「繳交與討論」一節。
