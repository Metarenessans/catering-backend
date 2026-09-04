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

    const initialName = nameInput.value.trim();
    const initialSlug = slugInput.value.trim();

    const matchesInitialName = !initialSlug || initialSlug === slugify(initialName);
    let userManuallyEditedSlug = !matchesInitialName;

    const wrapper = document.createElement('div');
    wrapper.className = 'slug-input-wrapper';

    const btnRefresh = document.createElement('button');
    btnRefresh.type = 'button';
    btnRefresh.className = 'btn-refresh-slug';
    btnRefresh.title = 'Сгенерировать slug из названия';
    btnRefresh.setAttribute('aria-label', 'Сгенерировать slug из названия');
    btnRefresh.innerHTML = '🔄';

    slugInput.parentNode.insertBefore(wrapper, slugInput);
    wrapper.appendChild(slugInput);
    wrapper.appendChild(btnRefresh);

    function updateSlugFromName() {
      const curName = nameInput.value.trim();
      slugInput.value = curName ? slugify(curName) : '';
      slugInput.dispatchEvent(new Event('change', { bubbles: true }));
    }

    btnRefresh.addEventListener('click', function (e) {
      e.preventDefault();
      userManuallyEditedSlug = false;
      updateSlugFromName();
      slugInput.classList.remove('slug-updated-flash');
      void slugInput.offsetWidth;
      slugInput.classList.add('slug-updated-flash');
    });

    slugInput.addEventListener('input', function () {
      const curSlug = slugInput.value.trim();
      const expected = slugify(nameInput.value.trim());
      if (!curSlug) {
        userManuallyEditedSlug = false;
      } else if (curSlug !== expected) {
        userManuallyEditedSlug = true;
      }
    });

    nameInput.addEventListener('input', function () {
      const curName = nameInput.value.trim();

      if (!curName) {
        userManuallyEditedSlug = false;
        slugInput.value = '';
        slugInput.dispatchEvent(new Event('change', { bubbles: true }));
        return;
      }

      if (!userManuallyEditedSlug || !slugInput.value.trim()) {
        updateSlugFromName();
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSlugAutoUpdate);
  } else {
    initSlugAutoUpdate();
  }
})();
