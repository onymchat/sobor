#!/usr/bin/env python3
"""Render public/{,ru/,cnr/}index.html from content/i18n.json.

One template, three locales. Output is committed — Vercel serves it as-is, there is
no build step at deploy time. Run this after editing content/i18n.json, and commit
the regenerated pages together with the string change.

    python3 tools/build.py          # write
    python3 tools/build.py --check  # fail if the committed output is stale
"""
import html
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
I18N = json.loads((ROOT / "content" / "i18n.json").read_text(encoding="utf-8"))
LOCALES = ["en", "ru", "cnr"]
ORIGIN = "https://sobor.io"

# The Cal.com event the booking section embeds. Namespace is arbitrary but has to
# match the one assets/cal.js initialises, or the embed renders into nothing.
CAL_LINK = "enikeev/sobor"
CAL_NS = "sobor"

# The venue, the organizer's contact, and how much of the fund has cleared.
# These are facts, not copy, so they live here rather than three times over in i18n.json.
VENUE_URL = ("https://www.google.com/maps/place/Montelibero-City/"
             "@42.0326317,19.1635781,17z/data=!3m1!4b1!4m6!3m5!"
             "1s0x134e7345408cff31:0x4c5d231719f81f5e!8m2!3d42.0326317!4d19.166153")
TG_URL = "https://t.me/programyzer"
TG_HANDLE = "@programyzer"
# The open group, as opposed to TG_URL above, which is the organizer himself.
TG_GROUP_URL = "https://t.me/onymsobor"

# Each status item is open until the thing it names is settled. Green tag, not red.
STATUS_STATE = {"venue": "settled", "arbiter": "settled", "fund": "settled"}

# The meter shows the share of the target that has cleared. There is no published
# target yet, so there is no share to draw and the meter is left out entirely —
# a bar at 0% under a non-zero figure would just read as a bug. Set this to the
# target in euros to bring it back.
FUND_TARGET = None

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


def meter(t):
    """The fund meter, or nothing at all while no target is published.

    The fill itself is --so-meter in assets/sobor.css, set by hand when the target
    is decided — the page carries no inline style attribute, and this is not the
    place to start.
    """
    if FUND_TARGET is None:
        return ""
    return ('        <div class="meter" role="img" aria-label="%s"><i></i></div>\n'
            % e(t["fund"]["meter_aria"]))


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
<meta property="og:image" content="{origin}/{og_image}"/>
<meta property="og:image:type" content="image/png"/>
<meta property="og:image:width" content="1200"/>
<meta property="og:image:height" content="630"/>
<meta property="og:image:alt" content="{og_alt}"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:image" content="{origin}/{og_image}"/>
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
    <div class="nav-cta"><a class="btn-pill" href="#book">{nav_book}</a></div>
  </div>
</header>

<main id="main">

  <div class="hero">
    <div class="hero-eyebrow">{hero_eyebrow}</div>
    <h1>{hero_h1}</h1>
    <div class="hero-copy">
      <p>{hero_lede}</p>
      <div class="hero-actions">
        <div class="hero-buttons">
          <a class="btn btn-primary" href="#book">{hero_cta}</a>
          <a class="btn btn-secondary" href="{tg_group_url}">{hero_tg}</a>
        </div>
        <a href="#rules">{hero_rules}</a>
      </div>
    </div>
  </div>

  <section class="band" id="book">
    <div class="wrap">
      <div class="eyebrow"><span>01</span><b>· {b_eyebrow}</b></div>
      <h2>{b_h2a}<br>{b_h2b}</h2>
      <p class="section-lede">{b_lede}</p>
      <!-- assets/cal.js mounts the Cal.com inline embed here and reads the event off
           these data attributes, so content/build.py stays the only place the link is
           written. The link underneath is not a fallback that JS removes: it stays, so
           the booking page is reachable with the embed blocked or failing to load. -->
      <div class="cal-mount" id="cal-mount"
           data-cal-link="{cal_link}" data-cal-namespace="{cal_ns}"></div>
      <p class="after-grid">{b_phone}</p>
      <p class="after-grid"><a href="https://cal.com/{cal_link}">{b_fallback}</a></p>
      <p class="after-grid">{b_note}</p>
      <p class="aph book-aph">{b_aph}</p>
    </div>
  </section>

  <section class="band" id="people">
    <div class="wrap">
      <div class="eyebrow"><span>02</span><b>· {p_eyebrow}</b></div>
      <h2>{p_h2a}<br>{p_h2b}</h2>
      <p class="section-lede">{p_lede}</p>
      <div class="people-grid">
        <div class="person">
          <img class="portrait" src="/assets/rinat.jpg" width="480" height="480"
               alt="{p_org_alt}" loading="lazy" decoding="async">
          <div>
            <div class="person-role">{p_org_role}</div>
            <h3>{p_org_name}</h3>
            <p>{p_org_p}</p>
            <p class="person-contact"><a href="{tg_url}" rel="me">{tg_handle}</a></p>
          </div>
        </div>
        <div class="person">
          <img class="portrait" src="/assets/andy.jpg" width="423" height="423"
               alt="{p_arb_alt}" loading="lazy" decoding="async">
          <div>
            <div class="person-role">{p_arb_role}</div>
            <h3>{p_arb_name}</h3>
            <p>{p_arb_p}</p>
          </div>
        </div>
      </div>
      <p class="aph">{p_aph}</p>
    </div>
  </section>

  <!-- The three questions that were open. A state flips in STATUS_STATE above and the
       paragraph gets rewritten in content/i18n.json. Do not soften these. -->
  <section class="status" id="status">
    <div class="wrap">
      <div class="status-stamp">{st_stamp}</div>
      <div class="status-grid">
        <div class="fact">
          <div class="fact-value">{st_venue_value}</div>
          <div class="fact-label"><i class="dot {st_venue_state}"></i>{st_venue_label}</div>
          <p>{st_venue_p}</p>
          <p class="fact-link"><a href="{venue_url}">{st_venue_link}</a></p>
        </div>
        <div class="fact">
          <div class="fact-value">{st_arbiter_value}</div>
          <div class="fact-label"><i class="dot {st_arbiter_state}"></i>{st_arbiter_label}</div>
          <p>{st_arbiter_p}</p>
        </div>
        <div class="fact fact-warm">
          <div class="fact-value">{st_fund_value}</div>
          <div class="fact-label"><i class="dot {st_fund_state}"></i>{st_fund_label}</div>
          <p>{st_fund_p}</p>
        </div>
      </div>
    </div>
  </section>

  <section class="band" id="contest">
    <div class="wrap">
      <div class="eyebrow"><span>03</span><b>· {c_eyebrow}</b></div>
      <h2>{c_h2a}<br>{c_h2b}</h2>
      <p class="section-lede">{c_lede}</p>
      <p class="after-grid" id="rules"><a href="#rules">{c_more}</a></p>
    </div>
  </section>

  <section class="band" id="seats">
    <div class="wrap">
      <div class="eyebrow"><span>04</span><b>· {s_eyebrow}</b></div>
      <h2>{s_h2a}<br>{s_h2b}</h2>
      <p class="section-lede">{s_lede}</p>
      <div class="grid-4 seats-grid">
{seats}
      </div>
      <p class="after-grid"><a href="https://onym.foundation/seats.html">{s_more}</a></p>
      <p class="after-grid">{s_note}</p>
    </div>
  </section>


  <section class="band">
    <div class="wrap">
      <div class="eyebrow"><span>05</span><b>· {f_eyebrow}</b></div>
      <div class="fund">
        <div class="fund-label">{f_label}</div>
        <!-- The figure is content/i18n.json fund.amount. The meter beneath it only
             appears once FUND_TARGET is set; see meter() above. -->
        <div class="fund-figure">
          <b>{f_amount}</b>
          <span>{f_caption}</span>
        </div>
{f_meter}        <div class="fund-cols">
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
        <a class="btn btn-primary" href="#book">{hero_cta}</a>
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
        <a href="{tg_url}" rel="me">{tg_handle}</a>
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
<script src="/assets/cal.js" defer></script>
</body>
</html>
""".format(
        lang=t["lang"], origin=ORIGIN, base=base, alts=alts, mark=MARK,
        title=e(t["title"]), description=e(t["description"]), og_description=e(t["og_description"]),
        og_image=("og.png" if code == "en" else "og-%s.png" % code),
        og_alt=e("%s %s — %s" % (t["hero"]["h1a"], t["hero"]["h1b"], t["hero"]["eyebrow"])),
        nav_home=e(t["nav"]["home"]), nav_contest=e(t["nav"]["contest"]), nav_seats=e(t["nav"]["seats"]),
        nav_rules=e(t["nav"]["rules"]), nav_status=e(t["nav"]["status"]), nav_book=e(t["nav"]["book"]),
        hero_eyebrow=e(t["hero"]["eyebrow"]), hero_h1=hero_h1, closing_h2=closing_h2,
        hero_lede=e(t["hero"]["lede"]), hero_cta=e(t["hero"]["cta"]), hero_rules=e(t["hero"]["rules"]),
        st_stamp=e(t["status"]["stamp"]), st_venue_p=e(t["status"]["venue_p"]),
        st_venue_value=e(t["status"]["venue_value"]), st_venue_label=e(t["status"]["venue_label"]),
        st_arbiter_value=e(t["status"]["arbiter_value"]), st_arbiter_label=e(t["status"]["arbiter_label"]),
        st_fund_value=e(t["status"]["fund_value"]), st_fund_label=e(t["status"]["fund_label"]),
        st_venue_link=e(t["status"]["venue_link"]), venue_url=e(VENUE_URL),
        st_venue_state=STATUS_STATE["venue"], st_arbiter_state=STATUS_STATE["arbiter"],
        st_fund_state=STATUS_STATE["fund"], tg_url=e(TG_URL), tg_handle=e(TG_HANDLE), tg_group_url=e(TG_GROUP_URL),
        hero_tg=e(t["hero"]["tg"]),
        st_arbiter_p=e(t["status"]["arbiter_p"]), st_fund_p=e(t["status"]["fund_p"]),
        c_eyebrow=e(t["contest"]["eyebrow"]), c_h2a=e(t["contest"]["h2a"]), c_h2b=e(t["contest"]["h2b"]),
        c_lede=e(t["contest"]["lede"]), c_more=e(t["contest"]["more"]),
        s_eyebrow=e(t["seats"]["eyebrow"]), s_h2a=e(t["seats"]["h2a"]), s_h2b=e(t["seats"]["h2b"]),
        s_lede=e(t["seats"]["lede"]), s_more=e(t["seats"]["more"]), s_note=e(t["seats"]["note"]), seats=seats,
        b_eyebrow=e(t["book"]["eyebrow"]), b_h2a=e(t["book"]["h2a"]), b_h2b=e(t["book"]["h2b"]),
        b_lede=e(t["book"]["lede"]), b_fallback=e(t["book"]["fallback"]),
        b_phone=e(t["book"]["phone"]), b_note=e(t["book"]["note"]), b_aph=e(t["book"]["aph"]),
        cal_link=e(CAL_LINK), cal_ns=e(CAL_NS),
        f_eyebrow=e(t["fund"]["eyebrow"]), f_label=e(t["fund"]["label"]), f_amount=e(t["fund"]["amount"]),
        f_caption=e(t["fund"]["caption"]), f_meter=meter(t),
        p_eyebrow=e(t["people"]["eyebrow"]), p_h2a=e(t["people"]["h2a"]), p_h2b=e(t["people"]["h2b"]),
        p_lede=e(t["people"]["lede"]), p_aph=e(t["people"]["aph"]),
        p_org_role=e(t["people"]["org_role"]), p_org_name=e(t["people"]["org_name"]),
        p_org_p=e(t["people"]["org_p"]), p_org_alt=e(t["people"]["org_alt"]),
        p_arb_role=e(t["people"]["arb_role"]), p_arb_name=e(t["people"]["arb_name"]),
        p_arb_p=e(t["people"]["arb_p"]), p_arb_alt=e(t["people"]["arb_alt"]),
        f_p1=e(t["fund"]["p1"]), f_p2=e(t["fund"]["p2"]), f_a=e(t["fund"]["a"]),
        cl_when=e(t["closing"]["when"]),
        ft_copy=e(t["footer"]["copy"]), ft_sign=e(t["footer"]["sign"]), ft_lang_aria=e(t["footer"]["lang_aria"]),
        lang_btns=lang_btns,
        th_aria=e(t["theme"]["aria"]), th_auto=e(t["theme"]["auto"]),
        th_light=e(t["theme"]["light"]), th_dark=e(t["theme"]["dark"]),
    )


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
