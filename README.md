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
| `tools/lang-test.js` | 27 locale-routing cases against a stubbed browser. |
| `public/{,ru/,cnr/}index.html` | **Generated — do not edit by hand.** |
| `public/sitemap.xml`, `robots.txt` | Generated too. |
| `public/assets/sobor.css` | Tokens + every component. Dark by default. |
| `public/assets/sobor.js` | The theme capsule. That is now its only job. |
| `public/assets/cal.js` | The Cal.com booking embed. The only third party on the page. |
| `public/assets/theme.js` | Pre-paint theme. Blocking `<script src>` in `<head>`. |
| `public/assets/lang.js` | Pre-paint locale routing. Same rule: blocking, never deferred. |
| `public/favicon.*`, `apple-touch-icon.png`, `icon-512.png` | **Generated** by `tools/favicon.py`. |
| `public/assets/{rinat,andy}.jpg` | The two portraits. Square, EXIF stripped. |
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

## Portraits

`assets/rinat.jpg` (480²) and `assets/andy.jpg` (423²) are the two faces in the
**Who runs it** band, which sits second, directly under the booking calendar. They are
drawn as circles with no card around them — a border and a fill would be two more lines
on a page whose argument is that there is nothing between you and the thing. Both are cropped square on disk rather than by CSS, so the file
that ships is the crop that shows; `object-fit: cover` is only there to defend against
a replacement that is not square.

Both were stripped of EXIF, XMP and Photoshop blocks before committing — a phone photo
carries a camera model, a timestamp and sometimes GPS, and none of that belongs on a
public page. Two things to know if you replace one:

- **Strip the metadata, then check the picture is still the right way up.** Orientation
  often lives *in* the EXIF that gets stripped, so an image that looked correct in
  Preview can land upside down once it is clean. Bake the rotation into the pixels
  (`sips -r 180`, say) rather than relying on the tag.
- Keep them square and keep them small; they are drawn at 104px, 88px on mobile.

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

The status band carries three facts and says exactly where each one stands. All three
are now settled: the **venue** is Montelibero City, the **arbiter** is Andy and is not
the organizer, and the **prize fund** is €1,000 secured. Do not soften these into
"coming soon" or a countdown, and do not re-open one in words while the tag stays green.
Each fact is set at display size with a quiet label under it, because the venue and the
prize are what people scan the page for. State lives in `STATUS_STATE` in
`tools/build.py` and colours the dot on the label — red `.dot`, green `.dot.settled`;
the value, the label and the paragraph are `content/i18n.json` (`*_value`, `*_label`,
`*_p`).

The order matters and is a promise the page keeps: the arbiter is named **because** the
fund is secured, which is what the fund section says it would take. Naming an arbiter
over an empty fund would make that paragraph a lie.

The prize figure reads what has actually cleared. A pledge that has not cleared is not
a number on that page. The meter beneath it draws a *share of a target*, so it renders
only once `FUND_TARGET` is set in `tools/build.py` — with no published target there is
no share, and a bar sitting at 0% under a non-zero figure just reads as a bug.

## Booking

Participants book a slot through **Cal.com** — event `enikeev/sobor`, embedded inline in
the page's first section, directly under the hero, with the team band right beneath it. There is no form of our own, no database, and no account of
ours anyone has to trust with anything beyond what Cal.com already holds.

```
link        enikeev/sobor          (tools/build.py — CAL_LINK)
namespace   sobor                  (tools/build.py — CAL_NS)
mount       <div id="cal-mount">   layout month_view, slots view when narrow
```

`build.py` writes the link and namespace onto `#cal-mount` as data attributes, and
`assets/cal.js` reads them back. That keeps the Cal link in exactly one place; changing
the event means editing `CAL_LINK` and rebuilding, not touching the JavaScript.

**The `cal.com/enikeev/sobor` link under the embed stays.** It is not a fallback that
JavaScript removes — it is the path for a reader with the iframe blocked, with the embed
failing to load, or with JavaScript off entirely. Do not hide it when the embed works.

Cal publishes its embed as an inline `<script>` snippet, and also as an
`@calcom/embed-react` package. Neither is used verbatim: there is no bundler here, and
the CSP has no `'unsafe-inline'` for script, so the vendor loader lives in
`assets/cal.js` as a normal file fetched from `'self'`. The loader itself is copied
unchanged from Cal's snippet — keep it that way, so it can be re-synced from their docs.

The embed does not inherit the page's colours, so `cal.js` passes the theme explicitly
and re-passes it when the footer capsule is clicked. `auto` is Cal's own name for
following the OS, which is what this site means by no stored choice.

### What the CSP had to give up

Three additions, and one real concession:

| Directive | Why |
|---|---|
| `script-src https://app.cal.com` | `cal.js` appends `app.cal.com/embed/embed.js`. |
| `frame-src https://app.cal.com` | The booking iframe is served from there. |
| `font-src https://cal.com` | `@font-face` in the stylesheet `embed.js` injects. |
| `style-src 'unsafe-inline'` | **The concession.** See below. |

`embed.js` does `document.head.appendChild(document.createElement("style")).innerHTML =
…` in the parent document, unconditionally. A hash cannot cover it, because the CSS
changes with the embed version. So `style-src` carries `'unsafe-inline'` where it used
to carry `'self'` alone.

`script-src` does **not** have `'unsafe-inline'` and must not get it — that is the
directive that matters, and the no-inline-`<script>` rule for the generated pages still
holds. The inline `style=` attribute rule also still holds: nothing in `index.html`
carries one, and the fund meter still takes its width from `--so-meter` in the
stylesheet rather than from a `style=` attribute the generator writes.

If the concession is ever unacceptable, the fix is to drop the inline embed and keep only
the link to `cal.com/enikeev/sobor`, which needs no CSP changes at all.

### What replaced what

The RSVP used to be a **Stellar payment carrying a text memo** — no form, no database,
the ledger as the register. That flow is gone, along with `tools/register.py`,
`content/rsvp.json`, `content/register.json`, the SEP-7 wallet button, the sixteen-bit
seat mask, and `public/.well-known/stellar.txt` (SEP-1), which existed only to name the
account that received the payments.

**One RSVP was on the ledger when it was removed** — `GCR3GN73U3G4CHAHPINTWZGH2ZIRTVZ4WNHWYSB3FZOU63W22IGRINAT`,
in person, seat Interface, pre-approved. The ledger still has it; the site no longer
reads it. If that person should be carried over, they have to be asked to book a slot,
because nothing about a Cal.com booking can be derived from a Stellar transaction. The
history is recoverable from git if the flow is ever wanted back.

The account `GB4SFOGWLZNETGEWCQVD4A6BVE3CAEAKLJXNXJDHZR2KVTP3VOUSOBOR` is unchanged and
still holds nothing. It is simply no longer mentioned on the site.

## Not done yet

- **RU and CNR are unreviewed.** See the warning above — the booking copy is new and
  unreviewed too.
- **The Cal.com event's own settings are not in this repo.** Availability, duration,
  questions and confirmation mail live in the Cal.com dashboard; the repo only knows the
  link. A change there is invisible to `--check`.
- **`style-src 'unsafe-inline'`** is the price of the inline embed. See above.
- **Only the Home page exists.** `#rules` and `#status` are in-page anchors, not separate
  pages.
