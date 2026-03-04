# 網站內容維護指南

> 所有課程內容集中在 `_data/` 資料夾的 YAML 檔案中。
> **一般維護完全不需要碰 HTML/CSS/JS。**

---

## 快速開始：更新後發布

```bash
git add .
git commit -m "content: 說明你更新了什麼"
git push
```

推送後約 2 分鐘，GitHub Actions 自動重建並發布至：
`https://lopentu.github.io/genai4humanities2026/`

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

## 5. 本機預覽（選用）

> **前提：** 需先在終端機執行一次 `sudo xcodebuild -license accept` 以啟用編譯器。

```bash
cd /Users/shukai/academics/GenAI4Humanities/2026/website
bundle install          # 第一次需要
bundle exec jekyll serve --baseurl ""
# 開啟 http://localhost:4000 預覽
```

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
