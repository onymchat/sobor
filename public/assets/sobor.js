/* sobor.io — the only script on the page.
   Three jobs: the theme capsule, the seat multi-select, and RSVP key validation.
   Nothing here talks to a network, because there is nothing to talk to yet. */
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

  /* ---------- RSVP: build the memo, then a SEP-0007 link ----------
     The RSVP *is* a Stellar payment carrying a 16-byte text memo. Nothing is posted
     anywhere: this only assembles the URI, and the wallet does the signing and the
     submitting. No key, no session, and no server ever holds any of it. */
  var card = document.getElementById('rsvp');
  var ACCOUNT = card && card.getAttribute('data-account');
  if (!card || !ACCOUNT) return;               // account unpublished — nothing to wire

  var EVENT = card.getAttribute('data-event');
  var AMOUNT = card.getAttribute('data-amount');
  var MSG = card.getAttribute('data-msg');
  var LBL_COPY = card.getAttribute('data-copy');
  var LBL_DONE = card.getAttribute('data-copied');

  var memoOut = document.getElementById('rsvp-memo');
  var memoAlt = document.getElementById('rsvp-memo2');
  var go = document.getElementById('rsvp-go');
  var mode = 'p';

  /* Bit n is the nth seat in the order published under "How to read this memo".
     Sixteen seats, so the mask is always four hex digits. */
  function mask() {
    var m = 0;
    var on = card.querySelectorAll('.rsvp-seats .pick[aria-pressed="true"]');
    for (var i = 0; i < on.length; i++) m |= 1 << parseInt(on[i].getAttribute('data-bit'), 10);
    return ('000' + m.toString(16)).slice(-4);
  }

  function memo() { return EVENT + ' ' + mode + ' ' + mask(); }

  /* SEP-0007. asset_code=XLM is named explicitly — the spec treats an absent asset as
     XLM, but some wallets then open with no asset selected. asset_issuer stays absent,
     which is what makes it native rather than a token that calls itself XLM.
     network_passphrase is omitted, which means the public network. */
  function uri(text) {
    return 'web+stellar:pay?destination=' + encodeURIComponent(ACCOUNT) +
           '&amount=' + encodeURIComponent(AMOUNT) +
           '&asset_code=XLM' +
           '&memo=' + encodeURIComponent(text) +
           '&memo_type=MEMO_TEXT' +
           '&msg=' + encodeURIComponent(MSG);
  }

  function sync() {
    var text = memo();
    if (memoOut) memoOut.textContent = text;
    if (memoAlt) memoAlt.textContent = text;
    if (go) go.setAttribute('href', uri(text));
  }

  var seatGroup = card.querySelector('.rsvp-seats');
  if (seatGroup) {
    seatGroup.addEventListener('click', function (e) {
      var b = e.target.closest('.pick');
      if (!b || !seatGroup.contains(b)) return;
      b.setAttribute('aria-pressed', b.getAttribute('aria-pressed') === 'true' ? 'false' : 'true');
      sync();
    });
  }

  var modeGroup = card.querySelector('.rsvp-mode');
  if (modeGroup) {
    modeGroup.addEventListener('click', function (e) {
      var b = e.target.closest('[data-mode]');
      if (!b || !modeGroup.contains(b)) return;
      var all = modeGroup.querySelectorAll('[data-mode]');
      for (var i = 0; i < all.length; i++) all[i].setAttribute('aria-checked', String(all[i] === b));
      mode = b.getAttribute('data-mode');
      sync();
    });
  }

  card.addEventListener('click', function (e) {
    var b = e.target.closest('.copy');
    if (!b || !card.contains(b)) return;
    var text = b.hasAttribute('data-copy-memo') ? memo() : b.getAttribute('data-copy');
    var done = function () {
      b.textContent = LBL_DONE;
      setTimeout(function () { b.textContent = LBL_COPY; }, 1600);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () {});
    } else {
      /* http, or an older browser — select it so the reader can copy by hand */
      var el = b.parentNode.querySelector('code');
      if (el && window.getSelection) {
        var r = document.createRange(); r.selectNodeContents(el);
        var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(r);
      }
    }
  });

  sync();
})();
