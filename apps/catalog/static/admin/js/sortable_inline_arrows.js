(function () {
  'use strict';

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function getCsrfToken() {
    const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return input ? input.value : getCookie('csrftoken');
  }

  function flashRow(row) {
    row.classList.remove('row-moved-highlight');
    void row.offsetWidth; // trigger reflow
    row.classList.add('row-moved-highlight');
  }

  const GRIP_SVG = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" style="pointer-events: none;"><circle cx="8" cy="5" r="2.2"/><circle cx="16" cy="5" r="2.2"/><circle cx="8" cy="12" r="2.2"/><circle cx="16" cy="12" r="2.2"/><circle cx="8" cy="19" r="2.2"/><circle cx="16" cy="19" r="2.2"/></svg>';
  const UP_ARROW_SVG = '<svg width="8" height="6" viewBox="0 0 8 6" fill="currentColor" style="pointer-events: none;"><path d="M4 0L8 6H0L4 0Z"/></svg>';
  const DOWN_ARROW_SVG = '<svg width="8" height="6" viewBox="0 0 8 6" fill="currentColor" style="pointer-events: none;"><path d="M4 6L0 0H8L4 6Z"/></svg>';

  // ==========================================
  // 1. CHANGELIST TABLE SORTING (#result_list)
  // ==========================================

  // Only update visual UI (badges, disabled buttons), NEVER post to server!
  function updateChangelistUI(tbody) {
    if (!tbody) return;
    const rows = Array.from(tbody.querySelectorAll('tr')).filter(r => r.querySelector('td.field-_reorder_'));
    rows.forEach((row, index) => {
      const orderVal = index + 1;
      const badge = row.querySelector('.order-badge');
      if (badge) badge.textContent = orderVal;

      const upBtn = row.querySelector('.btn-order-up');
      if (upBtn) upBtn.disabled = (index === 0);

      const downBtn = row.querySelector('.btn-order-down');
      if (downBtn) downBtn.disabled = (index === rows.length - 1);
    });
  }

  let saveDebounceTimer = null;

  // Called ONLY when the user explicitly moves an item (clicks arrow or drops drag)
  function saveChangelistOrder(tbody, updateUrl) {
    if (!tbody || !updateUrl) return;
    const rows = Array.from(tbody.querySelectorAll('tr')).filter(r => r.querySelector('td.field-_reorder_'));
    if (rows.length === 0) return;

    let firstOrder = 1;
    for (let r of rows) {
      const h = r.querySelector('.handle');
      if (h && h.getAttribute('order')) {
        const val = parseInt(h.getAttribute('order'), 10);
        if (!isNaN(val)) {
          firstOrder = 1;
          break;
        }
      }
    }

    const updatedItems = [];
    rows.forEach((row, index) => {
      const orderVal = firstOrder + index;
      const badge = row.querySelector('.order-badge');
      if (badge) badge.textContent = orderVal;

      const handle = row.querySelector('.handle');
      if (handle) {
        handle.setAttribute('order', String(orderVal));
        const pk = handle.getAttribute('pk');
        if (pk) {
          updatedItems.push([pk, orderVal]);
        }
      }

      const upBtn = row.querySelector('.btn-order-up');
      if (upBtn) upBtn.disabled = (index === 0);

      const downBtn = row.querySelector('.btn-order-down');
      if (downBtn) downBtn.disabled = (index === rows.length - 1);
    });

    if (updatedItems.length === 0) return;

    if (saveDebounceTimer) clearTimeout(saveDebounceTimer);
    saveDebounceTimer = setTimeout(() => {
      fetch(updateUrl, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ updatedItems: updatedItems })
      }).then(res => {
        if (!res.ok) console.error('[Sortable] Save order error:', res.statusText);
      }).catch(err => {
        console.error('[Sortable] Network error while saving order:', err);
      });
    }, 100);
  }

  function initDisabledChangelistRow(row) {
    const reorderCell = row.querySelector('td.field-_reorder_');
    if (!reorderCell || reorderCell.querySelector('.reorder-cell-content')) return;

    let dragHandle = reorderCell.querySelector('.drag.handle') || reorderCell.querySelector('.drag');
    const initialOrder = dragHandle ? dragHandle.getAttribute('order') : '';

    const wrapper = document.createElement('div');
    wrapper.className = 'reorder-cell-content';

    const badge = document.createElement('span');
    badge.className = 'order-badge';
    badge.textContent = initialOrder || '—';
    badge.title = 'Позиция внутри категории';

    wrapper.appendChild(badge);
    reorderCell.innerHTML = '';
    reorderCell.appendChild(wrapper);
  }

  function initChangelistRow(row, tbody, updateUrl) {
    const reorderCell = row.querySelector('td.field-_reorder_');
    if (!reorderCell || reorderCell.querySelector('.reorder-cell-content')) return;

    let dragHandle = reorderCell.querySelector('.drag.handle') || reorderCell.querySelector('.drag');
    const pk = dragHandle ? dragHandle.getAttribute('pk') : row.querySelector('input.action-select')?.value;
    const initialOrder = dragHandle ? dragHandle.getAttribute('order') : '1';

    const wrapper = document.createElement('div');
    wrapper.className = 'reorder-cell-content';

    // Drag Handle
    if (!dragHandle) {
      dragHandle = document.createElement('div');
      dragHandle.className = 'drag handle';
      if (pk) dragHandle.setAttribute('pk', pk);
      if (initialOrder) dragHandle.setAttribute('order', initialOrder);
    }
    dragHandle.classList.add('drag-handle-btn');
    dragHandle.setAttribute('title', 'Зажмите и перетащите для изменения порядка');
    dragHandle.innerHTML = GRIP_SVG;

    // Order Badge (displays existing order initially)
    const badge = document.createElement('span');
    badge.className = 'order-badge';
    badge.textContent = initialOrder || '1';

    // Arrows
    const arrowsWrapper = document.createElement('div');
    arrowsWrapper.className = 'order-arrows-wrapper';

    const upBtn = document.createElement('button');
    upBtn.type = 'button';
    upBtn.className = 'btn-order-move btn-order-up';
    upBtn.title = 'Переместить выше';
    upBtn.innerHTML = UP_ARROW_SVG;
    upBtn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      const prevRow = row.previousElementSibling;
      if (prevRow && prevRow.querySelector('td.field-_reorder_')) {
        tbody.insertBefore(row, prevRow);
        updateChangelistUI(tbody);
        saveChangelistOrder(tbody, updateUrl);
        flashRow(row);
      }
    });

    const downBtn = document.createElement('button');
    downBtn.type = 'button';
    downBtn.className = 'btn-order-move btn-order-down';
    downBtn.title = 'Переместить ниже';
    downBtn.innerHTML = DOWN_ARROW_SVG;
    downBtn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      const nextRow = row.nextElementSibling;
      if (nextRow && nextRow.querySelector('td.field-_reorder_')) {
        tbody.insertBefore(nextRow, row);
        updateChangelistUI(tbody);
        saveChangelistOrder(tbody, updateUrl);
        flashRow(row);
      }
    });

    arrowsWrapper.appendChild(upBtn);
    arrowsWrapper.appendChild(downBtn);

    wrapper.appendChild(dragHandle);
    wrapper.appendChild(badge);
    wrapper.appendChild(arrowsWrapper);

    reorderCell.innerHTML = '';
    reorderCell.appendChild(wrapper);

    // Native HTML5 Drag & Drop on the handle
    dragHandle.setAttribute('draggable', 'true');

    dragHandle.addEventListener('dragstart', function (e) {
      row.classList.add('is-dragging');
      dragHandle.classList.add('is-grabbing');
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/plain', pk || '');
      window._activeSortableRow = row;
    });

    dragHandle.addEventListener('dragend', function () {
      row.classList.remove('is-dragging');
      dragHandle.classList.remove('is-grabbing');
      tbody.querySelectorAll('tr').forEach(r => {
        r.classList.remove('drag-over-top', 'drag-over-bottom');
      });
      window._activeSortableRow = null;
    });

    row.addEventListener('dragover', function (e) {
      if (!window._activeSortableRow || window._activeSortableRow === row) return;
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
      const rect = row.getBoundingClientRect();
      const mid = rect.top + rect.height / 2;
      if (e.clientY < mid) {
        row.classList.add('drag-over-top');
        row.classList.remove('drag-over-bottom');
      } else {
        row.classList.add('drag-over-bottom');
        row.classList.remove('drag-over-top');
      }
    });

    row.addEventListener('dragleave', function () {
      row.classList.remove('drag-over-top', 'drag-over-bottom');
    });

    row.addEventListener('drop', function (e) {
      if (!window._activeSortableRow || window._activeSortableRow === row) return;
      e.preventDefault();
      const draggingRow = window._activeSortableRow;
      const rect = row.getBoundingClientRect();
      const mid = rect.top + rect.height / 2;

      row.classList.remove('drag-over-top', 'drag-over-bottom');

      if (e.clientY < mid) {
        tbody.insertBefore(draggingRow, row);
      } else {
        tbody.insertBefore(draggingRow, row.nextElementSibling);
      }

      updateChangelistUI(tbody);
      saveChangelistOrder(tbody, updateUrl);
      flashRow(draggingRow);
    });
  }

  function initChangelist() {
    const table = document.getElementById('result_list');
    if (!table) return;
    const tbody = table.querySelector('tbody');
    if (!tbody) return;

    let updateUrl = null;
    const configElem = document.getElementById('admin_sortable2_config');
    if (configElem) {
      try {
        updateUrl = JSON.parse(configElem.textContent).update_url;
      } catch (e) {}
    }
    if (!updateUrl) {
      updateUrl = window.location.pathname.replace(/\/+$/, '') + '/adminsortable2_update/';
    }

    const rows = Array.from(tbody.querySelectorAll('tr')).filter(r => r.querySelector('td.field-_reorder_'));
    if (rows.length === 0) return;

    // If on Product changelist without a category filter, disable drag/arrows to protect category ordering
    const isProductChangelist = window.location.pathname.includes('/catalog/product/');
    const hasCategoryFilter = window.location.search.includes('category');
    if (isProductChangelist && !hasCategoryFilter) {
      rows.forEach(row => initDisabledChangelistRow(row));
      return;
    }

    rows.forEach(row => initChangelistRow(row, tbody, updateUrl));
    
    // IMPORTANT: Only update UI disabled buttons/badges on load. DO NOT POST/SAVE TO SERVER!
    updateChangelistUI(tbody);

    // Watch for outside DOM changes: ONLY update visual UI, NEVER save!
    const observer = new MutationObserver(function (mutations) {
      let isChildChange = false;
      for (const m of mutations) {
        if (m.type === 'childList') {
          isChildChange = true;
          break;
        }
      }
      if (isChildChange && !window._activeSortableRow) {
        updateChangelistUI(tbody);
      }
    });
    observer.observe(tbody, { childList: true });
  }

  // ==========================================
  // 2. INLINE FORMSET SORTING (.inline-group)
  // ==========================================
  function updateInlineOrderValues(tbody) {
    if (!tbody) return;
    const rows = Array.from(tbody.querySelectorAll('tr.form-row:not(.empty-form)'));
    rows.forEach((row, index) => {
      const orderVal = index + 1;
      const orderInput = row.querySelector('input._reorder_');
      if (orderInput) orderInput.value = orderVal;

      const badge = row.querySelector('.order-badge');
      if (badge) badge.textContent = orderVal;

      const upBtn = row.querySelector('.btn-order-up');
      if (upBtn) upBtn.disabled = (index === 0);

      const downBtn = row.querySelector('.btn-order-down');
      if (downBtn) downBtn.disabled = (index === rows.length - 1);
    });
  }

  function initInlineRow(row, tbody) {
    if (row.classList.contains('empty-form')) return;
    const reorderCell = row.querySelector('td.field-_reorder_');
    if (!reorderCell || reorderCell.querySelector('.reorder-cell-content')) return;

    let dragHandle = reorderCell.querySelector('.drag.handle') || reorderCell.querySelector('.drag');

    const wrapper = document.createElement('div');
    wrapper.className = 'reorder-cell-content';

    if (dragHandle) {
      dragHandle.classList.add('drag-handle-btn');
      dragHandle.innerHTML = GRIP_SVG;
      dragHandle.setAttribute('title', 'Зажмите и перетащите для изменения порядка');
    }

    const badge = document.createElement('span');
    badge.className = 'order-badge';
    badge.textContent = '1';

    const arrowsWrapper = document.createElement('div');
    arrowsWrapper.className = 'order-arrows-wrapper';

    const upBtn = document.createElement('button');
    upBtn.type = 'button';
    upBtn.className = 'btn-order-move btn-order-up';
    upBtn.title = 'Переместить выше';
    upBtn.innerHTML = UP_ARROW_SVG;
    upBtn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      const prevRow = row.previousElementSibling;
      if (prevRow && prevRow.classList.contains('form-row') && !prevRow.classList.contains('empty-form')) {
        tbody.insertBefore(row, prevRow);
        updateInlineOrderValues(tbody);
        flashRow(row);
      }
    });

    const downBtn = document.createElement('button');
    downBtn.type = 'button';
    downBtn.className = 'btn-order-move btn-order-down';
    downBtn.title = 'Переместить ниже';
    downBtn.innerHTML = DOWN_ARROW_SVG;
    downBtn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      const nextRow = row.nextElementSibling;
      if (nextRow && nextRow.classList.contains('form-row') && !nextRow.classList.contains('empty-form')) {
        tbody.insertBefore(nextRow, row);
        updateInlineOrderValues(tbody);
        flashRow(row);
      }
    });

    arrowsWrapper.appendChild(upBtn);
    arrowsWrapper.appendChild(downBtn);

    if (dragHandle) wrapper.appendChild(dragHandle);
    wrapper.appendChild(badge);
    wrapper.appendChild(arrowsWrapper);

    reorderCell.innerHTML = '';
    reorderCell.appendChild(wrapper);
  }

  function initInline(inlineGroup) {
    const tbody = inlineGroup.querySelector('table tbody');
    if (!tbody) return;

    const rows = tbody.querySelectorAll('tr.form-row');
    rows.forEach(row => initInlineRow(row, tbody));
    updateInlineOrderValues(tbody);

    const observer = new MutationObserver(function () {
      updateInlineOrderValues(tbody);
    });
    observer.observe(tbody, { childList: true });
  }

  function initAll() {
    initChangelist();

    document.querySelectorAll('.inline-group.sortable, fieldset.sortable, .inline-group').forEach((group) => {
      if (group.querySelector('td.field-_reorder_')) {
        initInline(group);
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
  } else {
    initAll();
  }

  window.addEventListener('load', initAll);

  if (typeof django !== 'undefined' && django.jQuery) {
    django.jQuery(document).on('formset:added', function (event, $row) {
      const row = $row[0];
      const tbody = row.closest('tbody');
      if (tbody) {
        initInlineRow(row, tbody);
        updateInlineOrderValues(tbody);
      }
    });
  }
})();
