---
layout: page
title: 課程進度
subtitle: "Spring 2026 ｜ 共 17 週（含補課）"
permalink: /schedule/
---

<div class="timeline">
  {% for week in site.data.schedule %}
  <div class="week-entry {% if week.holiday %}holiday{% endif %} cluster-{{ week.cluster }} fade-up">
    <div class="week-card">
      <div class="week-header">
        <span class="week-number">W{{ week.week }}</span>
        <span class="week-date">{{ week.date }}</span>
      </div>
      <h3 class="week-title">{{ week.title }}</h3>
      {% if week.subtitle and week.subtitle != "" %}
      <p class="week-subtitle">{{ week.subtitle }}</p>
      {% endif %}
      {% if week.objectives.size > 0 %}
      <div class="week-objectives">
        <ul>
          {% for obj in week.objectives %}
          <li>{{ obj }}</li>
          {% endfor %}
        </ul>
      </div>
      {% endif %}
    </div>
  </div>
  {% endfor %}
</div>

<p style="margin-top: var(--space-md); font-size: 0.8rem; color: var(--c-text-muted); font-family: var(--font-mono);">
  ✦ 點擊各週卡片可展開詳細學習目標
</p>
