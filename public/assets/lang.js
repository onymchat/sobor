/* Locale routing. Blocking <script src> in <head> so the swap happens before paint.
   Order of authority: ?lang= → a remembered choice → a same-site referrer → the browser.
   An explicit choice always wins and is remembered, so this never fights the reader. */
(function () {
  'use strict';

  var LOCALES = { en: '/', ru: '/ru/', cnr: '/cnr/' };
  var KEY = 'sobor.lang';

  /* Remember a click on the footer switcher. Capture phase, so it lands before navigation. */
  try {
    document.addEventListener('click', function (e) {
      var a = e.target && e.target.closest ? e.target.closest('a[data-lang]') : null;
      if (a && LOCALES[a.getAttribute('data-lang')]) {
        try { localStorage.setItem(KEY, a.getAttribute('data-lang')); } catch (_) {}
      }
    }, true);
  } catch (e) {}

  try {
    /* Crawlers see exactly the URL they asked for — never redirect them, or hreflang breaks. */
    if (/bot|crawler|crawling|spider|slurp|bingpreview|headlesschrome|google-inspectiontool|chrome-lighthouse|gptbot|oai-searchbot|claude|anthropic|perplexity|yandex|duckduck|applebot|baiduspider|facebookexternalhit|twitterbot|discordbot|telegrambot|whatsapp|linkedinbot|pinterest|petalbot|semrush|ahrefs|mj12|dataforseo|screaming frog/i.test(navigator.userAgent || '')) return;

    var path = location.pathname;
    var hash = location.hash;
    var here = /^\/ru(\/|$)/.test(path) ? 'ru' : (/^\/cnr(\/|$)/.test(path) ? 'cnr' : 'en');
    var q = new URLSearchParams(location.search).get('lang');
    var want = null;

    /* A translated path is itself a request. Someone followed a link to /ru/ or /cnr/,
       and a shared link has to survive the recipient's browser settings — so serve it,
       remember it, and never bounce. Only the root "/" is treated as "you decide". */
    if (here !== 'en' && !(q && LOCALES[q] && q !== here)) {
      try { localStorage.setItem(KEY, here); } catch (_) {}
      try { sessionStorage.removeItem('sobor.rc'); } catch (_) {}
      if (q) { try { history.replaceState(null, '', path + hash); } catch (_) {} }
      return;
    }

    /* 1. explicit ?lang= */
    if (q && LOCALES[q]) {
      want = q;
      try { localStorage.setItem(KEY, q); } catch (_) {}
    }

    /* 2. a choice made earlier */
    if (!want) {
      var saved = null;
      try { saved = localStorage.getItem(KEY); } catch (_) {}
      if (saved && LOCALES[saved]) want = saved;
    }

    /* 3. arrived from our own site — respect the language of the page they came from */
    if (!want && document.referrer) {
      var same = false;
      try { same = new URL(document.referrer).host === location.host; } catch (_) {}
      if (same) want = here;
    }

    /* 4. the browser's own preference order */
    if (!want) {
      var langs = navigator.languages && navigator.languages.length
        ? navigator.languages : [navigator.language || ''];
      for (var i = 0; i < langs.length && !want; i++) {
        var l = String(langs[i]).toLowerCase();
        /* Montenegrin browsers rarely send "cnr" — the region's tags are sr/bs/hr/sh/me. */
        if (/^(cnr|sr|bs|hr|sh|me)\b/.test(l) || l === 'sr-me' || l === 'sr-latn-me') want = 'cnr';
        else if (/^ru\b/.test(l)) want = 'ru';
        else if (/^en\b/.test(l)) want = 'en';
      }
      if (!want) want = 'en';
    }

    if (want !== here) {
      /* Hard stop after two hops, so a storage quirk can never trap someone in a loop. */
      var n = 0;
      try { n = parseInt(sessionStorage.getItem('sobor.rc') || '0', 10) || 0; } catch (_) {}
      if (n >= 2) { try { sessionStorage.removeItem('sobor.rc'); } catch (_) {} return; }
      try { sessionStorage.setItem('sobor.rc', n + 1); } catch (_) {}

      var rest = path.replace(/^\/(ru|cnr)(?=\/|$)/, '') || '/';
      var to = LOCALES[want].replace(/\/$/, '') + rest;
      location.replace((to || '/') + hash);
      return;
    }

    try { sessionStorage.removeItem('sobor.rc'); } catch (_) {}
    /* Tidy ?lang= out of the address bar once it has been honoured. */
    if (q) { try { history.replaceState(null, '', path + hash); } catch (_) {} }
  } catch (e) {}
})();
