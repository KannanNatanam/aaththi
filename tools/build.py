#!/usr/bin/env python3
"""
Builds the AATHTHI website from data/products.json.

Usage (from the site folder):   python3 tools/build.py

You only need to run this when you ADD or EDIT a product. Amazon Attribution
links do not need a rebuild; they live in assets/js/amazon-links.js.

To add a product:
  1. Put its images in assets/products/<slug>/ named 1.webp, 2.webp, ...
     plus thumb.webp (a smaller copy of the main image).
  2. Add an entry to data/products.json (copy an existing one).
  3. Add its ASIN to assets/js/amazon-links.js.
  4. Run this script, then commit everything to GitHub.
"""
import json
import os
import re
import shutil
from datetime import date
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = "https://www.aaththi.com"
STORE_URL = "https://www.amazon.com/stores/AATHTHI/page/D9452E36-205C-4321-8BFA-5A0712A17366"
EMAIL = "info@aaththi.com"
CRAFT_SYMPHONY_URL = "https://www.thecraftsymphony.com/"
OTHER_BRAND_URL = "https://www.amazon.com/author/arcavenuepress"  # Arc & Avenue Press author page (footer only)
TAGLINE = "Connecting You To What You Love"
SOCIAL = [
    ("Instagram", "https://www.instagram.com/aaththienterprises/"),
    ("Facebook", "https://www.facebook.com/aaththi/"),
    ("Pinterest", "https://www.pinterest.com/aaththienterprises"),
    ("YouTube", "https://www.youtube.com/@aaththienterprises"),
    ("X", "https://x.com/aaththi_ent"),
    ("Threads", "https://www.threads.net/@aaththienterprises"),
    ("LinkedIn", "https://www.linkedin.com/company/aaththi/"),
    # Add TikTok here once you have the account URL, e.g. ("TikTok", "https://www.tiktok.com/@yourhandle"),
]
VERSION = date.today().strftime("%Y%m%d")  # cache-busting for CSS/JS

DATA = json.load(open(os.path.join(ROOT, "data", "products.json"), encoding="utf-8"))
CATS = {c["id"]: c for c in DATA["categories"]}
PRODUCTS = [p for p in DATA["products"] if p.get("active", True)]
PRODUCTS.sort(key=lambda p: p.get("order", 99))

ICON_AMAZON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
               'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/>'
               '<path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>')
ICON_SHIELD = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
               'stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/></svg>')
ICONS = {
    "truck": '<path d="M10 17h4V5H2v12h3"/><path d="M14 9h4l4 4v4h-3"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="16.5" cy="17.5" r="2.5"/>',
    "pen": '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
    "gift": '<rect x="3" y="8" width="18" height="4" rx="1"/><path d="M12 8v13"/><path d="M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7"/><path d="M7.5 8a2.5 2.5 0 0 1 0-5C10 3 12 8 12 8s2-5 4.5-5a2.5 2.5 0 0 1 0 5"/>',
    "lock": '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
}


def icon(name):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def e(s):
    return escape(str(s), quote=True)


def plain_dp(asin):
    return f"https://www.amazon.com/dp/{asin}"


def first_sentences(text, n=2, limit=240):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    out = " ".join(parts[:n])
    return out if len(out) <= limit else parts[0]


def paragraphs(text):
    """Split a long Amazon description into short paragraphs of ~3 sentences."""
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    if len(blocks) > 1:
        return blocks
    s = re.split(r"(?<=[.!?])\s+", text.strip())
    return [" ".join(s[i:i + 3]) for i in range(0, len(s), 3)]


# ---------------------------------------------------------------- layout

def page(rel, title, description, body, path, og_image=None, jsonld=None, current=""):
    """rel = relative prefix back to site root ('' or '../' etc.)."""
    canonical = SITE_URL + "/" + path
    og_image = og_image or SITE_URL + "/assets/brand/og-image.jpg"
    nav_items = [("Shop", "shop/", "shop"), ("Party Decor", "shop/#party", "party"),
                 ("Gifts", "shop/#couples", "gifts"), ("About", "about/", "about"), ("Contact", "contact/", "contact")]
    nav = "".join(
        f'<li><a href="{rel}{href}"{" aria-current=\"page\"" if key == current else ""}>{label}</a></li>'
        for label, href, key in nav_items)
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>'
                 for j in (jsonld or []))
    cat_links = "".join(f'<li><a href="{rel}shop/#{c["id"]}">{e(c["name"])}</a></li>' for c in DATA["categories"])
    socials = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{n}</a></li>' for n, u in SOCIAL)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="AATHTHI">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@aaththi_ent">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="{rel}favicon.png" type="image/png">
<link rel="apple-touch-icon" href="{rel}assets/brand/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500;1,600&family=Quicksand:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel}assets/css/style.css?v={VERSION}">
{ld}
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
<header class="site-header">
  <div class="wrap nav">
    <a class="brand" href="{rel or './'}" aria-label="AATHTHI home">
      <img class="mark" src="{rel}assets/brand/mark-gold.png" alt="" width="50" height="36">
      <img class="word" src="{rel}assets/brand/wordmark-black.png" alt="AATHTHI" width="128" height="18">
    </a>
    <button class="menu-toggle" aria-controls="menu" aria-expanded="false" aria-label="Menu">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M3 7h18M3 12h18M3 17h18"/></svg>
    </button>
    <ul class="menu" id="menu">
      {nav}
      <li><a class="btn btn-dark" href="{STORE_URL}" data-asin="STORE" target="_blank" rel="noopener">Amazon Store</a></li>
    </ul>
  </div>
</header>
<main id="content">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot-brand">
        <img class="mark" src="{rel}assets/brand/mark-gold.png" alt="" width="64" height="46">
        <img class="word" src="{rel}assets/brand/wordmark-white.png" alt="AATHTHI" width="150" height="21">
        <p>{TAGLINE}. Thoughtfully designed party decor and gifts, delivered by Amazon.</p>
      </div>
      <div>
        <h2>Shop</h2>
        <ul>{cat_links}<li><a href="{rel}shop/">All products</a></li></ul>
      </div>
      <div>
        <h2>Aaththi</h2>
        <ul>
          <li><a href="{rel}about/">Our story</a></li>
          <li><a href="{rel}contact/">Contact</a></li>
          <li><a href="{STORE_URL}" data-asin="STORE" target="_blank" rel="noopener">Amazon Brand Store</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
        </ul>
        <h2 style="margin-top:28px">Our other brands</h2>
        <ul><li><a href="{OTHER_BRAND_URL}" target="_blank" rel="noopener">Arc &amp; Avenue Press</a> <span style="color:#9b9585;font-size:.85rem">(books)</span></li>
          <li><a href="{CRAFT_SYMPHONY_URL}" target="_blank" rel="noopener">The Craft Symphony</a></li></ul>
      </div>
      <div>
        <h2>Follow us</h2>
        <ul>{socials}</ul>
      </div>
    </div>
    <div class="foot-bottom">
      <span>&copy; <span id="year">{date.today().year}</span> Aaththi Enterprises. All rights reserved.</span>
      <span>Products are sold and shipped through Amazon.com. Amazon and the Amazon logo are trademarks of Amazon.com, Inc. or its affiliates.</span>
    </div>
  </div>
</footer>
<script src="{rel}assets/js/amazon-links.js?v={VERSION}"></script>
<script src="{rel}assets/js/site.js?v={VERSION}"></script>
</body>
</html>
"""


def img(rel, p, n):
    return f'{rel}assets/products/{p["slug"]}/{n}'


def buy_button(p, cls="btn btn-gold", label="Buy on Amazon"):
    return (f'<a class="{cls}" href="{plain_dp(p["asin"])}" data-asin="{p["asin"]}" target="_blank" rel="noopener" '
            f'aria-label="{e(label)}: {e(p["name"])} (opens Amazon in a new tab)">{ICON_AMAZON}{label}</a>')


def card(rel, p, heading="h3"):
    cat = CATS[p["category"]]["name"]
    url = f'{rel}products/{p["slug"]}/'
    return f"""<article class="card" data-cat="{p['category']}">
  <a class="thumb" href="{url}" tabindex="-1" aria-hidden="true"><img src="{img(rel, p, 'thumb.webp')}" alt="" loading="lazy" width="600" height="600"></a>
  <div class="body">
    <span class="cat-label">{e(cat)}</span>
    <{heading}><a href="{url}">{e(p['name'])}</a></{heading}>
    <div class="card-actions">
      <a class="btn btn-line" href="{url}">Details</a>
      {buy_button(p, label="Buy on Amazon")}
    </div>
  </div>
</article>"""


def write(path, html):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html)


def by_slug(slug):
    return next(p for p in PRODUCTS if p["slug"] == slug)


# ---------------------------------------------------------------- pages

def build_home():
    rel = ""
    hero_imgs = [("i-am-one-kitten-banner", "6.webp", "Baby girl at her first birthday party under an I Am One kitten banner"),
                 ("mr-right-apron", "9.webp", "Couple cooking together, him in the Mr. Right apron"),
                 ("hubby-wifey-pillow-covers", "8.webp", "Hubby and Wifey pillow covers on a bed under fairy lights")]
    mosaic = "".join(
        f'<img src="assets/products/{s}/{f}" alt="{e(a)}" width="1200" height="1200"{" fetchpriority=\"high\"" if i == 0 else " loading=\"lazy\""}>'
        for i, (s, f, a) in enumerate(hero_imgs))
    cat_imgs = {"party": ("rustic-burlap-one-banner", "6.webp"),
                "couples": ("his-beauty-her-beast-pillow-covers", "8.webp"),
                "kitchen": ("coffee-teach-repeat-spoon", "8.webp")}
    cats = "".join(f"""<a class="cat" href="shop/#{c['id']}">
  <img src="assets/products/{cat_imgs[c['id']][0]}/{cat_imgs[c['id']][1]}" alt="" loading="lazy" width="1200" height="1200">
  <div class="cat-text"><h3>{e(c['name'])}</h3><p>{e(c['blurb'])}</p></div>
</a>""" for c in DATA["categories"] if any(p["category"] == c["id"] for p in PRODUCTS))
    featured = "".join(card(rel, p) for p in PRODUCTS[:6])
    body = f"""
<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <span class="eyebrow">Designed by Aaththi &middot; Delivered by Amazon</span>
      <h1>Little details for life&rsquo;s <em>big moments</em></h1>
      <p class="lead">Party banners for first birthdays and celebrations, plus playful gifts for couples, dads and coffee lovers. Every piece is designed to make the day feel personal.</p>
      <div class="actions">
        <a class="btn btn-gold btn-lg" href="shop/">Shop the collection</a>
        <a class="btn btn-line btn-lg" href="{STORE_URL}" data-asin="STORE" target="_blank" rel="noopener">Visit our Amazon store</a>
      </div>
    </div>
    <div class="mosaic">{mosaic}</div>
  </div>
</section>
<section class="promise" aria-label="Why shop Aaththi">
  <div class="wrap"><ul>
    <li>{icon('truck')}Fulfilled by Amazon</li>
    <li>{icon('lock')}Secure checkout on Amazon</li>
    <li>{icon('pen')}Designed in-house</li>
    <li>{icon('gift')}Made for gifting</li>
  </ul></div>
</section>
<section class="section">
  <div class="wrap">
    <div class="section-head"><div><span class="eyebrow">Shop by occasion</span><h2>Find the right piece</h2></div></div>
    <div class="cats">{cats}</div>
  </div>
</section>
<section class="section tint">
  <div class="wrap">
    <div class="section-head">
      <div><span class="eyebrow">The collection</span><h2>Featured products</h2></div>
      <a class="link-arrow" href="shop/">View all {len(PRODUCTS)} products &rarr;</a>
    </div>
    <div class="grid">{featured}</div>
  </div>
</section>
<section class="section">
  <div class="wrap story">
    <img src="assets/brand/mark-gold.png" alt="" width="220" height="158" loading="lazy">
    <div>
      <span class="eyebrow">Our name</span>
      <h2>Named after the aaththi flower</h2>
      <p class="lead">Aaththi takes its name from the aaththi flower (<i>Bauhinia racemosa</i>), celebrated in classical Tamil literature and remembered in Avvaiyar&rsquo;s <i>Aathichoodi</i>. Like the flower, our products are meant to bring a little beauty and warmth to everyday moments.</p>
      <a class="link-arrow" href="about/">Read our story &rarr;</a>
    </div>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="wrap">
    <div class="cta-band">
      <div><h2>Shop every Aaththi product on Amazon</h2><p>Fast delivery, easy returns and secure checkout through Amazon.com.</p></div>
      <a class="btn btn-gold btn-lg" href="{STORE_URL}" data-asin="STORE" target="_blank" rel="noopener">Open our Amazon store</a>
    </div>
  </div>
</section>"""
    org = {"@context": "https://schema.org", "@type": "Organization", "name": "Aaththi Enterprises",
           "alternateName": "AATHTHI", "url": SITE_URL + "/", "logo": SITE_URL + "/assets/brand/logo-tagline.png",
           "email": EMAIL, "slogan": TAGLINE, "sameAs": [u for _, u in SOCIAL] + [STORE_URL]}
    write("index.html", page(rel, f"AATHTHI | Party Decorations & Thoughtful Gifts | {TAGLINE}",
                             "Shop AATHTHI first birthday banners, party decorations, couple pillow covers, engraved spoons and gift aprons, available on Amazon.com.",
                             body, "", jsonld=[org]))


def build_shop():
    rel = "../"
    chips = '<button class="chip" data-filter="all" aria-pressed="true">All</button>' + "".join(
        f'<button class="chip" data-filter="{c["id"]}" aria-pressed="false">{e(c["name"])}</button>'
        for c in DATA["categories"] if any(p["category"] == c["id"] for p in PRODUCTS))
    grid = "".join(card(rel, p, "h2") for p in PRODUCTS)
    body = f"""
<section class="page-head">
  <div class="wrap">
    <h1>Shop all products</h1>
    <p class="lead">Every Aaththi product is sold and shipped through Amazon.com. Choose a product to see details, then buy securely on Amazon.</p>
  </div>
</section>
<section class="section" style="padding-top:40px">
  <div class="wrap">
    <div class="chips" role="group" aria-label="Filter by category">{chips}</div>
    <div class="grid">{grid}</div>
  </div>
</section>"""
    items = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "url": f'{SITE_URL}/products/{p["slug"]}/', "name": p["name"]}
        for i, p in enumerate(PRODUCTS)]}
    write("shop/index.html", page(rel, "Shop All Products | AATHTHI",
                                  "Browse AATHTHI party banners, couple pillow covers, engraved spoons and aprons. Buy securely on Amazon.com.",
                                  body, "shop/", jsonld=[items], current="shop"))


def build_product(p):
    rel = "../../"
    cat = CATS[p["category"]]
    imgs = p["images"]
    alt_base = p["name"].replace('"', "")
    thumbs = "".join(
        f'<button type="button" data-full="{img(rel, p, n)}" aria-current="{"true" if i == 0 else "false"}" aria-label="Show image {i + 1}">'
        f'<img src="{img(rel, p, n)}" alt="{e(alt_base)}, image {i + 1}" loading="lazy" width="120" height="120"></button>'
        for i, n in enumerate(imgs))
    video_main = ""
    if p.get("video"):
        # Video goes in second place in the gallery, after the main product photo.
        vthumb = (f'<button type="button" class="vthumb" data-video="{img(rel, p, p["video"])}" aria-current="false" aria-label="Play product video">'
                  f'<img src="{img(rel, p, p["video_poster"])}" alt="" loading="lazy" width="120" height="120">'
                  f'<span class="play" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z" fill="currentColor"/></svg></span></button>')
        first_end = thumbs.index("</button>") + len("</button>")
        thumbs = thumbs[:first_end] + vthumb + thumbs[first_end:]
        video_main = (f'<video id="main-video" controls playsinline preload="none" poster="{img(rel, p, p["video_poster"])}" hidden>'
                      f'<source data-src="{img(rel, p, p["video"])}" type="video/mp4">Your browser does not support video.</video>')
    feats = "".join(
        f'<li>{"<strong>" + e(b["title"]) + "</strong>" if b["title"] else ""}<p>{e(b["text"])}</p></li>'
        for b in p["bullets"])
    desc = "".join(f"<p>{e(x)}</p>" for x in paragraphs(p["description"]))
    related = [x for x in PRODUCTS if x["category"] == p["category"] and x is not p]
    related += [x for x in PRODUCTS if x["category"] != p["category"]]
    related_html = "".join(card(rel, x) for x in related[:3])
    lead = first_sentences(p["description"])
    body = f"""
<div class="wrap">
  <nav class="crumbs" aria-label="Breadcrumb" style="margin-top:24px">
    <a href="{rel}">Home</a><span aria-hidden="true">/</span><a href="{rel}shop/#{cat['id']}">{e(cat['name'])}</a><span aria-hidden="true">/</span><span>{e(p['name'])}</span>
  </nav>
  <div class="pdp">
    <div class="gallery">
      <div class="main"><img id="main-img" src="{img(rel, p, imgs[0])}" alt="{e(alt_base)}" width="1200" height="1200" fetchpriority="high">{video_main}</div>
      {'<p class="video-hint"><button type="button" class="link-arrow" id="watch-video">&#9658; Watch the video</button></p>' if p.get("video") else ""}
      <div class="thumbs">{thumbs}</div>
    </div>
    <div class="buybox">
      <span class="eyebrow">{e(cat['name'])}</span>
      <h1>{e(p['name'])}</h1>
      <p class="lead">{e(lead)}</p>
      {buy_button(p, "btn btn-gold btn-lg")}
      <p class="buy-note">{ICON_SHIELD}<span>You&rsquo;ll complete your purchase securely on Amazon.com, where you can see today&rsquo;s price, delivery date and returns policy.</span></p>
      <ul class="features">{feats}</ul>
    </div>
  </div>
</div>
<section class="section tint">
  <div class="wrap desc">
    <h2>About this product</h2>
    {desc}
    {buy_button(p, "btn btn-dark")}
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="section-head"><div><span class="eyebrow">You may also like</span><h2>More from Aaththi</h2></div>
      <a class="link-arrow" href="{rel}shop/">View all &rarr;</a></div>
    <div class="grid">{related_html}</div>
  </div>
</section>"""
    product_ld = {"@context": "https://schema.org", "@type": "Product", "name": p["name"].replace('"', ""),
                  "description": p["description"], "sku": p["asin"],
                  "image": [f'{SITE_URL}/assets/products/{p["slug"]}/{n}' for n in imgs[:4]],
                  "brand": {"@type": "Brand", "name": "AATHTHI"}, "url": f'{SITE_URL}/products/{p["slug"]}/'}
    crumbs_ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL + "/"},
        {"@type": "ListItem", "position": 2, "name": cat["name"], "item": f"{SITE_URL}/shop/"},
        {"@type": "ListItem", "position": 3, "name": p["name"].replace('"', "")}]}
    title = f'{p["name"].replace(chr(34), "")} | AATHTHI'
    write(f'products/{p["slug"]}/index.html',
          page(rel, title, lead[:160], body, f'products/{p["slug"]}/',
               og_image=f'{SITE_URL}/assets/products/{p["slug"]}/{imgs[0]}', jsonld=[product_ld, crumbs_ld]))


def build_about():
    rel = "../"
    body = f"""
<section class="page-head">
  <div class="wrap"><h1>Our story</h1><p class="lead">{TAGLINE}.</p></div>
</section>
<section class="section">
  <div class="wrap story">
    <img src="{rel}assets/brand/logo-tagline.png" alt="AATHTHI logo: a gold aaththi flower above the AATHTHI wordmark" width="220" height="220">
    <div class="prose">
      <h2 style="margin-top:0">Named after the aaththi flower</h2>
      <p>Aaththi takes its name from the aaththi flower (<i>Bauhinia racemosa</i>), a flower celebrated in classical Tamil literature and remembered in the title of Avvaiyar&rsquo;s <i>Aathichoodi</i>. Our gold flower logo is drawn from it: simple, graceful and full of meaning.</p>
      <h2>What we make</h2>
      <p>We design party decorations and gifts for the moments people remember: a baby&rsquo;s first birthday, a gender reveal, a newlywed home, Father&rsquo;s Day, or a thank-you for a favourite teacher. Each product is designed by our own team, with a focus on clean design, good materials and a touch of humour.</p>
      <h2>Why we sell on Amazon</h2>
      <p>Every Aaththi product is fulfilled by Amazon. That means fast delivery, secure checkout and Amazon&rsquo;s customer service and returns, while we focus on designing products you&rsquo;ll love.</p>
      <p style="margin-top:28px"><a class="btn btn-gold" href="{rel}shop/">Shop the collection</a></p>
    </div>
  </div>
</section>"""
    write("about/index.html", page(rel, "Our Story | AATHTHI",
                                   "AATHTHI is named after the aaththi flower from classical Tamil literature. We design party decorations and thoughtful gifts, fulfilled by Amazon.",
                                   body, "about/", current="about"))


def build_contact():
    rel = "../"
    socials = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{n}</a></li>' for n, u in SOCIAL)
    body = f"""
<section class="page-head">
  <div class="wrap"><h1>Contact us</h1><p class="lead">We&rsquo;d love to hear from you.</p></div>
</section>
<section class="section">
  <div class="wrap contact-grid">
    <div class="contact-card">
      <h2>Questions about an order</h2>
      <p>For delivery, returns or anything about an order you placed, please contact us from <b>Your Orders</b> on Amazon.com and choose <b>Contact seller</b>. That lets us see your order details and help you quickly.</p>
    </div>
    <div class="contact-card">
      <h2>General &amp; business enquiries</h2>
      <p>Product questions, bulk or event orders, and partnerships:</p>
      <p><a class="btn btn-dark" href="mailto:{EMAIL}">{EMAIL}</a></p>
    </div>
    <div class="contact-card">
      <h2>Follow Aaththi</h2>
      <p>New designs, party ideas and gift inspiration.</p>
      <ul class="social-list">{socials}</ul>
    </div>
  </div>
</section>"""
    write("contact/index.html", page(rel, "Contact | AATHTHI",
                                     "Contact AATHTHI for product questions, bulk orders and partnerships. For order help, use Contact seller on Amazon.com.",
                                     body, "contact/", current="contact"))


def build_404():
    # GitHub Pages serves 404.html from the root for any path, so use absolute links here.
    body = f"""
<section class="section center">
  <div class="wrap">
    <span class="eyebrow">Page not found</span>
    <h1>This page has wandered off</h1>
    <p class="lead">The page you&rsquo;re looking for doesn&rsquo;t exist or has moved.</p>
    <p style="margin-top:24px"><a class="btn btn-gold" href="/shop/">Shop all products</a> <a class="btn btn-line" href="/">Go home</a></p>
  </div>
</section>"""
    write("404.html", page("/", "Page not found | AATHTHI", "Page not found.", body, "404.html"))


def build_sitemap():
    urls = ["", "shop/", "about/", "contact/"] + [f'products/{p["slug"]}/' for p in PRODUCTS]
    today = date.today().isoformat()
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += "".join(f"  <url><loc>{SITE_URL}/{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls)
    xml += "</urlset>\n"
    write("sitemap.xml", xml)
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")


def clean_old_products():
    """Remove product pages for products that are no longer active."""
    pdir = os.path.join(ROOT, "products")
    if not os.path.isdir(pdir):
        return
    keep = {p["slug"] for p in PRODUCTS}
    for d in os.listdir(pdir):
        if d not in keep and os.path.isdir(os.path.join(pdir, d)):
            shutil.rmtree(os.path.join(pdir, d))


if __name__ == "__main__":
    clean_old_products()
    build_home()
    build_shop()
    for prod in PRODUCTS:
        build_product(prod)
    build_about()
    build_contact()
    build_404()
    build_sitemap()
    print(f"Built {len(PRODUCTS)} product pages (+ home, shop, about, contact, 404, sitemap).")
    hidden = [p["name"] for p in DATA["products"] if not p.get("active", True)]
    if hidden:
        print("Hidden (inactive):", ", ".join(hidden))
