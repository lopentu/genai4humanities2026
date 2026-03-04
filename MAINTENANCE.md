# 網站內容維護指南

> 所有課程內容集中在 `_data/` 資料夾的 YAML 檔案中。
> **一般維護完全不需要碰 HTML/CSS/JS，也不用在本機安裝 Ruby 或 Jekyll。**

---

## 更新方式（就這三步）

1. **編輯** — 用編輯器改 `_data/` 裡的 YAML 或 `pages/` 裡的 Markdown（見下方各節）。
2. **提交** — 在專案目錄執行：
   ```bash
   git add .
   git commit -m "content: 說明你更新了什麼"
   git push
   ```
3. **完成** — 約 2 分鐘後網站會自動更新：  
   `https://lopentu.github.io/genai4humanities2026/`

**不用在本機跑 Jekyll。** 改完 push，到上面網址看結果即可。

---

## 1. 更新課程進度

編輯 `_data/schedule.yml`，每週格式如下：

```yaml
- week: 8
  date: "2026-04-17"
  title: "讓生成式AI模型少說錯"
  subtitle: "Context Engineering (RAG)"
  cluster: "agent"      # prompting / llm / agent / humanities / ethics / final
  holiday: false
  objectives:
    - "了解 RAG 的基本原理"
    - "實作向量資料庫查詢"
```

**假日週範例：**
```yaml
- week: 6
  date: "2026-04-03"
  title: "兒童節補假"
  subtitle: ""
  cluster: ""
  holiday: true
  objectives: []
```

---

## 2. 新增助教

編輯 `_data/team.yml`，在 `tas:` 清單下新增：

```yaml
tas:
  - name: "王小明"
    github: "ming-wang"
    avatar: "/assets/images/ta-ming.jpg"   # 圖片放到 assets/images/
    role: "Teaching Assistant"
```

> 頭像圖片放到 `assets/images/` 資料夾，建議尺寸 200×200px。

---

## 3. 新增學習資源

編輯 `_data/resources.yml`，在對應的 section 新增 item：

```yaml
- title: "AI 工具"
  icon: "🤖"
  items:
    - name: "新工具名稱"
      url: "https://example.com"
      desc: "一句話說明"
```

---

## 4. 更新作業說明

編輯 `pages/assignments.md`，直接在檔案中加入作業卡片：

```markdown
<div class="highlight-card fade-up">
  <div class="card-icon">📝</div>
  <h3 class="card-title">作業一：Prompting 練習</h3>
  <p class="card-desc">截止日期：03/20 ｜ 繳交至 NTU COOL</p>
</div>
```

---

## 5. 本機預覽（可略過）

平常**不需要**本機預覽：改完 push，等 2 分鐘到正式站看即可。

若真的想在 push 前先看效果，有兩種方式：

| 方式 | 優點 | 做法 |
|------|------|------|
| **Docker** | 不用裝 Ruby，一條指令 | 本機先裝 [Docker Desktop](https://www.docker.com/products/docker-desktop/)，在 `website` 目錄執行：<br>`docker run --rm -p 4000:4000 -v "$(pwd):/srv/jekyll" jekyll/jekyll:4 jekyll serve --baseurl ""`<br>瀏覽器開 http://localhost:4000 |
| **本機 Ruby** | 與 GitHub 建置環境一致 | `bundle install` 後執行 `bundle exec jekyll serve --baseurl ""`（需 Xcode Command Line Tools，且建議用系統或 Homebrew 的 Ruby，不要用 conda 的 Ruby） |

不想搞環境的話，直接略過本機預覽，改完 push 到線上檢查即可。

---

## 檔案結構速查

```
website/
├── _data/
│   ├── schedule.yml    ← 課程週次（主要編輯這裡）
│   ├── team.yml        ← 師資名單
│   └── resources.yml   ← 學習資源
├── pages/
│   ├── schedule.md     ← 課程進度頁（通常不需改）
│   ├── assignments.md  ← 作業頁（需定期更新）
│   ├── project.md      ← 期末專案說明
│   └── resources.md    ← 資源頁（通常不需改）
├── assets/images/      ← 放頭像、圖片
└── index.md            ← 首頁（學期開始後幾乎不需改）
```

---

## 常見情境

| 要做什麼 | 編輯哪個檔案 |
|---------|------------|
| 修改某週主題或學習目標 | `_data/schedule.yml` |
| 新增 / 修改助教資訊 | `_data/team.yml` |
| 新增參考書目或工具 | `_data/resources.yml` |
| 公布作業 | `pages/assignments.md` |
| 更新期末專案說明 | `pages/project.md` |
| 修改首頁課程描述 | `index.md` |
