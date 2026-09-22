# tokfair — 中文 tokenization 公平性研究平台（分析層）

這個目錄是 `lab/session-9/zh-tokenizer.html` 背後的分析程式碼。
頁面上的每一個數字都由 `run_study.py` 產生，頁面本身不做任何計算，
因此展示與分析不會漂移。

## 為什麼要重做 v1

v1 比較「台灣繁體／中國簡體／香港繁體」三欄，把 token 數差異報成「方言稅」。
那個數字不可解釋，因為三欄同時變動兩個因子：

- **字形** 繁／簡 — 由 Unicode 碼位決定，是詞表**覆蓋率**問題
- **詞彙** 軟體／软件／軟件 — 由合併表決定，是字串**頻率**問題

拆開之後（37 個項目，項目內對比，配對 bootstrap 95% CI）：

```
cl100k_base   字形 繁−簡   +3.14 tok [+2.28, +4.17]  p < .001
              詞彙 台−中   +0.36 tok [−0.09, +0.86]  p = .166
              v1「方言稅」  +29.1%    [+18.4, +43.3]

o200k_base    字形 繁−簡   +1.60 tok [+1.22, +2.02]  p < .001
              詞彙 港−中   +0.49 tok [+0.18, +0.80]  p = .008
```

**那不是方言稅，是字形稅。** o200k 把字形效果壓到一半，
而詞彙效果反而變得可偵測——字形的雜訊小了，詞彙的訊號才浮出來。

機制是覆蓋率：`cl100k_base` 中有專屬 token 的簡體字，
其繁體對應字有 **92%** 沒有 token（反方向 0%），
因此每次出現都被拆成 2–3 個 UTF-8 位元組。

## 檔案

| 檔案 | 作用 |
|---|---|
| `minitok.py` | 離線的 tiktoken 相容編碼器。讀 `js-tiktoken` 的 rank 表，不需連網 |
| `stimuli.py` | 刺激庫與 2×3 完全交叉設計。詞彙欄人工撰寫，字形欄用 OpenCC 生成 |
| `metrics.py` | fertility、parity、byte-fallback rate、boundary F1、Rényi efficiency、成本換算 |
| `stats.py` | 配對 bootstrap、Wilcoxon 符號秩、rank-biserial、因子分解 |
| `vocab_audit.py` | 詞表考古：字形覆蓋不對稱、多字 token 的長度分布與內容 |
| `run_study.py` | 端到端執行，輸出 `data/study.json` |
| `build_web.py` | 把 `study.json` 注入頁面樣板，產生單一檔案的靜態頁 |
| `web/zh-tokenizer.template.html` | 頁面樣板，含 `__STUDY_DATA__` 佔位符 |
| `index.html` | 這個目錄在課程網站上的導覽頁 |
| `assignment1.html` | 延伸練習規格（網頁版） |
| `assignment1-tokenization-unfairness.md` | 同一份規格的 Markdown 原稿 |

## 安裝與執行

```bash
pip install regex opencc-python-reimplemented jieba numpy scipy
bash vendor_ranks.sh                      # 下載並解出離線 rank 表到 ranks/
python run_study.py                       # → data/study.json，並印出摘要
python build_web.py --out ../zh-tokenizer.html
```

`ranks/` 約 3.4 MB，已列入 `.gitignore`，由 `vendor_ranks.sh` 重建。
`data/study.json` 則入版控，這樣頁面與分析一定對得上。

## 已知限制

- 詞彙欄為作者自撰而非語料抽樣，不能推論到「一般文本」。
  要做那個推論，請改用維基百科 zh-tw／zh-cn／zh-hk 的自動轉換版本，
  或 FLORES-200 的 zho_Hant／zho_Hans 平行句對。
- 香港欄效度最弱。標記 `hk_confidence="low"` 的項目混入了書面粵語，
  那是語法差異而非詞彙差異，會污染詞彙效果的估計。需由香港母語者校訂。
- 只測兩個 OpenAI tokenizer。「誰訓練詞表」本身就是可測的變項（見作業 A1）。
- token 數差異與下游表現差異是兩件事。這裡只量前者。
- `metrics.py` 中的價格與 context 長度是**佔位值**，引用前請更新。
- 所有文獻引用是憑記憶寫的，**尚未查核**。寫進報告前請逐條確認。
