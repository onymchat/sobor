# sobor.io

Static site for **sobor** — a five-day contest in Bar, Montenegro, 21–25 September 2026,
to implement open seats in the [Onym](https://onym.foundation) network.

Implemented from the Claude Design canvas `Sobor Site.dc.html`
(project `3c76e8b2-8add-48eb-8519-b6ae7106f818`), which contains two artboards:
Home at 1440 dark and Home at 390 light. Both are one page, so the build is one
responsive document rather than two.

## Layout

| Path | What it is |
|---|---|
| `content/i18n.json` | **Every string on the site, in all three languages. Edit here.** |
| `tools/build.py` | Renders the pages from `i18n.json`. Python stdlib only. |
| `tools/favicon.py` | Redraws the icons from the mark's geometry. Needs Pillow. |
| `tools/register.py` | Folds the RSVP register off the Stellar ledger. Stdlib only. |
| `content/rsvp.json` | The sobor account, amount and event id. |
| `content/register.json` | **Generated** by `tools/register.py`. |
| `public/.well-known/stellar.txt` | SEP-1; served at `/.well-known/stellar.toml`. |
| `tools/lang-test.js` | 27 locale-routing cases against a stubbed browser. |
| `public/{,ru/,cnr/}index.html` | **Generated — do not edit by hand.** |
| `public/sitemap.xml`, `robots.txt` | Generated too. |
| `public/assets/sobor.css` | Tokens + every component. Dark by default. |
| `public/assets/sobor.js` | Theme capsule, seat multi-select, Stellar key validation. |
| `public/assets/theme.js` | Pre-paint theme. Blocking `<script src>` in `<head>`. |
| `public/assets/lang.js` | Pre-paint locale routing. Same rule: blocking, never deferred. |
| `public/favicon.*`, `apple-touch-icon.png`, `icon-512.png` | **Generated** by `tools/favicon.py`. |
| `design-prompt.md` | The brief the canvas was drafted from. |
| `.design/Sobor Site.dc.html` | The canvas source, decoded, for reference. |

No framework, no bundler, no dependencies — the same idiom as `onym.app`. The generator
is a local step, not a deploy step: Vercel serves the committed output as-is.

```sh
python3 tools/build.py           # regenerate after editing content/i18n.json
python3 tools/build.py --check   # non-zero if the committed output is stale
```

Three hand-kept copies of one page would drift, which is why the pages are generated
from a single string file — the same reason `onym.foundation` generates `site/` from
`pages/` and fails CI on drift. `--check` is that guard; run it before you commit.

## Icons

`favicon.svg` is the nav mark as a tile and is what modern browsers use; `favicon.ico`
(48/32/16), `apple-touch-icon.png` (180) and `icon-512.png` are rasterised from the same
geometry by `tools/favicon.py`, which redraws the mark rather than tracing the SVG —
there is no rasteriser in the toolchain.

Two deliberate departures from the inline SVG. The raster icons sit on a solid
`#0e0e10` tile, because a bare monochrome mark vanishes against one tab-strip theme or
the other. And the 16px layer draws a single centre dot instead of the ring of eight —
at that size they merge into a blob. Both are the usual favicon compromises; the SVG and
the larger sizes are faithful.

Pillow is needed only to regenerate. The output is committed, so a normal checkout and
deploy needs nothing.

## Languages

English at `/`, Russian at `/ru/`, Montenegrin at `/cnr/`. Every page carries `hreflang`
for all three plus `x-default`, and the footer switcher is real `<a href>` — it works
with JavaScript off and crawlers follow it.

**A translated path is a request, not a suggestion.** `/ru/` and `/cnr/` are always
served as asked and never redirected away, so a link shared with someone whose browser
is set to another language still opens the page that was shared. Landing on one also
remembers it. Only `/` means "you decide".

At `/`, `assets/lang.js` picks the language in this order of authority:

1. `?lang=en|ru|cnr` in the URL — explicit, and remembered (it also overrides the path)
2. a choice made earlier on the switcher (`localStorage['sobor.lang']`)
3. a same-site referrer — following a link keeps you in the language you were reading
4. `navigator.languages`, in the browser's own preference order
5. English

An explicit choice always outranks the browser, so the site never argues with someone
who has already told it what they want.

`node tools/lang-test.js` runs the whole matrix — 27 cases — against a stubbed browser. Crawlers are never redirected — the UA allowlist
is inherited from `onym.app` — or `hreflang` would be self-contradictory. A session
counter caps redirects at two hops, so no storage quirk can trap a reader in a loop.

Montenegrin browsers rarely send `cnr`; the tags that actually arrive from the region are
`sr`, `sr-Latn-ME`, `bs`, `hr`, `sh` and `me`, and all of them map to `/cnr/`.

Russian terminology follows `onym.app/ru` deliberately — **Курьер** for message carriage,
**Нотариус** for group verification, **Личность** for identity. Keep it consistent with
the sibling site rather than re-coining terms here.

The Russian headline uses **Гомстед его.** — the libertarian loanword, which Montelibero
readers will know from the homesteading principle. The rest of the Russian copy still
renders "homestead" as *занять / занимать* (`Выбери, построй, займи`, `Займи место`,
`Место не выдают. Его занимают.`). That is a live inconsistency: decide whether Гомстед
is the term throughout, or only the headline's one hard stress.

> **The RU and CNR copy is a first pass and has not been reviewed by a native speaker.**
> Have both read before the event, particularly the arbiter and prize-fund wording, where
> the exact promise matters.

## Design system

Colour, type, radii, and glass come from the Onym design system, verbatim from
`onym-website/public/assets/onym.css`. **Style through the `--on-*` tokens, never with a
literal colour.** The canvas also links `@onym/design` (the iOS component kit); it is not
used here and should not be — those components are phone screens, not a marketing page.

Dark is the default. `html[data-theme="light"]` switches; with no attribute the OS
preference wins. A pre-paint script in `<head>` applies the stored choice before first
paint, so there is no flash.

## Preview

```sh
python3 -m http.server 8791 --directory public
# → http://localhost:8791
```

## Deployment

Live at **https://sobor.io** — Vercel project `onym/sobor`, static, no build step.

```sh
vercel deploy --prod        # ship
vercel deploy               # preview URL
```

`vercel.json` sets `outputDirectory: public`, `cleanUrls`, and the security headers.
The CSP is strict — `default-src 'none'`, no `unsafe-inline` for script or style — which
is why there is **no inline `<script>` and no inline `style=` attribute anywhere in
`index.html`**. Keep it that way: the pre-paint theme snippet lives in
`assets/theme.js` as a blocking `<script src>` in `<head>` (never `defer`, or the page
flashes the wrong theme), and the fund meter takes its width from the `--so-meter`
custom property rather than an inline style.

Asset `Cache-Control` is deliberately short (1h + SWR) because the filenames are not
content-hashed; a long immutable cache would strand people on stale CSS.

Deployment protection is `all_except_custom_domains`: the `*.vercel.app` URLs require a
Vercel login, `sobor.io` is public. That also keeps the preview URLs out of search
results, so the custom domain is the only indexable copy.

### DNS

`sobor.io` is on Cloudflare nameservers (`marjory`/`elijah.ns.cloudflare.com`).

| Type | Name | Value | Proxy |
|---|---|---|---|
| A | `sobor.io` | `216.198.79.1` | **DNS only** |
| A | `sobor.io` | `64.29.17.1` | **DNS only** |
| CNAME | `www` | `753f29c2d25c320d.vercel-dns-017.com` | **DNS only** |

`www` is a 301 to the apex, configured on the Vercel side rather than in DNS.

**The orange cloud must stay off.** Vercel terminates TLS and issues the Let's Encrypt
certificate itself; proxying through Cloudflare breaks the ACME challenge and can produce
redirect loops. This is the same rule `onym.foundation` follows for its droplet.

Cloudflare credentials live in `.env` (gitignored; see `.env.example` for the scopes —
Zone:DNS:Edit and Zone:Zone:Read on `sobor.io` only).

## Content rules — keep these

Three facts are unsettled and the page says so, in its most prominent band:
the **venue** is undetermined, the **arbiter** is unnamed and is not the organizer,
and the **prize fund** is €0 secured. Do not soften these into "coming soon" or a
countdown. When one settles, swap `.tag.open` for `.tag.settled`, change the label,
and replace the paragraph — the switch points are marked with HTML comments.

The prize meter reads what has actually cleared. A pledge that has not cleared is not
a number on that page.

## How an RSVP is recorded

An RSVP is a **Stellar payment carrying a text memo**. There is no database, no session,
and no account of ours that anyone has to trust.

```
from    the joiner's own account
to      the sobor account (content/rsvp.json)
amount  0.0000001 XLM — one stroop, a signal and not a price
memo    MEMO_TEXT, e.g.  sobor2026 p 0009
```

### The memo grammar

```
sobor2026 p 0009     in person · seats Discovery + Device backup
sobor2026 r ffff     remote · all sixteen seats
sobor2026 p 0000     coming · no seat picked
sobor2026 out        withdrawing an earlier RSVP
```

Field three is a sixteen-bit hex mask, one bit per seat, **in the order of
`seats.items` in `content/i18n.json`, lowest bit first**. That order is published on the
page under "How to read this memo" so anyone can decode a memo without asking us.
Sixteen bytes worst case, against `MEMO_TEXT`'s 28-byte limit.

Reordering those seats would silently change what every memo already on the ledger
means. If the list ever has to change, bump `event` in `content/rsvp.json` instead.

Latest transaction per sender wins; `out` is a tombstone. `tools/register.py` folds the
account's payment history into `content/register.json`, which `build.py` renders into the
page. Two Horizon reads — the payment list, then each sender's MTLAP/MTLAC balance for
the pre-approved count.

### Why not SEP-10

SEP-10 proves control of an account for the length of a *session*, which then needs a
backend to store the RSVP. A submitted transaction proves control **and is** the record,
and the network enforces the account's signer thresholds — so a multisig MTLA account
works natively instead of us reimplementing threshold checks. A multisig joiner can route
the transaction through `eurmtl.me/sign_tools`, the same way Council decisions are signed.

### SEP-0007

The button builds a `web+stellar:pay` URI and hands it to whatever wallet has registered
the handler. `network_passphrase` is omitted, which means the public network.

`asset_code=XLM` is sent explicitly even though SEP-7 treats an absent asset as XLM —
some wallets open the request with **no asset selected** unless it is named. `asset_issuer`
stays absent, and that is what makes it the native asset rather than somebody's token that
calls itself XLM. Do not add an issuer.

`msg` is kept ASCII (a plain hyphen, not an em dash) because it is rendered inside the
wallet, where encoding handling is less predictable than in a browser.

`origin_domain` is deliberately **not** sent. SEP-7 expects it alongside a `signature`
made with a key published in the site's `stellar.toml`, and wallets flag an unsigned
origin claim — so claiming an origin we cannot prove is worse than claiming none. Signing
the URI is the obvious next step and needs a signing key sobor does not have yet.

Not every browser has a `web+stellar` handler registered, so the block also shows the
destination, amount and memo as copyable fields. The RSVP works by hand.

### The account

```
GB4SFOGWLZNETGEWCQVD4A6BVE3CAEAKLJXNXJDHZR2KVTP3VOUSOBOR
```

A vanity key ending in `SOBOR`. It holds nothing and spends nothing — it is a mailbox,
and losing its key would not erase a single RSVP, because the register lives in ledger
history rather than in the account.

`content/rsvp.json` carries it; `build.py` verifies the strkey checksum and refuses to
build on a typo. Set it back to `""` and the page honestly reports the account as
unpublished instead of rendering a button that signs against nothing.

### Verifying the site owns the account

`public/.well-known/stellar.toml` (SEP-1) is half of the link: the site names the
account. It is stored as `stellar.txt` and rewritten onto the `.toml` path — Vercel
derives `Content-Type` from the extension and ignores a custom one for static files, and
SEP-1 wants `text/plain` so browsers render it instead of downloading it. The mandatory
part, `Access-Control-Allow-Origin: *`, is set on both paths. The other half is **on the account — set its `home_domain` to `sobor.io`**,
which needs a `setOptions` transaction from its key and has not been done yet.

Until both halves exist there is no on-chain way to tell a real RSVP request from one
served by a lookalike domain with a different destination. For a flow that asks people
to send a payment, that is worth closing.

## Not done yet

- **`home_domain` is not set on the account**, so the site/account link is one-sided.
- **The SEP-7 URI is unsigned.** Needs a signing key and a `.well-known/stellar.toml`
  before wallets will show the request as verified.
- **No QR code.** Desktop browsers without a `web+stellar` handler currently fall back to
  copy-by-hand; a QR would let them hand off to a phone wallet.
- **RU and CNR are unreviewed.** See the warning above.
- **Only the Home page exists.** The canvas has no Seats, Status, or RSVP-confirmation
  artboard; `#rules` and `#status` are in-page anchors, not separate pages.
