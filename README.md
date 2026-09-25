# sobor.io

Static site for **sobor** — a five-day contest in Bar, Montenegro, 21–25 September 2026,
to implement open seats in the [Onym](https://onym.foundation) network.

**The contest is over.** Sobor 26 ran 21–25 September 2026, the winners were awarded, and
on 25 September the site was cut down to a single screen: the mark, three lines, and the
language and theme controls. Everything that served a live event — the booking calendar,
the sixteen seats, the status band, the prize fund, the team, the submission deadline —
was removed. The generator, the token block, the icons and the locale routing all stayed,
so whatever the site becomes for Onym 27 starts from the same system rather than a blank
file. The removed markup is one `git show` away.

Originally implemented from the Claude Design canvas `Sobor Site.dc.html`
(project `3c76e8b2-8add-48eb-8519-b6ae7106f818`), which contains two artboards:
Home at 1440 dark and Home at 390 light. Both are one page, so the build is one
responsive document rather than two.

## Layout

| Path | What it is |
|---|---|
| `content/i18n.json` | **Every string on the site, in all three languages. Edit here.** |
| `tools/build.py` | Renders the pages from `i18n.json`. Python stdlib only. |
| `tools/favicon.py` | Redraws the icons from the mark's geometry. Needs Pillow. |
| `tools/og.py` | Redraws the three Open Graph cards from the headline. Needs Pillow. |
| `tools/lang-test.js` | 27 locale-routing cases against a stubbed browser. |
| `public/{,ru/,cnr/}index.html` | **Generated — do not edit by hand.** |
| `public/sitemap.xml`, `robots.txt` | Generated too. |
| `public/assets/sobor.css` | The token block, then the one screen. Dark by default. |
| `public/assets/sobor.js` | The theme capsule. That is now its only job. |
| `public/assets/theme.js` | Pre-paint theme. Blocking `<script src>` in `<head>`. |
| `public/assets/lang.js` | Pre-paint locale routing. Same rule: blocking, never deferred. |
| `public/favicon.*`, `apple-touch-icon.png`, `icon-512.png` | **Generated** by `tools/favicon.py`. |
| `design-prompt.md` | The brief the canvas was drafted from. Describes the event site. |
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

Russian terminology followed `onym.app/ru` deliberately — **Курьер** for message
carriage, **Нотариус** for group verification, **Личность** for identity. None of those
words appear on the one-screen site, but keep them if the site grows back, rather than
re-coining terms here.

The brand stays Latin in all three languages — **Sobor 26**, not *Собор 26* — because it
names the event, not the word. `Onym 27` likewise.

> **The RU and CNR copy is a first pass and has not been reviewed by a native speaker.**
> It is three lines now, so this is cheap to fix: have both read.

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
The CSP is still strict — `default-src 'none'`, and no `unsafe-inline` for **script** —
which is why there is **no inline `<script>` and no inline `style=` attribute anywhere in
`index.html`**. It does now allow `app.cal.com` and inline *style*, for the booking
embed; see **Booking** below for exactly what and why. Keep the rest that way: the pre-paint theme snippet lives in
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

The page states two facts in the past tense and one expectation. Sobor 26 **finished**
and the winners **were awarded** — do not soften either into a countdown, a "results
coming soon", or a re-opened call for submissions. The third line looks forward to Onym
27 and is deliberately the only forward-looking thing on the site: it carries no date,
because there is none, and it steps down in colour rather than starting a second
headline. Add a date to it only when there is one to add.

The three lines live in `content/i18n.json` under `hero` (`h1a`, `h1b`, `h1c`) and are
drawn twice — once by `tools/build.py` into the page, once by `tools/og.py` into the
Open Graph cards. Change a line and run both, or the link preview keeps saying the old
thing.

## Not done yet

- **RU and CNR are unreviewed.** See the warning above.
- **Only the Home page exists**, and now it is the whole site. There are no in-page
  anchors left to link to.
- **`design-prompt.md` and `.design/` still describe the event site.** They are kept as
  the record of what was built, not as a description of what is served.
