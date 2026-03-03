---
layout: home
title: 首頁
---

<!-- HERO -->
<section class="hero">
  <div class="container hero-content">
    <p class="hero-eyebrow">Spring 2026 &nbsp;|&nbsp; 114-2</p>
    <h1 class="hero-title">生成式 AI 的<br>人文導論</h1>
    <p class="hero-title-en">Introducing Generative AI for the Humanities</p>
    <div class="hero-actions">
      <a href="{{ site.baseurl }}/schedule/" class="btn btn-primary">查看課程進度 →</a>
      <a href="{{ site.baseurl }}/resources/" class="btn btn-outline">學習資源</a>
    </div>
    <p class="hero-meta">
      <span>{{ site.instructor }}</span>
      &nbsp;·&nbsp; 語言學研究所
      &nbsp;·&nbsp; <span>LING5004</span>
      &nbsp;·&nbsp; TAICA
    </p>
  </div>
</section>

<!-- STATS BAR -->
<div class="stats-bar">
  <div class="container">
    <div class="stat-item"><strong>16</strong> 週課程</div>
    <div class="stat-item"><strong>3</strong> 學分</div>
    <div class="stat-item"><strong>100</strong> 人上限</div>
    <div class="stat-item"><strong>文學院</strong> 大學部與研究生</div>
  </div>
</div>

<!-- OVERVIEW -->
<section class="section">
  <div class="container">
    <div class="overview-grid">
      <div class="overview-text fade-up">
        <h2 class="section-title">課程<span>概述</span></h2>
        <p>隨著AI科技的迅速發展，生成式 AI 迅速與多樣化產製內容的能力，不論在知識傳承或實務創作上，都帶給人文社會領域新的養分與挑戰。</p>
        <p>本堂課特別針對人文領域的學生設計，以人本為核心關懷出發，以直觀概念與模擬講解 AI 模型的基礎與發展，並搭配文史哲議題、語言與溝通、藝術音樂與遊戲創作等人文主題的實作練習。</p>
        <p style="font-size:0.88rem; color: var(--c-accent-gold); font-family: var(--font-mono);">重點不在「會用」，而是要「會活用、反思 AI 技術」。</p>
      </div>
      <div class="grading-chart fade-up">
        <h3>評量方式</h3>
        <div class="donut-container">
          <svg viewBox="0 0 36 36" width="180" height="180">
            <!-- 40% Final Project (gold) -->
            <circle cx="18" cy="18" r="15.9" fill="none" stroke="#E8A045" stroke-width="3.5"
              stroke-dasharray="25.13 65.97" stroke-dashoffset="0"/>
            <!-- 40% Assignments (violet) -->
            <circle cx="18" cy="18" r="15.9" fill="none" stroke="#7B6FF0" stroke-width="3.5"
              stroke-dasharray="25.13 65.97" stroke-dashoffset="-25.13"/>
            <!-- 20% Participation (teal) -->
            <circle cx="18" cy="18" r="15.9" fill="none" stroke="#4ECDC4" stroke-width="3.5"
              stroke-dasharray="12.57 78.53" stroke-dashoffset="-50.27"/>
          </svg>
          <div class="donut-label">
            <span>100</span>
            <span>POINTS</span>
          </div>
        </div>
        <ul class="grading-legend">
          <li><span class="legend-dot" style="background:#E8A045"></span>期末專案 40%</li>
          <li><span class="legend-dot" style="background:#7B6FF0"></span>每週作業 40%</li>
          <li><span class="legend-dot" style="background:#4ECDC4"></span>課堂參與 20%</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<!-- HIGHLIGHTS -->
<section class="section" style="background: var(--c-bg-card); border-top: 1px solid var(--c-border); border-bottom: 1px solid var(--c-border);">
  <div class="container">
    <h2 class="section-title fade-up">本學期<span>亮點</span></h2>
    <div class="highlights-grid">
      <div class="highlight-card fade-up">
        <div class="card-icon">💬</div>
        <h3 class="card-title">Prompting & Vibe Coding</h3>
        <p class="card-desc">以語義、風格與敘事驅動的提示設計，讓人文底蘊成為你與 AI 對話的最大優勢。</p>
      </div>
      <div class="highlight-card fade-up">
        <div class="card-icon">🎨</div>
        <h3 class="card-title">AI × 藝術數位策展</h3>
        <p class="card-desc">跨界應用生成式 AI 於文學場景再現、藝術風格混搭、音樂創作，探索 AI 美學的邊界。</p>
      </div>
      <div class="highlight-card fade-up">
        <div class="card-icon">🧭</div>
        <h3 class="card-title">倫理、對齊與數位分身</h3>
        <p class="card-desc">深入探討 AI 時代的人類價值議題：對齊（Alignment）、數位分身、深度偽造的社會衝擊。</p>
      </div>
    </div>
  </div>
</section>

<!-- TEAM -->
<section class="section">
  <div class="container">
    <h2 class="section-title fade-up">師資<span>團隊</span></h2>
    {% assign instructor = site.data.team.instructor %}
    <div class="instructor-card fade-up">
      <img class="instructor-avatar"
           src="{{ site.baseurl }}{{ instructor.avatar }}"
           alt="{{ instructor.name }}"
           onerror="this.style.background='var(--c-bg-card-alt)';this.removeAttribute('src')">
      <div class="instructor-info">
        <h3>{{ instructor.name }}</h3>
        <p>{{ instructor.title }}</p>
        <p style="margin-top:0.3rem;">
          <a href="https://github.com/{{ instructor.github }}" target="_blank" rel="noopener"
             style="font-size:0.8rem; font-family: var(--font-mono);">
            GitHub ↗
          </a>
        </p>
      </div>
    </div>

    {% if site.data.team.tas.size > 0 %}
    <h3 style="font-family: var(--font-sans); font-size:0.9rem; color: var(--c-text-muted); letter-spacing: 0.05em; margin-bottom: var(--space-sm);">TEACHING ASSISTANTS</h3>
    <div class="ta-grid">
      {% for ta in site.data.team.tas %}
      <div class="ta-card fade-up">
        <img class="ta-avatar" src="{{ site.baseurl }}{{ ta.avatar }}" alt="{{ ta.name }}"
             onerror="this.style.background='var(--c-bg-card-alt)';this.removeAttribute('src')">
        <p class="ta-name">{{ ta.name }}</p>
        <p class="ta-role">{{ ta.role | default: "Teaching Assistant" }}</p>
      </div>
      {% endfor %}
    </div>
    {% endif %}
  </div>
</section>
