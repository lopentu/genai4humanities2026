---
layout: page
title: 學習資源
subtitle: "工具、書目與認證資源"
permalink: /resources/
---

{% for section in site.data.resources.sections %}
<div class="fade-up" style="margin-bottom: var(--space-lg);">
  <h2 class="section-title" style="font-size: 1.5rem; margin-bottom: var(--space-sm);">
    {{ section.icon }} <span>{{ section.title }}</span>
  </h2>
  <div class="highlights-grid">
    {% for item in section.items %}
    <a href="{{ item.url }}" target="_blank" rel="noopener" class="highlight-card"
       style="display:block; color: inherit; text-decoration: none;">
      <h3 class="card-title" style="font-size:1rem;">{{ item.name }}</h3>
      {% if item.desc and item.desc != "" %}
      <p class="card-desc">{{ item.desc }}</p>
      {% endif %}
    </a>
    {% endfor %}
  </div>
</div>
{% endfor %}

<!-- Interactive practice -->
<div class="fade-up" style="margin-top: var(--space-lg);">
  <h2 class="section-title" style="font-size: 1.5rem; margin-bottom: var(--space-sm);">
    🕹️ <span>互動練習</span>
  </h2>

  <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: var(--space-sm);">
    <button
      type="button"
      onclick="window.__practiceTab('kana')"
      style="padding: 0.75rem 1.2rem; border-radius: 8px; border: 1px solid var(--c-border); background: rgba(255,255,255,0.02); color: var(--c-text); font-family: var(--font-sans); cursor: pointer;"
      id="practice-tab-kana">
      互動練習
    </button>
    <button
      type="button"
      onclick="window.__practiceTab('vibe')"
      style="padding: 0.75rem 1.2rem; border-radius: 8px; border: 1px solid var(--c-border); background: rgba(255,255,255,0.02); color: var(--c-text); font-family: var(--font-sans); cursor: pointer;"
      id="practice-tab-vibe">
      vibe coding practice
    </button>
  </div>

  <div id="practice-panel-kana" style="border: 1px solid var(--c-border); border-radius: 12px; overflow: hidden;">
    <iframe
      src="https://lopentu.github.io/genai4humanities/vc/session1-kana-memory-v2-embed.html"
      title="仮名メモリー（假名配對遊戲）"
      style="width: 100%; height: 900px; border: 0; display: block;"
      loading="lazy"
      allowfullscreen>
    </iframe>
  </div>

  <div id="practice-panel-vibe" style="display: none;">
    <h3 class="section-title" style="font-size: 1.25rem; margin-top: var(--space-lg); margin-bottom: var(--space-sm);">
      第一個專案練習
    </h3>

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
</div>

<script>
  window.__practiceTab = function (tab) {
    const kanaPanel = document.getElementById("practice-panel-kana");
    const vibePanel = document.getElementById("practice-panel-vibe");
    const tabKana = document.getElementById("practice-tab-kana");
    const tabVibe = document.getElementById("practice-tab-vibe");
    if (!kanaPanel || !vibePanel) return;

    const isKana = tab === "kana";
    kanaPanel.style.display = isKana ? "block" : "none";
    vibePanel.style.display = isKana ? "none" : "block";

    if (tabKana && tabVibe) {
      tabKana.style.borderColor = isKana ? "rgba(232,160,69,0.8)" : "var(--c-border)";
      tabVibe.style.borderColor = !isKana ? "rgba(232,160,69,0.8)" : "var(--c-border)";
    }
  };
</script>

<script>
  // Support header nav click: /resources/?practice=vibe
  (function () {
    try {
      const params = new URLSearchParams(window.location.search);
      const tab = params.get("practice");
      if (tab === "vibe" && window.__practiceTab) window.__practiceTab("vibe");
    } catch (e) {}
  })();
</script>
