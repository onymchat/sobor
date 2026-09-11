Draft a website for **sobor.io** in this project.

### What it is
Sobor is a hackathon-style contest held the week of **21–25 September 2026** in Montenegro, in and
around **MTL City** — the startup town being built by the Montelibero movement, centred on Bar on
the Adriatic coast. Teams compete to **build a seat**: a working implementation of one of the open
roles in the Onym network (see onym.foundation). A prize fund rewards the seats that get filled.
Attendees RSVP by proving control of a **Stellar account**; accounts already known to the
Montelibero Association (MTLAP/MTLAC holders, per bsn.expert) are pre-approved and RSVP
automatically. The site ships in **English and Russian**.

### Three things are deliberately not settled, and the site must say so
- **The venue is not determined.** The week is fixed; the room is not.
- **The arbiter is not named.** The arbiter is not the organizer. They will be named as soon as the
  prize fund is secured — not before.
- **The prize fund is not secured.** Show the amount raised as what it actually is. If that is
  zero, the page says zero.

Do not soften these into "coming soon", "stay tuned", or a countdown. State them flatly and move
on. This is the house style: onym.foundation shows empty registers as empty and labels proposed
governance as proposed. Match that.

### Which design system to use
Use the **Onym web layer** — the token set below, plain semantic HTML, CSS custom properties,
page-local styles. **Do not** compose this out of the `@onym/design` React components in this
project (`Screen`, `ScreenContent`, `TabDock`, `NavBar`, `ChatBubble`, `Row`, `ListItem`,
`PrimaryButton`…). Those are the **iOS app** kit — phone screens with Liquid Glass chrome. They
share these tokens but are the wrong layer for a marketing site. There is no utility-class
vocabulary here; no Tailwind.

### Tokens — use these verbatim, never a literal color
Dark is the default. `html[data-theme="light"]` switches. With no attribute, the OS preference
wins. Design and show **both** themes.

```css
:root {
  /* surfaces */
  --on-bg: #000000;
  --on-surface: #0e0e10;
  --on-surface2: #17171a;
  --on-surface3: #1f1f23;
  /* text */
  --on-text: #f2f2f4;
  --on-text2: rgba(242,242,244,.62);
  --on-text3: rgba(242,242,244,.40);
  /* hairlines */
  --on-hairline: rgba(255,255,255,.07);
  --on-hairline-strong: rgba(255,255,255,.12);
  /* semantic */
  --on-blue: #3fa8ff;  --on-green: #34c759;  --on-red: #ff453a;
  --on-on-accent: #000000;
  /* identity accents */
  --on-accent-orange: #ff7a45;  --on-accent-blue: #3fa8ff;   --on-accent-green: #3dd66e;
  --on-accent-purple: #b278ff;  --on-accent-pink: #ff4d6d;   --on-accent-yellow: #ffc93c;
  /* liquid glass */
  --on-glass: rgba(58,58,62,.48);
  --on-glass-bd: rgba(255,255,255,.13);
  --on-glass-hi: rgba(255,255,255,.12);
  --on-glass-shadow: 0 12px 34px -8px rgba(0,0,0,.65);
  /* shape + type */
  --on-radius-card: 14px;  --on-radius-field: 12px;  --on-radius-pill: 999px;
  --on-font: -apple-system, BlinkMacSystemFont, system-ui, "Helvetica Neue", sans-serif;
  --on-font-mono: ui-monospace, SFMono-Regular, Menlo, monospace;
  --nav-bg: rgba(14,14,16,.72);
}
```

Light overrides: `--on-bg:#ffffff; --on-surface:#f5f5f7; --on-surface2:#ffffff;
--on-surface3:#ebebef; --on-text:#0a0a0c; --on-text2:rgba(10,10,12,.62);
--on-text3:rgba(10,10,12,.42); --on-hairline:rgba(0,0,0,.06);
--on-hairline-strong:rgba(0,0,0,.12); --on-blue:#1f86e0; --on-green:#1fa84a; --on-red:#e5392e;
--on-on-accent:#ffffff; --on-accent-orange:#e85f2a; --on-accent-purple:#8b4deb;
--on-accent-pink:#e03253; --on-accent-yellow:#d9a400; --on-glass:rgba(255,255,255,.58);
--on-glass-bd:rgba(255,255,255,.60); --on-glass-hi:rgba(255,255,255,.90);
--on-glass-shadow:0 10px 32px -6px rgba(24,24,40,.22); --nav-bg:rgba(245,245,247,.72);`

The page ground is `--on-surface`, not `--on-bg`.

### Type and rhythm — copy these numbers
- Container: `width: min(1180px, calc(100% - 48px)); margin: auto`. Prose-only pages narrow to
  `max-width: 820px`. Nav height **58px on the home page, 52px on inner pages**, fixed,
  `backdrop-filter: saturate(160%) blur(16px)`, 1px `--on-hairline` bottom border.
- `h1`: `clamp(64px, 10vw, 138px)`, `line-height: .88`, `letter-spacing: -.065em`, max-width 1100px.
- `h2`: `clamp(48px, 6.5vw, 88px)`, `line-height: .95`, `letter-spacing: -.055em`.
- `h3` in a card: 30px, `letter-spacing: -.035em`. Step headings `clamp(42px,5vw,70px)`,
  `line-height: .98`, `letter-spacing: -.05em`.
- All display headings get `text-wrap: balance`.
- Lead paragraph: `clamp(20px, 2.3vw, 30px)`, `line-height: 1.25`, `letter-spacing: -.02em`,
  `--on-text2`. Section paragraph 20px / 1.45. Card body 15px / 1.48.
- **Measure is always capped in `ch`** — 56ch to 64ch. Never let a paragraph run the container.
- `.eyebrow`: 12.5px, weight 500, `letter-spacing: .14em`, uppercase, `--on-text2`.
- `.number`: **mono**, 11px, `letter-spacing: .12em`, `--on-text2`. Every numeric value on the
  site — account keys, amounts, dates, counts — is mono.
- Hero: `min-height: 100svh`, padding `150px 0 90px`, flex centred. Sections: `padding: 120px 0`
  with `border-top: 1px solid var(--on-hairline-strong)`. Closing section 150px, centred.
- Breakpoints at 850px and 560px (→ sections `90px 0`, container `min(100% - 36px, 1180px)`).

### Component idiom
- **Card**: `background: --on-surface2`, `1px solid --on-hairline`, radius 14. Flat. No shadows
  anywhere except the glass treatment and the prominent button.
- **Primary button**: radius 14, min-height 44px, padding `0 20px`, 15px/600, `--on-blue` fill,
  `--on-on-accent` text, `box-shadow: 0 9px 24px color-mix(in srgb, var(--on-blue) 25%, transparent)`.
- **Secondary button**: transparent, `--on-text`, `1px solid --on-hairline-strong`; hover border
  `--on-text3`.
- **Nav CTA**: pill, `padding: 10px 17px`, `--on-blue` fill.
- **Chip**: `padding: 3px 6px`, radius **4**, 9.5px/700, `letter-spacing: .5px`, uppercase,
  `--on-surface3` background. Colored variants tint at 14%:
  `color-mix(in srgb, var(--on-blue) 14%, transparent)`. Use chips for status tags only.
- **Link**: inherits text color — links are **not** blue by default. Underline in
  `--on-hairline-strong`, `text-underline-offset: 3px`, turning `--on-blue` on hover.
- **Status pill** (for the three open facts, and for the Status page rows): `inline-flex`,
  `gap: 6px`, `1px solid --on-hairline-strong`, `padding: 3px 9px`, radius 999, **mono**,
  `.66rem`, `letter-spacing: .14em`, uppercase, `--on-text2`, preceded by a `6px` round dot at
  `opacity: .55`. Stroke the dot `--on-green` / `--on-red` when the state warrants it.
- **Selectable pill / toggle group** — the pattern for seat multi-select and the EN|RU switcher:
  transparent with a `--on-hairline-strong` border; hover brings the border to `--on-text`;
  **selected inverts** — `background: var(--on-text); color: var(--on-surface);
  border-color: var(--on-text)`. `padding: 6px 14px`, radius 999, 12.5px.
- **Text field**: `min-height: 50px`, `padding: 13px 14px`, radius 14, `--on-surface2` background,
  `1px solid --on-hairline`, 16px. Focus changes **only** the border to `--on-blue` — no ring.
  Placeholder `--on-text3`; helper text 12.5px `--on-text2`.
- **Accordion** (if the rules page needs one): native `<details>`, hairline top border per item,
  marker hidden and replaced with a `+` that becomes `−` when open, answer indented 34px.
- **Ornamental divider** (`.brick-rule`): a mono uppercase label centred between two fading
  hairlines — `linear-gradient(90deg, transparent, var(--on-hairline-strong), transparent)` on
  `::before`/`::after`.
- **Warm capstone card** — the one permitted warm accent, for the prize-fund block only:
  `border-color: rgba(240,179,94,.45)` over
  `linear-gradient(180deg, rgba(240,179,94,.10) 0%, var(--on-surface2) 70%)`, all-mono content.
- **Theme toggle**: fixed bottom-right glass capsule, radius 999, `--on-glass` background,
  `.5px solid --on-glass-bd`, `backdrop-filter: blur(20px) saturate(1.6)`, three buttons
  (Auto / Light / Dark), active one gets `--on-blue` text.
- **Multi-column grid**: a single bordered container, radius 14, `overflow: hidden`, divided by
  internal `--on-hairline-strong` borders — not separate floating cards.
- Icons are line-drawn SF-Symbols-style, round caps, 2pt stroke. **Never an external icon
  library. No stock photography. No illustration.** Diagrams are inline SVG — monochrome
  `currentColor` strokes at `stroke-width: 1–1.4`, `opacity: .22–.35`, mono labels at 7–9px.
- **Mark.** Onym's is a broken ring — two arcs with four gaps, rotated 45° — set as a 22%-radius
  squircle with a luminous halo in dark mode. Sobor needs a sibling mark of its own, drawn in the
  same hairline geometric language: assembly, convocation, a ring of seats. Propose one; do not
  reuse the Onym ring unchanged, and do not use a wordmark alone.
- Focus is visible on every interactive element: `outline: 2px solid`, `outline-offset: 3px`.

### Motion
No animation library — CSS transitions plus scroll observers. Durations: `.15s` hover/border,
`.2s` toggles, `.25s` nav background, `.3s` step and dot states, `.35s` theme swap, `.6–.8s`
scroll reveals. Easing is `ease`, except the signature reveal curve **`cubic-bezier(.2,.7,.2,1)`**.
Scroll reveal: `opacity: 0; transform: translateY(18px)` → `opacity: 1; transform: none`.
`html { scroll-behavior: smooth }`. Honour `prefers-reduced-motion: reduce` — reveals resolve
instantly, smooth scroll off.

### Voice — follow the grammar, not just the tone
- **Headlines are sentence case and end with a full stop.** The house shape is two short
  declaratives split by a line break: "Four parts.⏎No single owner." · "Own Name,⏎Your Messenger."
  Even single-word page titles take the period: "Changelog." "Press kit."
- **Headlines are never uppercase.** Uppercase with `.14–.18em` tracking is reserved for
  eyebrows, section labels, chips, and status pills.
- **The middle dot `·` is the house separator** — in eyebrows, nav breadcrumbs, footers, metadata.
- **Numbered items** are a two-digit mono number plus an uppercase qualifier: `01 · BUILD`,
  `02 · SUBMIT`, `03 · JUDGE`, `04 · FILL`.
- **Each card closes with a short bolded aphorism** — the onym.app tic. "The courier cannot read
  the letter." "A window, not a gatekeeper." Write new ones that fit this event; do not reuse those.
- Arrow-suffixed links (`Read the rules →`). Em-dashes and semicolons used freely. Short sentences.
- No exclamation marks, no hype, no "join the revolution", no urgency devices. When something
  does not exist yet, the sentence says it does not exist yet — and the site names its own limits
  rather than waiting to be asked.

Reference sentences from the family, for register — do not copy them:
"A messenger no one owns needs an institution that owns nothing."
"The courier cannot read the letter. Delivery is a service, not a vantage point."
"Deliberately anticlimactic."
"Step 03 never required steps 01–02."

The footer sign-off on onym.app is "Never pay with your identity." Write sobor's own equivalent —
one line, same weight, in mono beside the copyright.

### Artboards to draft
Lay these out on one canvas, left to right.

**1 · Home — 1440, dark.** Full page.
- Fixed glass nav: Onym-family wordmark "sobor", links (The contest · Seats · Rules · Status),
  pill CTA "RSVP".
- Hero, `100svh`. Eyebrow: `MTL CITY · MONTENEGRO · 21–25 SEPTEMBER 2026`. `h1` — something with
  the shape of "Build a seat. Take it home." Lead paragraph on the left of a
  `minmax(0,620px) auto` grid, actions on the right: primary "RSVP with a Stellar account",
  secondary "Read the rules →".
- A hairline strip directly under the hero carrying the three open facts as **status pills with
  dots**: `VENUE — UNDETERMINED` · `ARBITER — UNNAMED` · `PRIZE FUND — €0 SECURED`, each with a
  one-line plain-language expansion beneath in `--on-text2`. This is the page's most important
  element. Give it room — a full hairline-bounded band, not a footnote.
- `01 · THE CONTEST` — section head, two-column `1fr 1fr`, h2 + 20px paragraph. Then a four-cell
  bordered grid: Build · Submit · Judge · Fill. 300px min-height cells, mono number top, h3
  pushed to the bottom with `margin-top: auto`, each closing on a bolded aphorism.
- `02 · THE SEATS` — the seventeen open Onym roles, as a dense bordered grid of small cells: role
  name, a one-line "what filled means", and a chip carrying its real status
  (`DRAFT SPEC`, `IN REVIEW`, `REFERENCE OPERATOR EXISTS`, `LIVE ON iOS`). Link out to
  onym.foundation/seats.
- `03 · WHO MAY COME` — two cards: *Pre-approved* ("Your account already holds MTLAP or MTLAC.
  RSVP is one signature.") and *Everyone else* ("Register interest. We answer, or we answer
  honestly that there is nothing yet."). Mono sample account key, truncated middle.
- `04 · THE PRIZE FUND` — the **warm capstone card**, all-mono: a fund meter that reads honestly
  at zero against a stated target, plus the sponsor path. State that the arbiter is named only
  once the fund is secured, and that the arbiter is not the organizer.
- Closing centred section, then footer: left `© 2026 · sobor.io · an Onym event`, right links
  (onym.app · onym.foundation · bsn.expert), and the **EN|RU switcher as an inverted-fill mono
  pill pair**. The sign-off line in mono.

**2 · Home — 390, light.** The same page at mobile: nav collapses to wordmark + RSVP pill, hero
`h1` `clamp(60px,19vw,88px)`, the four-cell grid becomes 2×2, the seat grid becomes one column.
Show the light palette honestly — this is where `--on-surface:#f5f5f7` and the blue at `#1f86e0`
have to hold up.

**3 · RSVP — 1440, dark.** A three-step page in the shape of onym.foundation's pledge flow:
mono `STEP 1 OF 3` labels, generous vertical separation, no wizard chrome.
- **Step 1 — Prove the account.** Wallet buttons (Freighter · Albedo · Lobstr · xBull ·
  WalletConnect) as a row of bordered cards. Below: "We check the signature, never the balance —
  and we ask the network, not you, whether you already hold MTLAP." Show the connected state too:
  mono public key, a green `PRE-APPROVED` chip, and the resolved BSN display name.
- **Step 2 — Pre-select a seat (optional).** The heart of the page. A selectable grid of the
  seventeen roles grouped as the seat map groups them — **Core ring** (Interface, Message
  carriage, Media storage, Group verification), **Service market** (Audit & attestation,
  Arbitration, Discovery, Moderation authority, Recovery trustee, Device backup, Naming &
  credentials), **Application profiles** (Charitable coordination, Banking & payments,
  Distribution, Acquisition), **Organizational** (Recruitment, Sponsorship). Multi-select, using
  the **inverted-fill selected state** — `background: var(--on-text); color: var(--on-surface)`.
  Each cell: role name, status chip, one line of what it earns. Plus a final cell "Just
  attending — no seat". The word "optional" is visible and the page works with nothing selected.
- **Step 3 — Know what you are RSVPing to.** A card of flat statements: the venue is not
  determined; the arbiter is not named and is not the organizer; the prize fund is not secured;
  selecting a seat reserves nothing and competes for nothing; the RSVP is an intention, not a
  ticket; if the event does not happen, nothing was collected.
- Sticky footer bar: primary "Sign the RSVP", with mono text "One signature. Sequence 0 — the
  transaction can never reach the network."

**4 · RSVP step 2 — 390, dark.** The seat grid expanded on mobile, with two roles selected and
the group headers visible, so the selected/unselected treatment is legible.

**5 · Seats — 1440, dark.** The seventeen roles at full detail, four concentric bands rendered as
stacked bordered sections (Core ring → Service market → Application profiles → Organizational),
each role a row with name, status chip, what it does, what it earns, who it fits, and a
"Build this at sobor →" link. An inline-SVG seat-map diagram at the top: the person in the
centre, the bands around them. Nothing decorative.

**6 · Status — 1440, light.** The register page. Everything the event does and does not yet have,
as mono rows with real values and dates: venue (undetermined), arbiter (unnamed), prize fund
(€0 of a stated target), RSVPs received (a number), seats pre-selected (a breakdown by role),
pre-approved accounts (from bsn.expert, with a `last synced` timestamp). Empty things are shown
empty, with an em-dash, not hidden. A dated changelog at the bottom.

**7 · RSVP confirmation — 390, dark.** A single centred card, `min(520px,100%)`, radius 14,
padding `44px 32px`: wordmark, mono eyebrow `RSVP RECORDED`, short heading, mono public key,
the seats they picked as chips, and a plain line about what happens next and when they will
hear about the venue. Nothing celebratory.

### Copy notes
- Write every artboard's copy in **English**, and add a small Russian variant of the hero and of
  RSVP step 3 so the type scale can be checked against Cyrillic — Russian runs longer and the
  `-.065em` tracking on `h1` needs to survive it.
- "Sobor" (собор) is an assembly or council. It is a **new coinage for this community** —
  Montelibero's own word is *Собрание* / "the Assembly". Let the site carry the word with weight,
  but never imply it is established Montelibero usage.
- Say **MTL City**, not "Montelibero City".
- The week contains the Montelibero Association's third anniversary (founded 23 September 2023).
  A single restrained line, at most.

### Do not
- Do not add a countdown timer, a hero photograph, a gradient mesh, a testimonial, a logo wall of
  fictional sponsors, or a "limited seats" scarcity device.
- Do not invent a venue, an arbiter, a prize amount, a sponsor, a speaker, or a schedule.
- Do not use a shadow outside the glass elements, the prominent button, and the card `--shadow`.
- Do not use the iOS `@onym/design` components.
- Do not set a headline in uppercase, and do not leave one without its full stop.
- Do not make body links blue; the hairline underline is the affordance.
- Do not soften the three open facts.
