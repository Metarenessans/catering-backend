(function () {
  'use strict';

  const RU_MAP = {
    а: 'a', б: 'b', в: 'v', г: 'g', д: 'd', е: 'e', ё: 'yo', ж: 'zh',
    з: 'z', и: 'i', й: 'y', к: 'k', л: 'l', м: 'm', н: 'n', о: 'o',
    п: 'p', р: 'r', с: 's', т: 't', у: 'u', ф: 'f', х: 'kh', ц: 'ts',
    ч: 'ch', ш: 'sh', щ: 'shch', ъ: '', ы: 'y', ь: '', э: 'e', ю: 'yu',
    я: 'ya'
  };

  function slugify(text) {
    if (typeof URLify === 'function') {
      const u = URLify(text, 100, false);
      if (u) return u;
    }
    return text
      .toLowerCase()
      .split('')
      .map((c) => RU_MAP[c] || c)
      .join('')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');
  }

  function initSlugAutoUpdate() {
    const nameInput = document.getElementById('id_name');
    const slugInput = document.getElementById('id_slug');
    if (!nameInput || !slugInput) return;

    if (slugInput.parentNode.querySelector('.btn-refresh-slug')) return;

    const initialSlug = slugInput.value.trim();
    // Если слаг уже был при загрузке страницы — это существующая запись.
    // Для существующих записей автогенерацию при вводе отключаем, чтобы не ломать рабочие URL!
    const isNewRecord = !initialSlug;
    let userManuallyEditedSlug = !isNewRecord;

    const wrapper = document.createElement('div');
    wrapper.className = 'slug-input-wrapper';
    wrapper.style.cssText = 'display: inline-flex !important; align-items: center !important; gap: 8px !important; vertical-align: middle !important;';

    const btnRefresh = document.createElement('button');
    btnRefresh.type = 'button';
    btnRefresh.className = 'btn-refresh-slug';
    btnRefresh.title = 'Обновить slug из названия';
    btnRefresh.setAttribute('aria-label', 'Обновить slug из названия');
    btnRefresh.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display:block; margin:auto; flex-shrink:0;">
        <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.3"/>
      </svg>
    `;

    // Инлайн стили для гарантированно тёмного фона независимо от кэша браузера
    btnRefresh.style.cssText = `
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      width: 35px !important;
      height: 35px !important;
      padding: 0 !important;
      margin: 0 !important;
      background: #25282c !important;
      background-color: #25282c !important;
      border: 1px solid #41454c !important;
      border-radius: 6px !important;
      cursor: pointer !important;
      color: #e2e8f0 !important;
      transition: all 0.15s ease !important;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4) !important;
      flex-shrink: 0 !important;
    `;

    btnRefresh.addEventListener('mouseenter', function () {
      btnRefresh.style.backgroundColor = '#1e3a8a';
      btnRefresh.style.borderColor = '#3b82f6';
      btnRefresh.style.color = '#ffffff';
    });

    btnRefresh.addEventListener('mouseleave', function () {
      btnRefresh.style.backgroundColor = '#25282c';
      btnRefresh.style.borderColor = '#41454c';
      btnRefresh.style.color = '#e2e8f0';
    });

    slugInput.parentNode.insertBefore(wrapper, slugInput);
    wrapper.appendChild(slugInput);
    wrapper.appendChild(btnRefresh);

    function updateSlugFromName() {
      const curName = nameInput.value.trim();
      if (!curName) return;
      slugInput.value = slugify(curName);
      slugInput.dispatchEvent(new Event('change', { bubbles: true }));
      btnRefresh.style.backgroundColor = '#1e3a8a';
      btnRefresh.style.borderColor = '#3b82f6';
      setTimeout(() => {
        btnRefresh.style.backgroundColor = '#25282c';
        btnRefresh.style.borderColor = '#41454c';
      }, 500);
    }

    btnRefresh.addEventListener('click', function (e) {
      e.preventDefault();
      updateSlugFromName();
    });

    slugInput.addEventListener('input', function () {
      userManuallyEditedSlug = true;
    });

    // Автогенерация при наборе текста работает ТОЛЬКО при создании новой записи
    if (isNewRecord) {
      nameInput.addEventListener('input', function () {
        if (!userManuallyEditedSlug) {
          const curName = nameInput.value.trim();
          slugInput.value = curName ? slugify(curName) : '';
          slugInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSlugAutoUpdate);
  } else {
    initSlugAutoUpdate();
  }
})();
