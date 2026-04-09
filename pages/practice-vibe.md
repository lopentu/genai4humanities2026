---
layout: page
title: lab sessions
subtitle: "課堂 Lab 互動頁與第一個專案練習"
permalink: /practice/lab/
---

<p class="fade-up">
  以下為本課程 <code>lab</code> 資料夾中各週的靜態互動頁入口；點選區塊可進入該週列表，再開啟單一 HTML 練習。底部保留「第一個專案練習」嵌入頁（與先前學習資源頁相同內容）。
</p>

<div class="fade-up" style="margin-top: var(--space-lg); margin-bottom: var(--space-sm);">
  <h2 class="section-title" style="font-size: 1.5rem;">
    📂 <span>依 Lab 週次瀏覽</span>
  </h2>
  <div class="highlights-grid">
    {% for s in site.data.vibe_lab.sessions %}
    <a
      href="{{ site.baseurl }}/practice/lab/{{ s.id }}/"
      class="highlight-card"
      style="display: block; color: inherit; text-decoration: none;"
    >
      <h3 class="card-title" style="font-size: 1.05rem;">{{ s.title }}</h3>
      <p class="card-desc">{{ s.blurb }}</p>
    </a>
    {% endfor %}
  </div>
</div>

<div class="fade-up" style="margin-top: var(--space-lg);">
  <h2 class="section-title" style="font-size: 1.5rem;">
    🎯 <span>第一個專案練習（嵌入）</span>
  </h2>
  <p class="card-desc" style="margin-bottom: var(--space-sm); max-width: 48rem;">
    學習挑戰卡：外觀調整與擴充（舊版學習資源頁之「vibe」分頁同一內容）。
  </p>
  <div style="border: 1px solid var(--c-border); border-radius: 12px; overflow: hidden;">
    <iframe
      src="https://lopentu.github.io/genai4humanities/vc/session1-challenge-card-interactive-embed.html"
      title="學習挑戰卡（外觀調整與擴充）"
      style="width: 100%; height: 720px; border: 0; display: block;"
      loading="lazy"
      allowfullscreen>
    </iframe>
  </div>
</div>
