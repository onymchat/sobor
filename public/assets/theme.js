/* Applied before first paint — keep this a blocking <script src> in <head>,
   never deferred, or the page flashes the wrong theme.
   Kept out of the HTML so the CSP can refuse inline script entirely. */
(function () {
  try {
    var t = localStorage.getItem('sobor.theme');
    if (t === 'light' || t === 'dark') document.documentElement.setAttribute('data-theme', t);
  } catch (e) {}
})();
