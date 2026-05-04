// Code block enhancements: line numbers, copy button, toggle
(function () {
  'use strict';

  var LINE_NUMBERS_KEY = 'codeLineNumbers';
  var lineNumbersEnabled = localStorage.getItem(LINE_NUMBERS_KEY) !== 'false';

  function addLineNumbers(pre) {
    if (pre.querySelector('.line-numbers-col')) return;
    var code = pre.querySelector('code');
    if (!code) return;

    var lines = code.textContent.split('\n');
    // Remove trailing empty line (common in fenced code blocks)
    if (lines[lines.length - 1] === '') lines.pop();

    var col = document.createElement('span');
    col.className = 'line-numbers-col';
    col.setAttribute('aria-hidden', 'true');
    for (var i = 1; i <= lines.length; i++) {
      var num = document.createElement('span');
      num.className = 'line-number';
      num.textContent = i;
      col.appendChild(num);
    }
    pre.insertBefore(col, pre.firstChild);
    pre.classList.add('has-line-numbers');
  }

  function removeLineNumbers(pre) {
    var col = pre.querySelector('.line-numbers-col');
    if (col) col.remove();
    pre.classList.remove('has-line-numbers');
  }

  function addToolbar(pre) {
    if (pre.querySelector('.code-toolbar')) return;

    var toolbar = document.createElement('div');
    toolbar.className = 'code-toolbar';

    // Copy button
    var copyBtn = document.createElement('button');
    copyBtn.className = 'code-btn code-copy-btn';
    copyBtn.title = 'Copy to clipboard';
    copyBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';
    copyBtn.addEventListener('click', function () {
      var code = pre.querySelector('code');
      if (!code) return;
      var text = code.textContent;
      navigator.clipboard.writeText(text).then(function () {
        copyBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>';
        setTimeout(function () {
          copyBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';
        }, 2000);
      });
    });

    // Toggle line numbers button
    var toggleBtn = document.createElement('button');
    toggleBtn.className = 'code-btn code-lines-btn';
    toggleBtn.title = 'Toggle line numbers';
    toggleBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="5" y2="6"/><line x1="9" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="5" y2="12"/><line x1="9" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="5" y2="18"/><line x1="9" y1="18" x2="21" y2="18"/></svg>';
    toggleBtn.addEventListener('click', function () {
      var hasNumbers = pre.classList.contains('has-line-numbers');
      if (hasNumbers) {
        removeLineNumbers(pre);
      } else {
        addLineNumbers(pre);
      }
    });

    toolbar.appendChild(toggleBtn);
    toolbar.appendChild(copyBtn);
    pre.style.position = 'relative';
    pre.appendChild(toolbar);
  }

  function init() {
    var pres = document.querySelectorAll('pre');
    pres.forEach(function (pre) {
      addToolbar(pre);
      if (lineNumbersEnabled) {
        addLineNumbers(pre);
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
