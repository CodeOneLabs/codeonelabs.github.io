# CodeOneLabs — memegames.dev

Minimal project universe for CodeOneLabs. Project names link directly to their destinations. OneText and Trolley are the two largest planets; the original TrolleyDilemma page remains at `trolley.html`.

Static GitHub Pages site served from `main` at the root. Game source and credentials are not included.

Website: https://memegames.dev/
Privacy: https://memegames.dev/privacy.html (English, default)
Translations: privacy-ko.html, privacy-ja.html, privacy-zh.html, privacy-fr.html
Old address: https://codeonelabs.github.io/ redirects here, so links already handed out (App Store, Google Play, Steam) keep working. Keep this repository's name as it is, or the redirect stops.
Contact: contact@memegames.dev (Namecheap email forwarding)
Icon: assets/trolley-icon-128.png (128 x 128 PNG)

## Editing

- Privacy policy: edit the text in tools/build_privacy.py, then run `python3 tools/build_privacy.py` to regenerate all languages. Do not hand-edit privacy*.html.
- Home page: `index.html` includes the map CSS, stars, drag/zoom controls, and direct project links. Edit each `.planet-node` anchor to change its name, destination or desktop/mobile position. No build step or external library is required.
- About page: `about.html` contains the studio introduction, project platforms and public contact information. OneText links to `/OneText`, served by the existing OneText project Pages site.
- Trolley page: `trolley.html`. Shared privacy styles are still in `style.css`.
- `404.html`, `robots.txt` and `sitemap.xml` are hand-written; add a line to sitemap.xml for each new page.
- After changing style.css, bump CSS_VERSION in tools/build_privacy.py and the `?v=` in trolley.html and 404.html, then regenerate.

## Domain

- memegames.dev is registered at Namecheap. DNS (Advanced DNS):
  - A `@` → 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153
  - AAAA `@` → 2606:50c0:8000::153, 2606:50c0:8001::153, 2606:50c0:8002::153, 2606:50c0:8003::153
  - CNAME `www` → codeonelabs.github.io.
- The CNAME file in this repository sets the custom domain for GitHub Pages. .dev only works over HTTPS, so keep "Enforce HTTPS" on.
