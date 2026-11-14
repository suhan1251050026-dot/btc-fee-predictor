# Fonts

The app is set in **Ferry** for headings and **Salvatore** for normal text, with
**Quair Triangle** as a second choice for normal text. All three are paid fonts,
so their files are not in this repo. Until you add them, the app uses free
stand-ins: **Archivo Black** for headings and **Archivo** for body text
(both SIL Open Font License, in `fallback/`).

## Add the paid fonts

**Ferry** — buy from Letters from Sweden (letters.cz) and copy in:

| File | Used by |
|---|---|
| `Ferry.woff2` | the web page |
| `Ferry.otf` | matplotlib charts |

Ferry ships as a single black weight, uppercase letters only — the page
already sets headings in capitals to match.

**Salvatore** — buy the desktop + web licence from W Type Foundry (wtypefoundry.com)
and copy in:

| Style | Web page (`.woff2`) | Charts (`.otf`) |
|---|---|---|
| Regular | `Salvatore-Regular.woff2` | `Salvatore-Regular.otf` |
| Italic | `Salvatore-Italic.woff2` | `Salvatore-Italic.otf` |
| Bold | `Salvatore-Bold.woff2` | `Salvatore-Bold.otf` |
| Bold Italic | `Salvatore-BoldItalic.woff2` | `Salvatore-BoldItalic.otf` |

**Quair Triangle** — buy from Alias (alias.design) or MyFonts, then copy in:

| Style | Web page (`.woff2`) | Charts (`.otf`) |
|---|---|---|
| Regular | `QuairTriangle-Regular.woff2` | `QuairTriangle-Regular.otf` |
| Italic | `QuairTriangle-Italic.woff2` | `QuairTriangle-Italic.otf` |
| Bold | `QuairTriangle-Bold.woff2` | `QuairTriangle-Bold.otf` |
| Bold Italic | `QuairTriangle-BoldItalic.woff2` | `QuairTriangle-BoldItalic.otf` |

- The web page loads the `.woff2` files (served from `/fonts/`).
- Charts are SVG, so they use the same web fonts.
- If a font is already installed on your PC, the browser uses it even without these files.

Rebuild after adding fonts: `cd frontend ; npm run build`.
