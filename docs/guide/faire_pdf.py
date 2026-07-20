#!/usr/bin/env python3
"""Fabrique le PDF du guide a partir du Markdown et des captures.

Chaine : Markdown -> HTML autonome -> Chrome headless -> PDF. Rien a installer :
ni pandoc ni weasyprint ne sont presents sur ce poste, Chrome si.

Les images sont inlinees en data: URI pour que le HTML soit autonome et que Chrome
n'ait aucune requete a faire au moment de l'impression.

  python3 faire_pdf.py <guide.md> <sortie.pdf>
"""
import base64
import mimetypes
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

CSS = """
@page { size: A4; margin: 18mm 16mm 16mm 16mm; }
@page { @bottom-center { content: counter(page); } }
body { font-family: "Source Serif 4", "DejaVu Serif", Georgia, serif;
       font-size: 10.5pt; line-height: 1.5; color: #1a1a1a; }
h1 { font-size: 20pt; color: #0f6cbf; border-bottom: 2px solid #0f6cbf;
     padding-bottom: 4px; margin-top: 0; page-break-before: always; }
h1:first-of-type { page-break-before: avoid; }
h2 { font-size: 14pt; color: #0f6cbf; margin-top: 1.4em; page-break-after: avoid; }
h3 { font-size: 11.5pt; margin-top: 1.1em; page-break-after: avoid; }
h4 { font-size: 10.5pt; margin-top: 1em; page-break-after: avoid; }
p, li { orphans: 3; widows: 3; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 9pt;
       background: #f2f4f7; padding: 1px 4px; border-radius: 3px; }
/* pre-wrap et pas overflow-x : sur du papier rien ne defile, une ligne trop longue
   serait coupee sans le moindre signe et la commande imprimee deviendrait fausse. */
pre { background: #f7f8fa; border: 1px solid #dde1e7; border-left: 3px solid #0f6cbf;
      border-radius: 4px; padding: 8px 10px; page-break-inside: avoid;
      white-space: pre-wrap; overflow-wrap: break-word; }
pre code { background: none; padding: 0; font-size: 8.6pt; line-height: 1.4; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 9.4pt;
        page-break-inside: avoid; }
th, td { border: 1px solid #ccd2da; padding: 5px 7px; text-align: left;
         vertical-align: top; }
th { background: #eef4fb; font-weight: 600; }
img { max-width: 100%; height: auto; display: block; margin: 0.8em auto;
      border: 1px solid #ccd2da; border-radius: 4px; page-break-inside: avoid; }
blockquote { border-left: 3px solid #e8a33d; background: #fdf6e9; margin: 1em 0;
             padding: 8px 12px; page-break-inside: avoid; }
blockquote p { margin: 0.3em 0; }
a { color: #0f6cbf; text-decoration: none; }
hr { border: none; border-top: 1px solid #dde1e7; margin: 1.6em 0; }
.legende { font-size: 8.8pt; color: #667; text-align: center; margin-top: -0.5em;
           margin-bottom: 1.2em; font-style: italic; }
"""


def inliner_images(html: str, base: Path) -> str:
    """Remplace chaque src par un data: URI. Chrome imprime alors sans requete."""
    def rempl(m):
        src = m.group(1)
        if src.startswith(("data:", "http:", "https:")):
            return m.group(0)
        chemin = (base / src).resolve()
        if not chemin.exists():
            print(f"  ATTENTION image absente : {src}", file=sys.stderr)
            return m.group(0)
        t = mimetypes.guess_type(str(chemin))[0] or "image/png"
        d = base64.b64encode(chemin.read_bytes()).decode()
        return m.group(0).replace(src, f"data:{t};base64,{d}")
    return re.sub(r'<img[^>]+src="([^"]+)"', rempl, html)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    source, sortie = Path(sys.argv[1]), Path(sys.argv[2])
    texte = source.read_text(encoding="utf-8")

    corps = markdown.markdown(texte, extensions=["tables", "fenced_code", "toc",
                                                 "attr_list", "sane_lists"])
    corps = inliner_images(corps, source.parent)
    # Une ligne en italique seule juste apres une image devient une legende.
    corps = re.sub(r'(</p>\s*)<p><em>(.*?)</em></p>',
                   r'\1<p class="legende">\2</p>', corps)

    html = (f'<!doctype html><html lang="fr"><head><meta charset="utf-8">'
            f'<title>{source.stem}</title><style>{CSS}</style></head>'
            f'<body>{corps}</body></html>')

    with tempfile.TemporaryDirectory() as d:
        page = Path(d) / "guide.html"
        page.write_text(html, encoding="utf-8")
        r = subprocess.run(
            ["google-chrome", "--headless", "--disable-gpu", "--no-sandbox",
             "--no-pdf-header-footer", "--print-to-pdf-no-header",
             f"--print-to-pdf={sortie.resolve()}", page.as_uri()],
            capture_output=True, text=True, timeout=180)
        if not sortie.exists():
            sys.exit(f"Chrome n'a pas produit le PDF :\n{r.stderr[-800:]}")

    pages = len(re.findall(rb'/Type\s*/Page\b', sortie.read_bytes()))
    print(f"{sortie}  {sortie.stat().st_size // 1024} Ko  environ {pages} pages")


if __name__ == "__main__":
    main()
