#!/usr/bin/env python3
"""Render public/{,ru/,cnr/}index.html from content/i18n.json.

One template, three locales. Output is committed — Vercel serves it as-is, there is
no build step at deploy time. Run this after editing content/i18n.json, and commit
the regenerated pages together with the string change.

    python3 tools/build.py          # write
    python3 tools/build.py --check  # fail if the committed output is stale
"""
import base64
import html
import json
import pathlib
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
I18N = json.loads((ROOT / "content" / "i18n.json").read_text(encoding="utf-8"))
RSVP = json.loads((ROOT / "content" / "rsvp.json").read_text(encoding="utf-8"))
_reg = ROOT / "content" / "register.json"
REGISTER = json.loads(_reg.read_text(encoding="utf-8")) if _reg.exists() else {}
LOCALES = ["en", "ru", "cnr"]
ORIGIN = "https://sobor.io"


def crc16(data):
    """CRC-16/XMODEM — Stellar appends it to a strkey payload, little-endian."""
    crc = 0
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def is_account_id(s):
    """A real strkey check, so a typo in content/rsvp.json cannot reach the site."""
    if not isinstance(s, str) or len(s) != 56 or not s.startswith("G"):
        return False
    try:
        raw = base64.b32decode(s)
    except Exception:
        return False
    if len(raw) != 35 or raw[0] != 6 << 3:
        return False
    return crc16(raw[:33]) == raw[33] | (raw[34] << 8)


ACCOUNT = RSVP.get("account", "").strip()
if ACCOUNT and not is_account_id(ACCOUNT):
    sys.exit("content/rsvp.json: %r is not a valid Stellar account id" % ACCOUNT)

# Which chip each seat carries, and which external link (if any) its paragraph ends on.
CHIPS = ["impl", "review_unwired", "review_noimpl", "impl", "draft", "draft", "draft",
         "draft", "draft", "draft", "draft", "operator", "operator", "operator",
         "live_both", "live_ios"]
TONE = {"impl": "green", "operator": "green", "live_both": "green", "live_ios": "green",
        "review_unwired": "amber", "review_noimpl": "amber", "draft": "blue"}
LINKS = {
    0:  ("link_impl",      "https://github.com/onymchat/onym-discovery"),
    3:  ("link_impl",      "https://github.com/onymchat/onym-backup"),
    13: ("link_contracts", "https://github.com/onymchat/onym-contracts"),
    15: ("link_rust",      "https://github.com/onymchat/onym-moderation"),
}

MARK = """<svg width="28" height="28" viewBox="0 0 28 28" aria-hidden="true">
        <rect x=".5" y=".5" width="27" height="27" rx="6.2" fill="none" stroke="var(--on-hairline-strong)"></rect>
        <g transform="rotate(45 14 14)" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round">
          <path d="M14 5.2A8.8 8.8 0 0 1 22.8 14"></path>
          <path d="M14 22.8A8.8 8.8 0 0 1 5.2 14"></path>
        </g>
        <g fill="currentColor" opacity=".85">
          <circle cx="18.6" cy="14" r="1.15"></circle><circle cx="17.25" cy="17.25" r="1.15"></circle>
          <circle cx="14" cy="18.6" r="1.15"></circle><circle cx="10.75" cy="17.25" r="1.15"></circle>
          <circle cx="9.4" cy="14" r="1.15"></circle><circle cx="10.75" cy="10.75" r="1.15"></circle>
          <circle cx="14" cy="9.4" r="1.15"></circle><circle cx="17.25" cy="10.75" r="1.15"></circle>
        </g>
      </svg>"""


def e(s):
    return html.escape(str(s), quote=True)


def line(block, key):
    """A headline line, wrapped in <span lang> when the locale marks it as borrowed.

    The Russian page says "Homestead it." in English on purpose; tagging it keeps a
    screen reader from reading English letters with Russian phonetics.
    """
    text = e(block[key])
    tag = block.get(key + "_lang")
    return '<span lang="%s">%s</span>' % (e(tag), text) if tag else text


def render(code):
    t = I18N[code]
    base = t["dir"]

    alts = "\n".join(
        '<link rel="alternate" hreflang="%s" href="%s%s"/>' % (I18N[l]["lang"], ORIGIN, I18N[l]["dir"])
        for l in LOCALES
    ) + '\n<link rel="alternate" hreflang="x-default" href="%s/"/>' % ORIGIN

    # language switcher — real links, so it works with JS off and search engines follow it
    lang_btns = "\n        ".join(
        '<a class="pick%s" href="%s" lang="%s" hreflang="%s" data-lang="%s" title="%s"%s>%s</a>'
        % (" is-on" if l == code else "", I18N[l]["dir"], I18N[l]["lang"], I18N[l]["lang"],
           I18N[l]["lang"], e(I18N[l]["title_label"]), ' aria-current="true"' if l == code else "",
           I18N[l]["label"])
        for l in LOCALES
    )

    cards = "\n".join(
        """        <div class="card">
          <div class="kicker">%02d · %s</div>
          <h3>%s</h3>
          <p>%s</p>
          <p class="aph">%s</p>
        </div>""" % (i + 1, e(c["k"]), e(c["h"]), e(c["p"]), e(c["a"]))
        for i, c in enumerate(t["contest"]["cards"])
    )

    seats = []
    for i, s in enumerate(t["seats"]["items"]):
        chip = t["seats"]["chips"][CHIPS[i]]
        body = e(s["p"])
        if i in LINKS:
            key, url = LINKS[i]
            body += ' <a href="%s">%s</a>' % (url, e(t["seats"][key]))
        seats.append(
            """        <div class="card seat">
          <h3>%s</h3>
          <p>%s</p>
          <span class="chip %s">%s</span>
        </div>""" % (e(s["h"]), body, TONE[CHIPS[i]], e(chip))
        )
    seats = "\n".join(seats)

    picks = "\n            ".join(
        '<button class="pick" type="button" aria-pressed="false" data-bit="%d">%s</button>'
        % (i, e(s["h"]))
        for i, s in enumerate(t["seats"]["items"])
    )
    rsvp_body = rsvp_block(t, picks)

    hero_h1 = line(t["hero"], "h1a") + "<br>" + line(t["hero"], "h1b")
    closing_h2 = line(t["closing"], "h2a") + "<br>" + line(t["closing"], "h2b")
    if t["closing"].get("h2c"):
        closing_h2 += "<br>" + line(t["closing"], "h2c")

    return """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{title}</title>
<meta name="description" content="{description}"/>
<meta name="theme-color" content="#0e0e10" media="(prefers-color-scheme: dark)"/>
<meta name="theme-color" content="#f5f5f7" media="(prefers-color-scheme: light)"/>
<link rel="canonical" href="{origin}{base}"/>
{alts}
<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large"/>
<meta property="og:type" content="website"/>
<meta property="og:url" content="{origin}{base}"/>
<meta property="og:site_name" content="sobor"/>
<meta property="og:locale" content="{lang}"/>
<meta property="og:title" content="{title}"/>
<meta property="og:description" content="{og_description}"/>
<meta name="twitter:card" content="summary_large_image"/>
<link rel="icon" href="/favicon.ico" sizes="48x48"/>
<link rel="icon" href="/favicon.svg" type="image/svg+xml"/>
<link rel="apple-touch-icon" href="/apple-touch-icon.png"/>
<link rel="manifest" href="/site.webmanifest"/>
<script src="/assets/theme.js"></script>
<script src="/assets/lang.js"></script>
<link rel="stylesheet" href="/assets/sobor.css"/>
</head>
<body>

<header class="nav">
  <div class="wrap">
    <a class="brand" href="{base}" aria-label="{nav_home}">
      {mark}
      <span>sobor</span>
    </a>
    <nav class="nav-links">
      <a href="#contest">{nav_contest}</a>
      <a href="#seats">{nav_seats}</a>
      <a href="#rules">{nav_rules}</a>
      <a href="#status">{nav_status}</a>
    </nav>
    <div class="nav-cta"><a class="btn-pill" href="#rsvp">{nav_rsvp}</a></div>
  </div>
</header>

<main id="main">

  <div class="hero">
    <div class="hero-eyebrow">{hero_eyebrow}</div>
    <h1>{hero_h1}</h1>
    <div class="hero-copy">
      <p>{hero_lede}</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="#rsvp">{hero_cta}</a>
        <a href="#rules">{hero_rules}</a>
      </div>
    </div>
  </div>

  <!-- The three open questions. When one settles, swap .tag.open for .tag.settled in
       content/i18n.json's label and rewrite the paragraph. Do not soften these. -->
  <section class="status" id="status">
    <div class="wrap">
      <div class="status-stamp">{st_stamp}</div>
      <div class="status-grid">
        <div>
          <span class="tag open">{st_venue_tag}</span>
          <p>{st_venue_p}</p>
        </div>
        <div>
          <span class="tag open">{st_arbiter_tag}</span>
          <p>{st_arbiter_p}</p>
        </div>
        <div>
          <span class="tag open">{st_fund_tag}</span>
          <p>{st_fund_p}</p>
        </div>
      </div>
    </div>
  </section>

  <section class="band" id="contest">
    <div class="wrap">
      <div class="eyebrow"><span>01</span><b>· {c_eyebrow}</b></div>
      <h2>{c_h2a}<br>{c_h2b}</h2>
      <p class="section-lede">{c_lede}</p>
      <div class="grid-4">
{cards}
      </div>
      <p class="after-grid" id="rules"><a href="#rules">{c_more}</a></p>
    </div>
  </section>

  <section class="band" id="seats">
    <div class="wrap">
      <div class="eyebrow"><span>02</span><b>· {s_eyebrow}</b></div>
      <h2>{s_h2a}<br>{s_h2b}</h2>
      <p class="section-lede">{s_lede}</p>
      <div class="grid-4 seats-grid">
{seats}
      </div>
      <p class="after-grid"><a href="https://onym.foundation/seats.html">{s_more}</a></p>
      <p class="after-grid">{s_note}</p>
    </div>
  </section>

  <section class="band who">
    <div class="wrap">
      <div class="eyebrow"><span>03</span><b>· {w_eyebrow}</b></div>
      <h2>{w_h2a}<br>{w_h2b}</h2>
      <div class="grid-2">
        <div class="card">
          <h3>{w_pre_h}</h3>
          <p>{w_pre_p1}<a href="https://bsn.expert">bsn.expert</a>{w_pre_p2}</p>
          <div class="meta">{w_pre_meta}</div>
          <p class="aph">{w_pre_a}</p>
        </div>
        <div class="card">
          <h3>{w_else_h}</h3>
          <p>{w_else_p}</p>
          <div class="meta">{w_else_meta}</div>
          <p class="aph">{w_else_a}</p>
        </div>
      </div>

{rsvp_body}
    </div>
  </section>

  <section class="band">
    <div class="wrap">
      <div class="eyebrow"><span>04</span><b>· {f_eyebrow}</b></div>
      <div class="fund">
        <div class="fund-label">{f_label}</div>
        <!-- When money clears: replace the amount, change the caption, and set --so-meter. -->
        <div class="fund-figure">
          <b>{f_amount}</b>
          <span>{f_caption}</span>
        </div>
        <div class="meter" role="img" aria-label="{f_meter_aria}"><i></i></div>
        <div class="fund-cols">
          <p>{f_p1}</p>
          <p>{f_p2}</p>
        </div>
        <p class="aph">{f_a}</p>
      </div>
    </div>
  </section>

  <section class="closing">
    <div>
      <h2>{closing_h2}</h2>
      <div class="closing-actions">
        <a class="btn btn-primary" href="#rsvp">{hero_cta}</a>
        <a href="#rules">{hero_rules}</a>
      </div>
      <p class="when">{cl_when}</p>
    </div>
  </section>

</main>

<footer>
  <div class="wrap">
    <div class="foot-l">
      <div class="foot-copy">{ft_copy}</div>
      <div class="foot-sign">{ft_sign}</div>
    </div>
    <div class="foot-r">
      <div class="foot-links">
        <a href="https://onym.app">onym.app</a>
        <a href="https://onym.foundation">onym.foundation</a>
        <a href="https://bsn.expert">bsn.expert</a>
      </div>
      <nav class="lang" aria-label="{ft_lang_aria}">
        {lang_btns}
      </nav>
      <!-- Lives in the footer so that on a narrow screen it can simply sit there
           instead of floating over the text. Above 850px it is fixed again. -->
      <div class="theme" role="group" aria-label="{th_aria}">
        <button type="button" data-theme-set="auto" aria-pressed="true">{th_auto}</button>
        <button type="button" data-theme-set="light" aria-pressed="false">{th_light}</button>
        <button type="button" data-theme-set="dark" aria-pressed="false">{th_dark}</button>
      </div>
    </div>
  </div>
</footer>

<script src="/assets/sobor.js" defer></script>
</body>
</html>
""".format(
        lang=t["lang"], origin=ORIGIN, base=base, alts=alts, mark=MARK,
        title=e(t["title"]), description=e(t["description"]), og_description=e(t["og_description"]),
        nav_home=e(t["nav"]["home"]), nav_contest=e(t["nav"]["contest"]), nav_seats=e(t["nav"]["seats"]),
        nav_rules=e(t["nav"]["rules"]), nav_status=e(t["nav"]["status"]), nav_rsvp=e(t["nav"]["rsvp"]),
        hero_eyebrow=e(t["hero"]["eyebrow"]), hero_h1=hero_h1, closing_h2=closing_h2,
        hero_lede=e(t["hero"]["lede"]), hero_cta=e(t["hero"]["cta"]), hero_rules=e(t["hero"]["rules"]),
        st_stamp=e(t["status"]["stamp"]), st_venue_tag=e(t["status"]["venue_tag"]), st_venue_p=e(t["status"]["venue_p"]),
        st_arbiter_tag=e(t["status"]["arbiter_tag"]), st_arbiter_p=e(t["status"]["arbiter_p"]),
        st_fund_tag=e(t["status"]["fund_tag"]), st_fund_p=e(t["status"]["fund_p"]),
        c_eyebrow=e(t["contest"]["eyebrow"]), c_h2a=e(t["contest"]["h2a"]), c_h2b=e(t["contest"]["h2b"]),
        c_lede=e(t["contest"]["lede"]), c_more=e(t["contest"]["more"]), cards=cards,
        s_eyebrow=e(t["seats"]["eyebrow"]), s_h2a=e(t["seats"]["h2a"]), s_h2b=e(t["seats"]["h2b"]),
        s_lede=e(t["seats"]["lede"]), s_more=e(t["seats"]["more"]), s_note=e(t["seats"]["note"]), seats=seats,
        w_eyebrow=e(t["who"]["eyebrow"]), w_h2a=e(t["who"]["h2a"]), w_h2b=e(t["who"]["h2b"]),
        w_pre_h=e(t["who"]["pre_h"]), w_pre_p1=e(t["who"]["pre_p1"]), w_pre_p2=e(t["who"]["pre_p2"]),
        w_pre_meta=e(t["who"]["pre_meta"]), w_pre_a=e(t["who"]["pre_a"]),
        w_else_h=e(t["who"]["else_h"]), w_else_p=e(t["who"]["else_p"]),
        w_else_meta=e(t["who"]["else_meta"]), w_else_a=e(t["who"]["else_a"]),
        f_eyebrow=e(t["fund"]["eyebrow"]), f_label=e(t["fund"]["label"]), f_amount=e(t["fund"]["amount"]),
        f_caption=e(t["fund"]["caption"]), f_meter_aria=e(t["fund"]["meter_aria"]),
        f_p1=e(t["fund"]["p1"]), f_p2=e(t["fund"]["p2"]), f_a=e(t["fund"]["a"]),
        rsvp_body=rsvp_body,
        cl_when=e(t["closing"]["when"]),
        ft_copy=e(t["footer"]["copy"]), ft_sign=e(t["footer"]["sign"]), ft_lang_aria=e(t["footer"]["lang_aria"]),
        lang_btns=lang_btns,
        th_aria=e(t["theme"]["aria"]), th_auto=e(t["theme"]["auto"]),
        th_light=e(t["theme"]["light"]), th_dark=e(t["theme"]["dark"]),
    )



def sep7_uri(memo, msg):
    """A SEP-0007 `pay` URI.

    asset_code=XLM is sent even though SEP-7 says an absent asset means XLM: some
    wallets open the request with no asset selected unless it is named. asset_issuer
    stays absent, which is what makes it the native asset rather than someone's token
    called XLM. network_passphrase is omitted, which SEP-7 reads as the public network.

    origin_domain is left off deliberately: without a matching `signature` from a key
    published in stellar.toml, wallets flag it, so an unsigned claim of origin is worse
    than none. Signing it is the next step, and needs a key sobor does not have yet."""
    q = [("destination", ACCOUNT), ("amount", RSVP["amount"]), ("asset_code", "XLM"),
         ("memo", memo), ("memo_type", "MEMO_TEXT"), ("msg", msg)]
    return "web+stellar:pay?" + urllib.parse.urlencode(q, quote_via=urllib.parse.quote)


def rsvp_block(t, picks):
    r = t["rsvp"]
    ev = RSVP["event"]

    # The register line. The "as of" stamp shows in both states on purpose: a count
    # baked at build time that does not say when it was taken reads as live, and this
    # page does not get to imply things it has not checked.
    n = REGISTER.get("count") or 0
    stamp = REGISTER.get("synced", "")
    stamp = stamp.replace("T", " ").replace("Z", " UTC")[:-7] + " UTC" if stamp else "—"
    head = ("<b>%d</b> %s · <b>%d</b> %s" % (n, e(r["register"]), REGISTER.get("pre_approved", 0),
                                             e(r["pre_approved"]))) if n else e(r["empty_register"])
    # The newline before the stamp is load-bearing: .rsvp-synced is display:block, but
    # if the stylesheet is stale or missing this still reads as "… pre-approved last
    # read from the ledger …" rather than running the two together.
    reg = '<span class="rsvp-reg">%s\n<span class="rsvp-synced">%s %s</span></span>' % (
        head, e(r["synced"]), e(stamp))

    if not ACCOUNT:
        return """      <div class="card rsvp" id="rsvp">
        <div class="kicker">%s</div>
        <span class="tag open">%s</span>
        <p class="rsvp-note">%s</p>
        <p class="rsvp-note">%s</p>
      </div>""" % (e(r["kicker"]), e(r["unset_tag"]), e(r["unset_p"]), e(r["ledger_note"]))

    bits = "\n            ".join(
        '<li><code>%d</code> %s</li>' % (i, e(s["h"])) for i, s in enumerate(t["seats"]["items"]))

    return """      <div class="card rsvp" id="rsvp"
           data-account="{acct}" data-amount="{amount}" data-event="{ev}"
           data-msg="{msg}" data-copy="{copy}" data-copied="{copied}">
        <div class="kicker">{kicker}</div>
        {reg}

        <div class="kicker kicker-seats">{mode_kicker}</div>
        <div class="rsvp-mode" role="radiogroup" aria-label="{mode_kicker}">
          <button class="pick" type="button" role="radio" aria-checked="true" data-mode="p">{mode_person}</button>
          <button class="pick" type="button" role="radio" aria-checked="false" data-mode="r">{mode_remote}</button>
        </div>

        <div class="kicker kicker-seats">{seats_kicker}</div>
        <div class="rsvp-seats" role="group" aria-label="{seats_aria}">
            {picks}
        </div>

        <div class="kicker kicker-seats">{memo_kicker}</div>
        <div class="rsvp-row">
          <output class="rsvp-memo" id="rsvp-memo" for="rsvp">{memo0}</output>
          <a class="btn btn-primary" id="rsvp-go" href="{uri0}">{open_wallet}</a>
        </div>
        <p class="rsvp-note">{wallet_note}</p>

        <details class="drop">
          <summary>{manual}</summary>
          <dl class="kv">
            <dt>{f_to}</dt><dd><code>{acct}</code><button class="copy" type="button" data-copy="{acct}">{copy}</button></dd>
            <dt>{f_amount}</dt><dd><code>{amount} XLM</code><button class="copy" type="button" data-copy="{amount}">{copy}</button></dd>
            <dt>{f_memo}</dt><dd><code id="rsvp-memo2">{memo0}</code><button class="copy" type="button" data-copy-memo>{copy}</button></dd>
          </dl>
        </details>

        <details class="drop">
          <summary>{decode}</summary>
          <p>{decode_p}</p>
          <ol class="bits" start="0">
            {bits}
          </ol>
        </details>

        <div class="rsvp-foot">
          <p class="rsvp-note">{ledger_note}</p>
          <p class="rsvp-out"><a id="rsvp-out" href="{uri_out}">{withdraw}</a></p>
        </div>
      </div>""".format(
        acct=e(ACCOUNT), amount=e(RSVP["amount"]), ev=e(ev), msg=e(r["msg"]),
        copy=e(r["copy"]), copied=e(r["copied"]), reg=reg,
        kicker=e(r["kicker"]), mode_kicker=e(r["mode_kicker"]),
        mode_person=e(r["mode_person"]), mode_remote=e(r["mode_remote"]),
        seats_kicker=e(r["seats_kicker"]), seats_aria=e(r["seats_aria"]), picks=picks,
        memo_kicker=e(r["memo_kicker"]), memo0=e("%s p 0000" % ev),
        uri0=e(sep7_uri("%s p 0000" % ev, r["msg"])),
        uri_out=e(sep7_uri("%s out" % ev, r["msg"])),
        open_wallet=e(r["open_wallet"]), wallet_note=e(r["wallet_note"]),
        manual=e(r["manual"]), f_to=e(r["f_to"]), f_amount=e(r["f_amount"]), f_memo=e(r["f_memo"]),
        decode=e(r["decode"]), decode_p=e(r["decode_p"]), bits=bits,
        ledger_note=e(r["ledger_note"]), withdraw=e(r["withdraw"]))


def target(code):
    return ROOT / "public" / (I18N[code]["dir"].strip("/") or ".") / "index.html"


def main():
    check = "--check" in sys.argv
    stale = []
    for code in LOCALES:
        out, path = render(code), target(code)
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != out:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(out, encoding="utf-8")
            print("  wrote %s  (%d bytes)" % (path.relative_to(ROOT), len(out.encode())))

    # sitemap
    urls = "".join(
        "\n  <url><loc>%s%s</loc>%s</url>" % (
            ORIGIN, I18N[c]["dir"],
            "".join('<xhtml:link rel="alternate" hreflang="%s" href="%s%s"/>'
                    % (I18N[l]["lang"], ORIGIN, I18N[l]["dir"]) for l in LOCALES))
        for c in LOCALES
    )
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
               'xmlns:xhtml="http://www.w3.org/1999/xhtml">%s\n</urlset>\n' % urls)
    robots = "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % ORIGIN
    for name, body in (("sitemap.xml", sitemap), ("robots.txt", robots)):
        p = ROOT / "public" / name
        if check:
            if not p.exists() or p.read_text(encoding="utf-8") != body:
                stale.append("public/" + name)
        else:
            p.write_text(body, encoding="utf-8")
            print("  wrote public/%s" % name)

    if check:
        if stale:
            print("STALE (run tools/build.py):")
            [print("  " + s) for s in stale]
            return 1
        print("  output is up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
