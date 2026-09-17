/* sobor.io — the Cal.com booking embed.
   Separate from sobor.js because it is the only thing on the page that talks to a
   third party, and because the CSP has to name app.cal.com for this file alone.

   Cal publishes this as an inline <script> snippet. The CSP here has no
   'unsafe-inline' for script, so it lives in a file instead — same code, fetched
   from 'self'. The loader it defines appends https://app.cal.com/embed/embed.js,
   which is why script-src names that origin in vercel.json.

   The event, the namespace and the mount point all come off #cal-mount's data
   attributes, so tools/build.py stays the only place the Cal link is written. */
(function () {
  'use strict';

  var mount = document.getElementById('cal-mount');
  if (!mount) return;                        // page without a booking section

  var calLink = mount.getAttribute('data-cal-link');
  var ns = mount.getAttribute('data-cal-namespace');
  if (!calLink || !ns) return;

  /* ---------- vendor loader, from cal.com's own embed snippet ---------- */
  (function (C, A, L) {
    var p = function (a, ar) { a.q.push(ar); };
    var d = C.document;
    C.Cal = C.Cal || function () {
      var cal = C.Cal;
      var ar = arguments;
      if (!cal.loaded) {
        cal.ns = {};
        cal.q = cal.q || [];
        d.head.appendChild(d.createElement('script')).src = A;
        cal.loaded = true;
      }
      if (ar[0] === L) {
        var api = function () { p(api, arguments); };
        var namespace = ar[1];
        api.q = api.q || [];
        if (typeof namespace === 'string') {
          cal.ns[namespace] = cal.ns[namespace] || api;
          p(cal.ns[namespace], ar);
          p(cal, ['initNamespace', namespace]);
        } else {
          p(cal, ar);
        }
        return;
      }
      p(cal, ar);
    };
  })(window, 'https://app.cal.com/embed/embed.js', 'init');

  /* ---------- the sobor embed ---------- */
  var Cal = window.Cal;
  Cal('init', ns, { origin: 'https://app.cal.com' });

  var api = Cal.ns[ns];

  api('inline', {
    elementOrSelector: '#cal-mount',
    calLink: calLink,
    config: { layout: 'month_view', useSlotsViewOnSmallScreen: 'true' }
  });

  /* The embed does not inherit the page's colours, so it is told the theme
     explicitly. 'auto' is Cal's own name for following the OS, which is what this
     site means by no stored choice — see assets/theme.js. */
  function theme() {
    try {
      var t = localStorage.getItem('sobor.theme');
      return t === 'light' || t === 'dark' ? t : 'auto';
    } catch (e) { return 'auto'; }
  }

  function paint() {
    api('ui', { theme: theme(), hideEventTypeDetails: false, layout: 'month_view' });
  }

  paint();

  /* Follow the capsule in the footer. sobor.js owns the buttons and the storage;
     this only listens, so the two scripts stay independent of each other's order. */
  Array.prototype.forEach.call(document.querySelectorAll('[data-theme-set]'), function (b) {
    b.addEventListener('click', paint);
  });
})();
