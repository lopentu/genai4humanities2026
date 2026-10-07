# 中文 Tokenization v3：程式、材料與判讀

<div class="intro">這是一個自撰材料的探索實驗。用字形與用詞的交叉對照觀察切分，再檢查材料篩選、分母與成本情境是否改變你的結論。</div>

[開啟實驗工作台 v3](../zh-tokenizer.html) · [延伸練習](assignment1.html) · [LING5006 A1](https://lopentu.github.io/courses/cllt2026/a1/)

## 先走一次實驗

1. 在工作台查看 29 個模板篩選項目的台中 2×2 格子；這些材料仍未母語者校訂。
2. 切換「全部材料」「香港排除低信心」與「逐字相同控制」，看效果改變多少。
3. 用 token ID、UTF-8 hex 與 byte 區間查驗碎片；單獨不可解碼不等於缺少單字 token。
4. 檢查構式例子的表面切分；模型是否理解構式要另做實驗。
5. 輸入價格與 context 假設，選漢字或 Unicode 碼位分母。情境值不是現行供應商價格。
6. 下載 JSON / CSV，公開你的比較單位、排除規則與推論範圍。

## v3 更正了什麼？

移除普遍性的「字形稅」結論、將詞表視為構式庫的推論，以及「新聞類都是對照」的假設。修正碎片辨識、漢字單 token 指標與詞界座標；信賴區間保留負值，Wilcoxon 與平均差 CI 分開解讀。

[完整修訂與指標定義](README.md) · [完整資料](data/study.json) · [測量 CSV](data/measurements.csv) · [官方 tiktoken 比對紀錄](data/validation.json)

## 本地重現

```bash
cd lab/session-9/tokfair
python -m pip install -r requirements.txt
bash vendor_ranks.sh
python run_study.py
python validate.py
python build_web.py --out ../zh-tokenizer.html
python build_docs.py
```

第一次取得 rank 表需 Node/npm 與網路。之後普通文字分析可離線；驗證程式第一次可能下載官方 rank 表。資料保留 source / rank hash、套件版本、seed 與原始對比。

## 程式地圖

| 檔案 | 可檢查的問題 |
|---|---|
| [stimuli.py](stimuli.py) | 怎麼選材料？哪些被排除？哪幾句逐字相同？ |
| [metrics.py](metrics.py) | bytes、漢字與參照詞界如何量？分母是什麼？ |
| [stats.py](stats.py) | 項目內對比怎麼算？CI 與檢定分別問什麼？ |
| [vocab_audit.py](vocab_audit.py) | 單字覆蓋的條件分母與精確匹配是什麼？ |
| [run_study.py](run_study.py) | 如何生成同一份 JSON / CSV 與來源識別？ |
| [validate.py](validate.py) | 如何獨立比對官方編碼與重新量全部資料？ |
| [build_web.py](build_web.py) | 如何把資料嵌入互動工作台？ |

## 仍待完成

材料未做母語者校訂或真實語料抽樣；香港版本含語法與指涉差異。兩個 tokenizer 的差異不能識別訓練資料或團隊的因果作用。平台沒有測量模型理解，也沒有替任何使用情境定義公平性門檻。

[歷史 v2（含已更正的解釋）](../zh-tokenizer-v2.html) · [v1 歷史探索器](../zh-tokenizer-v1.html)
