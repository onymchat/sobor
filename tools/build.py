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

<a class="brand" href="{base}" aria-label="{nav_home}">
  {mark}
  <span>sobor</span>
</a>

<main id="main">
  <h1>{h1a}<br>{h1b}<br><span class="ahead">{h1c}</span></h1>
</main>

<footer>
  <div class="foot-copy">{ft_copy}</div>
  <nav class="lang" aria-label="{ft_lang_aria}">
        {lang_btns}
  </nav>
  <div class="theme" role="group" aria-label="{th_aria}">
    <button type="button" data-theme-set="auto" aria-pressed="true">{th_auto}</button>
    <button type="button" data-theme-set="light" aria-pressed="false">{th_light}</button>
    <button type="button" data-theme-set="dark" aria-pressed="false">{th_dark}</button>
  </div>
</footer>

<script src="/assets/sobor.js" defer></script>
</body>
</html>
""".format(
        lang=t["lang"], origin=ORIGIN, base=base, alts=alts, mark=MARK,
        title=e(t["title"]), description=e(t["description"]), og_description=e(t["og_description"]),
        og_image=("og.png" if code == "en" else "og-%s.png" % code),
        og_alt=e("%s %s %s" % (t["hero"]["h1a"], t["hero"]["h1b"], t["hero"]["h1c"])),
        nav_home=e(t["nav"]["home"]),
        h1a=e(t["hero"]["h1a"]), h1b=e(t["hero"]["h1b"]), h1c=e(t["hero"]["h1c"]),
        ft_copy=e(t["footer"]["copy"]), ft_lang_aria=e(t["footer"]["lang_aria"]),
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
