/**
 * Live Character Counter for Django Admin SEO fields.
 * Always displays the character count and recommended limits.
 */
(function () {
  'use strict';

  const FIELD_RULES = {
    home_title: { label: 'Title главной', min: 50, max: 60, hardLimit: 75 },
    blog_title: { label: 'Title блога', min: 50, max: 60, hardLimit: 75 },
    seo_title: { label: 'SEO Title', min: 50, max: 60, hardLimit: 75 },

    home_description: { label: 'Description главной', min: 150, max: 165, hardLimit: 180 },
    blog_description: { label: 'Description блога', min: 150, max: 165, hardLimit: 180 },
    seo_description: { label: 'SEO Description', min: 150, max: 165, hardLimit: 180 },
  };

  function getRuleForInput(input) {
    const name = (input.name || '').toLowerCase();
    const id = (input.id || '').toLowerCase();
    const rowClass = (input.closest('.form-row')?.className || '').toLowerCase();

    // Check exact known fields
    for (const [key, rule] of Object.entries(FIELD_RULES)) {
      if (
        name === key ||
        id === `id_${key}` ||
        id.endsWith(`_${key}`) ||
        rowClass.includes(`field-${key}`)
      ) {
        return rule;
      }
    }

    // Generic match for SEO fields
    if (name.includes('title') || id.includes('title') || rowClass.includes('title')) {
      return { label: 'Title', min: 50, max: 60, hardLimit: 75 };
    }
    if (
      name.includes('description') ||
      id.includes('description') ||
      name.includes('desc') ||
      id.includes('desc') ||
      rowClass.includes('description')
    ) {
      return { label: 'Description', min: 150, max: 165, hardLimit: 180 };
    }

    return null;
  }

  function updateCounter(input, counterEl, rule) {
    const len = (input.value || '').length;

    let statusClass = 'char-counter-empty';
    let icon = '📏';
    let hintText = '';

    if (len === 0) {
      statusClass = 'char-counter-empty';
      hintText = `(рекомендуется: ${rule.min}–${rule.max})`;
    } else if (len >= rule.min && len <= rule.max) {
      statusClass = 'char-counter-optimal';
      icon = '✓';
      hintText = `(оптимально: ${rule.min}–${rule.max})`;
    } else if (len < rule.min) {
      statusClass = 'char-counter-under';
      icon = '📏';
      hintText = `(рекомендуется: ${rule.min}–${rule.max})`;
    } else if (len <= rule.hardLimit) {
      statusClass = 'char-counter-warning';
      icon = '⚠️';
      hintText = `(желательно до ${rule.max})`;
    } else {
      statusClass = 'char-counter-danger';
      icon = '⚠️';
      hintText = `(превышен лимит сниппета: ${rule.max})`;
    }

    counterEl.className = `char-counter-badge ${statusClass}`;
    counterEl.innerHTML = `
      <span class="char-counter-icon">${icon}</span>
      <span class="char-counter-label">Символов: <strong class="char-counter-num">${len}</strong></span>
      <span class="char-counter-hint">${hintText}</span>
    `;
  }

  function initCounter(input) {
    if (input.dataset.hasCharCounter === 'true') return;

    const rule = getRuleForInput(input);
    if (!rule) return;

    input.dataset.hasCharCounter = 'true';

    const counter = document.createElement('div');
    counter.className = 'char-counter-badge char-counter-empty';

    // Insert right below input or textarea, above .help text
    const parent = input.parentNode;
    const helpEl = parent.querySelector('.help');
    if (helpEl) {
      parent.insertBefore(counter, helpEl);
    } else if (input.nextSibling) {
      parent.insertBefore(counter, input.nextSibling);
    } else {
      parent.appendChild(counter);
    }

    const handler = () => updateCounter(input, counter, rule);

    input.addEventListener('input', handler);
    input.addEventListener('keyup', handler);
    input.addEventListener('change', handler);
    input.addEventListener('paste', () => setTimeout(handler, 20));
    input.addEventListener('cut', () => setTimeout(handler, 20));

    // Initial render
    handler();
  }

  function runAll() {
    const inputs = document.querySelectorAll(
      'input[type="text"], textarea, .vTextField, .vLargeTextField'
    );
    inputs.forEach(initCounter);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runAll);
  } else {
    runAll();
  }

  window.addEventListener('load', runAll);

  // MutationObserver for dynamic admin forms
  const observer = new MutationObserver(function () {
    runAll();
  });
  if (document.body) {
    observer.observe(document.body, { childList: true, subtree: true });
  }

  // Periodic safety pass for 3 seconds after page load
  let passes = 0;
  const timer = setInterval(() => {
    runAll();
    passes++;
    if (passes > 6) clearInterval(timer);
  }, 500);
})();
