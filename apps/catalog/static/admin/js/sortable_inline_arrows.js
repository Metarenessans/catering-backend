(function () {
  'use strict';

  function updateOrderValues(tbody) {
    if (!tbody) return;
    const rows = Array.from(tbody.querySelectorAll('tr.form-row:not(.empty-form)'));
    rows.forEach((row, index) => {
      const orderVal = index + 1;
      const orderInput = row.querySelector('input._reorder_');
      if (orderInput) {
        orderInput.value = orderVal;
      }
      const badge = row.querySelector('.order-badge');
      if (badge) {
        badge.textContent = orderVal;
      }
      const upBtn = row.querySelector('.btn-order-up');
      if (upBtn) {
        upBtn.disabled = index === 0;
      }
      const downBtn = row.querySelector('.btn-order-down');
      if (downBtn) {
        downBtn.disabled = index === rows.length - 1;
      }
    });
  }

  function flashRow(row) {
    row.classList.remove('row-moved-highlight');
    void row.offsetWidth; // trigger reflow
    row.classList.add('row-moved-highlight');
  }

  function initRowArrows(row, tbody) {
    if (row.classList.contains('empty-form')) return;
    const reorderCell = row.querySelector('td.field-_reorder_');
    if (!reorderCell || reorderCell.querySelector('.reorder-cell-content')) return;

    const dragHandle = reorderCell.querySelector('.drag.handle') || reorderCell.querySelector('.drag');

    const wrapper = document.createElement('div');
    wrapper.className = 'reorder-cell-content';

    const badge = document.createElement('span');
    badge.className = 'order-badge';
    badge.textContent = '1';

    const arrowsWrapper = document.createElement('div');
    arrowsWrapper.className = 'order-arrows-wrapper';

    const upBtn = document.createElement('button');
    upBtn.type = 'button';
    upBtn.className = 'btn-order-move btn-order-up';
    upBtn.title = 'Переместить выше';
    upBtn.innerHTML = '▲';
    upBtn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      const prevRow = row.previousElementSibling;
      if (prevRow && prevRow.classList.contains('form-row') && !prevRow.classList.contains('empty-form')) {
        tbody.insertBefore(row, prevRow);
        updateOrderValues(tbody);
        flashRow(row);
      }
    });

    const downBtn = document.createElement('button');
    downBtn.type = 'button';
    downBtn.className = 'btn-order-move btn-order-down';
    downBtn.title = 'Переместить ниже';
    downBtn.innerHTML = '▼';
    downBtn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      const nextRow = row.nextElementSibling;
      if (nextRow && nextRow.classList.contains('form-row') && !nextRow.classList.contains('empty-form')) {
        tbody.insertBefore(nextRow, row);
        updateOrderValues(tbody);
        flashRow(row);
      }
    });

    arrowsWrapper.appendChild(upBtn);
    arrowsWrapper.appendChild(downBtn);

    if (dragHandle) {
      wrapper.appendChild(dragHandle);
    }
    wrapper.appendChild(badge);
    wrapper.appendChild(arrowsWrapper);

    reorderCell.appendChild(wrapper);
  }

  function initInline(inlineGroup) {
    const tbody = inlineGroup.querySelector('table tbody');
    if (!tbody) return;

    const rows = tbody.querySelectorAll('tr.form-row');
    rows.forEach((row) => initRowArrows(row, tbody));
    updateOrderValues(tbody);

    const observer = new MutationObserver(function () {
      updateOrderValues(tbody);
    });
    observer.observe(tbody, { childList: true });
  }

  function initAll() {
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

  if (typeof django !== 'undefined' && django.jQuery) {
    django.jQuery(document).on('formset:added', function (event, $row, formsetName) {
      const row = $row[0];
      const tbody = row.closest('tbody');
      if (tbody) {
        initRowArrows(row, tbody);
        updateOrderValues(tbody);
      }
    });
  }
})();
