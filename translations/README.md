# Static translations

English remains the original at `/`, `/about/`, and `/start-here/`.
Danish, German, and Simplified Chinese use `/da/`, `/de/`, and `/zh-hans/`.

Edit the three English pages for shared structure. Update the corresponding
English-string keys and translations in each JSON file when copy changes.
The JSON files also contain descriptions and interactive/accessibility text.
Game names, technical identifiers, recording destinations and metric values
are intentionally preserved. Other sections remain English.

Regenerate and validate from the repository root:

```sh
python3 scripts/build-translations.py
python3 scripts/check-translations.py
node scripts/check-languages.cjs
node --check assets/site.js
```

Commit the generated HTML and sitemaps together with the source changes.
GitHub Pages serves the translated content without requiring JavaScript.

The language links are ordinary anchors, usable without JavaScript. On a fresh
English entry, `assets/languages.js` uses the saved explicit selection first,
then the browser's ordered language list. Unsupported languages fall back to
English. Traditional Chinese locales are not treated as Simplified Chinese.
Direct localized URLs, same-origin English navigation and browser back/forward
navigation are respected. Changing language keeps the page, query and fragment.
A preference is stored locally only when a visitor selects a language; storage
failure is tolerated. Canonicals are self-referencing, with reciprocal
`hreflang` links and English as `x-default`.
