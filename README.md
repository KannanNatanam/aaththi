# aaththi.com: AATHTHI brand website

A fast, static website for GitHub Pages. It shows every AATHTHI product, and each
"Buy on Amazon" button sends shoppers to the Amazon.com product page through
your Amazon Attribution link.

## Publish it (first time)

1. Open your website repository on GitHub.
2. Delete the old "coming soon" files, but **keep `CNAME`** (this folder includes
   one with `www.aaththi.com`, so either copy is fine).
3. Upload everything in this folder: **Add file → Upload files**, drag the
   folders and files in, then **Commit changes**.
4. Wait 1–2 minutes and open https://www.aaththi.com.

## Add a pending Amazon Attribution link (no rebuild needed)

Open `assets/js/amazon-links.js` on GitHub, click the pencil icon, and paste the
link between the quotes next to the product marked `PENDING`. Commit, and you're done.
Until a link is added, that product's button opens the plain Amazon page, so it
still works but the sale isn't tracked for the Brand Referral Bonus.

There's also an optional `STORE` entry for an Attribution link to your Amazon Brand Store.

## Change or add products

Product text, categories and image lists live in `data/products.json`.
After editing it, run this from the folder:

    python3 tools/build.py

Then upload the changed files. Full steps are at the top of `tools/build.py`.

- **Show or hide a product:** set `"active": true` or `false`.
- **Product video:** save it as `assets/products/<slug>/video.mp4` (720p, under about 5 MB) with a
  `video-poster.webp` still frame, and add `"video": "video.mp4", "video_poster": "video-poster.webp"`
  to that product in `data/products.json`.
- **New product images:** put them in `assets/products/<slug>/` as `1.webp`, `2.webp`
  and so on, plus `thumb.webp`.

## Notes

- Fonts: headings use Cormorant Garamond and body text uses Quicksand (from the
  brand guide). Qochy, the brand-guide display font, is a demo font that isn't
  licensed for websites, so the logo images carry the brand lettering instead.
- TikTok isn't linked yet because the old site pointed to tiktok.com rather than your
  account. Add it to the `SOCIAL` list in `tools/build.py` and rebuild.
- The site shows no prices, so nothing goes out of date. Shoppers see the current
  price on Amazon.
