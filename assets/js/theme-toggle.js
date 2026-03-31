(function() {
  var toggle = document.getElementById('theme-toggle');
  var currentTheme = localStorage.getItem('theme') || 'light';

  function updateIcon(theme) {
    if (!toggle) return;
    var icon = toggle.querySelector('i');
    if (!icon) return;
    if (theme === 'dark') {
      icon.className = 'fas fa-sun';
      toggle.title = 'Switch to light mode';
    } else {
      icon.className = 'fas fa-adjust';
      toggle.title = 'Switch to dark mode';
    }
  }

  if (currentTheme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
  }
  updateIcon(currentTheme);

  if (toggle) {
    toggle.addEventListener('click', function(e) {
      e.preventDefault();
      var theme = document.documentElement.getAttribute('data-theme');
      if (theme === 'dark') {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
        updateIcon('light');
      } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
        updateIcon('dark');
      }
    });
  }
})();
