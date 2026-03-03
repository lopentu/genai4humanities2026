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
