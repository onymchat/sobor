/* sobor.io — site theme.
   One job: the AUTO | LIGHT | DARK capsule in the footer, remembered across visits.
   The pre-paint half lives in assets/theme.js; this is the part that reacts to a
   click. The booking embed is in assets/cal.js, and nothing else here talks to a
   network. */
(function () {
  'use strict';

  /* ---------- theme: auto | light | dark, remembered ---------- */
  var root = document.documentElement;
  var themeButtons = Array.prototype.slice.call(document.querySelectorAll('[data-theme-set]'));

  function readTheme() {
    try {
      var t = localStorage.getItem('sobor.theme');
      return t === 'light' || t === 'dark' ? t : 'auto';
    } catch (e) { return 'auto'; }
  }

  function applyTheme(mode) {
    if (mode === 'auto') root.removeAttribute('data-theme');
    else root.setAttribute('data-theme', mode);
    themeButtons.forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-theme-set') === mode));
    });
    try {
      if (mode === 'auto') localStorage.removeItem('sobor.theme');
      else localStorage.setItem('sobor.theme', mode);
    } catch (e) {}
  }

  themeButtons.forEach(function (b) {
    b.addEventListener('click', function () { applyTheme(b.getAttribute('data-theme-set')); });
  });
  applyTheme(readTheme());
})();
