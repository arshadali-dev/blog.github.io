(function () {
  var browser = document.querySelector('.home-category-browser');
  var tabs = Array.from(browser.querySelectorAll('[data-category]')).filter(function (element) {
    return element.tagName === 'A';
  });
  var panels = Array.from(browser.querySelectorAll('.home-category-panel'));
  var status = browser.querySelector('.home-category-status');
  var pagination = browser.querySelector('.home-category-pagination');
  var pageLabel = browser.querySelector('.home-category-page');
  var previous = pagination.querySelector('[data-page="previous"]');
  var next = pagination.querySelector('[data-page="next"]');
  var pageSize = Number(browser.dataset.pageSize);
  var homeUrl = new URL(browser.dataset.homeUrl, window.location.origin);
  var selectedCategory;
  var selectedPage;

  function viewUrl(category, page) {
    var url = new URL(homeUrl);
    if (category !== 'data-engineering') url.searchParams.set('category', category);
    if (page > 1) url.searchParams.set('page', page);
    return url;
  }

  function render(category, page, push) {
    var panel = panels.find(function (item) { return item.dataset.category === category; });
    var posts = Array.from(panel.querySelectorAll('.post-teaser'));
    var pageCount = Math.max(1, Math.ceil(posts.length / pageSize));
    selectedCategory = category;
    selectedPage = Math.min(pageCount, Math.max(1, Number.isSafeInteger(page) ? page : 1));

    tabs.forEach(function (tab) {
      var selected = tab.dataset.category === category;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
      tab.href = viewUrl(tab.dataset.category, 1).href;
    });
    panels.forEach(function (item) { item.hidden = item !== panel; });
    posts.forEach(function (post, index) {
      post.hidden = index < (selectedPage - 1) * pageSize || index >= selectedPage * pageSize;
    });
    status.hidden = false;
    status.textContent = panel.dataset.categoryName + ': ' + posts.length +
      (posts.length === 1 ? ' article' : ' articles') + ', page ' + selectedPage + ' of ' + pageCount + '.';
    pagination.hidden = pageCount <= 1;
    pageLabel.textContent = 'Page ' + selectedPage + ' of ' + pageCount;
    previous.hidden = selectedPage === 1;
    next.hidden = selectedPage === pageCount;
    previous.href = viewUrl(category, selectedPage - 1).href;
    next.href = viewUrl(category, selectedPage + 1).href;
    window.history[push ? 'pushState' : 'replaceState'](null, '', viewUrl(category, selectedPage));
  }

  function readUrl(initial) {
    var params = new URLSearchParams(window.location.search);
    var category = params.get('category');
    if (!panels.some(function (panel) { return panel.dataset.category === category; })) {
      category = 'data-engineering';
    }
    var page = Number(params.get('page') || (initial ? browser.dataset.initialPage : 1));
    render(category, page, false);
  }

  browser.querySelector('.home-category-tabs').setAttribute('role', 'tablist');
  panels.forEach(function (panel) {
    panel.setAttribute('role', 'tabpanel');
    panel.setAttribute('aria-labelledby', 'tab-' + panel.dataset.category);
    panel.tabIndex = 0;
  });
  tabs.forEach(function (tab, index) {
    tab.setAttribute('role', 'tab');
    tab.setAttribute('aria-controls', 'home-' + tab.dataset.category);
    tab.addEventListener('click', function (event) {
      if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      if (selectedCategory !== tab.dataset.category) render(tab.dataset.category, 1, true);
    });
    tab.addEventListener('keydown', function (event) {
      var target;
      if (event.key === 'ArrowRight') target = (index + 1) % tabs.length;
      if (event.key === 'ArrowLeft') target = (index + tabs.length - 1) % tabs.length;
      if (event.key === 'Home') target = 0;
      if (event.key === 'End') target = tabs.length - 1;
      if (target === undefined) return;
      event.preventDefault();
      tabs[target].focus();
      render(tabs[target].dataset.category, 1, true);
    });
  });
  [previous, next].forEach(function (link) {
    link.addEventListener('click', function (event) {
      if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      render(selectedCategory, selectedPage + (link === next ? 1 : -1), true);
      browser.scrollIntoView({ block: 'start' });
      panels.find(function (panel) { return !panel.hidden; }).focus({ preventScroll: true });
    });
  });
  window.addEventListener('popstate', function () { readUrl(false); });
  readUrl(true);
})();
