// assets/js/main.js

// ── Scroll-triggered fade-up animations ──
(function() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));
})();

// ── Week accordion (schedule page) ──
(function() {
  document.querySelectorAll('.week-card').forEach(card => {
    if (card.closest('.holiday')) return;
    card.addEventListener('click', () => {
      const objectives = card.querySelector('.week-objectives');
      if (objectives) objectives.classList.toggle('open');
    });
  });
})();

// ── Active nav link ──
(function() {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach(link => {
    if (link.getAttribute('href') === path || path.startsWith(link.getAttribute('href'))) {
      link.classList.add('active');
    }
  });
})();
