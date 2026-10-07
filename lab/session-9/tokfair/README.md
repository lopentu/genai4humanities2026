# tokfair v3 — 中文 Tokenization 實驗工作台

v3 將字串切分、成本情境與公平性論證分開。原始 37 個項目保留，篩選理由與資料驗證公開。這是自撰材料的探索研究，沒有母語者校訂、真實語料抽樣或下游模型評測。

## 分析範圍

| 範圍 | n | 條件 | 解讀 |
|---|---:|---|---|
| twcn_screened | 29 | 台中 2×2 | 排除 8 個額外措辭、指涉或跨地區模板風險項目；作者篩選，非人工 gold |
| twcn_all | 37 | 台中 2×2 | 保留原始項目，作敏感度比較 |
| hk_nonlow | 28 | 三地 2×3 | 排除香港 low 信心項目，仍未驗證 |
| hk_all | 37 | 三地 2×3 | 混入書面粵語與指涉差異，僅作探索 |
| controls | 3 | 三地 2×3 | 每種字形下三欄字串完全相同，詞彙對比精確為零 |

新聞類整體不是控制組。OpenCC 字形轉換是操作性定義，不能保證語義或社會語言學等價；未使用同時轉換台灣用詞的 `s2twp`。`original_surface` 表示作者原始版本，不代表 corpus attestation。歷史欄位 `attested` 已移除。

## 安裝與重現

使用 Python 3.11 以上。第一次取得 rank 表需 Node/npm 與網路，之後普通文字測量可離線執行。

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
bash vendor_ranks.sh
python run_study.py
python validate.py
python build_web.py --out ../zh-tokenizer.html
```

`validate.py` 第一次可能下載官方 tiktoken rank 表；比對完整 rank 表、874 個文字編碼案例（含隨機文字）、所有 444 格測量、位元組重建、控制差為零、基準路徑恆等式。只確認普通文字編碼；不是完整 special-token API 相容性宣告。報告見 `data/validation.json`。

資料記錄 Python / 套件版本、bootstrap seed / 次數、rank SHA-256、分析原始碼 SHA-256，以及來源基底 commit。基底 commit 是執行當時 HEAD，不宣稱包含未提交的修改；source hash 才是該次分析的程式識別。

瀏覽器即時 tokenizer 使用網站內 `assets/tokenizer/tokenizer.mjs`，按需下載，沒有外部 CDN。重建：

```bash
cd assets/tokenizer
npm ci
npm run build
```

## 指標與推論

- `n_tokens`：全部文字的 token 數，包括標點與空白。
- `tokens_per_han`：n_tokens / 漢字數；混排文字的分子仍包含非漢字。
- `tokens_per_codepoint`：n_tokens / Unicode 碼位數，含標點與空白；不是 grapheme count。
- `n_utf8_fragments`：單獨無法解碼成有效 UTF-8 的 token 數。直接查 bytes，不以 U+FFFD 猜測；不等於「缺少單字 token」或「原始單位元組 token 數」。
- `han_split_rate`：漢字內部有實際 token 邊界的比例。
- `han_one_token_rate`：byte 區間恰好等於一個 token 區間的漢字比例；多字合併也會降低它，故不是品質分數。
- `fertility`：n_tokens / Jieba 參照單位數。Jieba 包含標點等單位；改用人類詞界時要明確定義分母。
- `boundary_f1`：實際 token 邊界 vs Jieba 邊界，均使用 UTF-8 byte 座標；碎片的內部邊界也計入。不稱作斷詞準確率。
- 平均字形差：每項目跨所選用詞的繁−簡平均；平均用詞差：跨兩種字形的地區−中國用詞平均；交互作用：繁體下的用詞差−簡體下的用詞差。
- 精確基準路徑：台繁−中簡 = (台簡−中簡) + (台繁−台簡)。邊際效果不當成此路徑的貢獻。
- 95% CI：項目差值平均的 percentile bootstrap，B=10,000，seed=20261007。每對比使用穩定 RNG；不受其他分析執行順序影響。
- Wilcoxon / rank-biserial：補充性的符號秩結果，不檢定與平均差區間完全相同的假設。p 未作多重比較校正；n_nonzero 與完整 n 分開報告。
- 成本情境：使用總 tokens / 總字數的比率；價格與 context 由使用者假設，非 tokenizer 屬性或供應商報價。

在自撰材料上 bootstrap 不會補足代表性；小子集的區間不穩定。沒有顯著結果不等於等價，也不要求學生製造 null 結果。詞表是形式片段清單，不能直接當成構式庫、頻率表或訓練語料重建。

## 程式與輸出

| 檔案 | 用途 |
|---|---|
| stimuli.py | 歷史材料、公開篩選與逐字控制 |
| minitok.py | 輕量 ordinary-text BPE 編碼器 |
| metrics.py | byte 區間、片段有效性、漢字與詞界指標 |
| stats.py | 項目對比、穩定 bootstrap、補充檢定 |
| vocab_audit.py | 精確字串覆蓋與形式條目描述 |
| run_study.py | 生成 JSON / CSV 與來源識別 |
| validate.py | 官方編碼與測量一致性檢查 |
| build_web.py | 安全嵌入 JSON，生成頁面 |
| data/study.json | 完整材料、token ID / hex / 區間、效果與來源 |
| data/measurements.csv | 444 格原始測量 |
| data/validation.json | 計算驗證紀錄 |
| web/zh-tokenizer.template.html | v3 互動樣板 |

## v2 → v3

1. 移除普遍性「字形稅」結論、覆蓋率與頻率的二分因果說法。
2. 台中與香港分開，保留全部材料的敏感度比較；逐字相同控制由程式選出。
3. 顯示真實 token bytes / ID，修正漢字完整性與詞界座標。
4. 詞表覆蓋只計精確單漢字，不剝掉空白；分母公開。
5. CI 圖保留負值與零線；平均差區間與 Wilcoxon 各自解讀。
6. 構式例子只討論表面邊界；成本由可調情境計算。
7. 實驗頁與作業入口同步更新；兩個 repo 的分析副本一致。

歷史 v2 快照保留在 `../zh-tokenizer-v2.html`，含已更正解釋，不作現行作業範本。

## 技術定義參照

使用可查的官方來源，不再保留未核對的記憶式文獻引用：

- [tiktoken](https://github.com/openai/tiktoken) 與 [byte 解碼介面](https://github.com/openai/tiktoken/blob/main/tiktoken/core.py)
- [OpenCC](https://github.com/BYVoid/OpenCC)：詞組與上下文轉換，不是單純 Unicode 碼位代換
- [SciPy Wilcoxon](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html)：符號秩虛無假設與 ties / zeros 的處理

日後做語料或模型研究時，再按研究問題補充經查證的學術文獻。此頁的指標皆以程式定義為準。

## 瀏覽器驗證

```bash
python -m pip install -r requirements-browser.txt
# 未安裝 Chrome 時：python -m playwright install chromium
python test_browser.py http://127.0.0.1:8000/zh-tokenizer.html
```

先從網站根目錄開 HTTP server；URL 請依本地路徑調整。測試包含範圍／tokenizer／類別的 60 組切換、444 格 Python/JS token 證據一致性、負值 CI、CSV/JSON 下載、成本邊界、Unicode/BOM、手機版面、離線分析與載入失敗。測試輸出到暫存目錄；這不是 Colab 執行驗證。
