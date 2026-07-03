"""Rend un fichier markdown en PDF presentable, via un navigateur Chromium headless.

Chaine : markdown -> HTML (theme clair, imprimable) avec les images embarquees en
base64 (le PDF est donc autonome) -> msedge/chrome --headless --print-to-pdf.

Usage :
    python outils/doc_pdf.py GUIDE.md chemin/vers/README.pdf

GUIDE.md est le guide utilisateur (celui livre dans le bundle). Sans argument, prend
GUIDE.md -> GUIDE.pdf a la racine.
"""
import base64
import mimetypes
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

RACINE = Path(__file__).resolve().parent.parent

GABARIT = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<style>
  @page {{ size: A4; margin: 18mm 16mm; }}
  body {{ font-family: "Segoe UI", "Calibri", Arial, sans-serif; color: #23272e;
          font-size: 11.5pt; line-height: 1.5; }}
  h1 {{ color: #2c6e2c; font-size: 22pt; margin: 0 0 4pt; }}
  h2 {{ color: #2c6e2c; font-size: 15pt; margin: 22pt 0 6pt;
        border-bottom: 1px solid #d9e2d9; padding-bottom: 3pt; }}
  h3 {{ color: #3a5; font-size: 12.5pt; margin: 14pt 0 4pt; }}
  p, li {{ margin: 4pt 0; }}
  code {{ font-family: "Consolas", "JetBrains Mono", monospace; font-size: 10.5pt;
          background: #eef1f4; padding: 1px 4px; border-radius: 3px; }}
  pre code {{ display: block; padding: 8pt 10pt; }}
  img {{ max-width: 100%; border: 1px solid #cfd6dd; border-radius: 5px;
         margin: 8pt 0; box-shadow: 0 1px 4px rgba(0,0,0,0.12); }}
  strong {{ color: #1c1f24; }}
  a {{ color: #2c6e2c; }}
</style></head><body>
{corps}
</body></html>"""


def _inline_images(html: str, base: Path) -> str:
    """Remplace la source de chaque <img ... src="chemin" ...> par une image base64, pour
    un PDF autonome. On capture l'attribut src ou qu'il soit dans la balise (markdown met
    alt avant src)."""
    def repl(m):
        avant, src, apres = m.group(1), m.group(2), m.group(3)
        chemin = (base / src).resolve()
        if not chemin.exists():
            return m.group(0)
        mime = mimetypes.guess_type(str(chemin))[0] or "image/png"
        donnees = base64.b64encode(chemin.read_bytes()).decode("ascii")
        return f'{avant}data:{mime};base64,{donnees}{apres}'
    return re.sub(r'(<img\b[^>]*?\bsrc=")([^"]+)(")', repl, html)


def _navigateur() -> str:
    candidats = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for c in candidats:
        if Path(c).exists():
            return c
    raise SystemExit("Aucun navigateur Chromium trouve (Edge/Chrome) pour le rendu PDF.")


def rendre(md_path: Path, pdf_path: Path) -> None:
    md_path = md_path.resolve()
    pdf_path = pdf_path.resolve()          # msedge exige un chemin absolu pour --print-to-pdf
    texte = md_path.read_text(encoding="utf-8")
    corps = markdown.markdown(texte, extensions=["fenced_code", "tables", "sane_lists"])
    corps = _inline_images(corps, md_path.parent)
    html = GABARIT.format(corps=corps)

    with tempfile.TemporaryDirectory() as d:
        html_tmp = Path(d) / "doc.html"
        html_tmp.write_text(html, encoding="utf-8")
        subprocess.run([_navigateur(), "--headless", "--disable-gpu",
                        "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf_path}", html_tmp.as_uri()],
                       check=True, capture_output=True)
    if not pdf_path.exists():
        raise SystemExit("Le navigateur n'a pas produit le PDF (verifie Edge/Chrome).")
    print("PDF ecrit :", pdf_path, f"({pdf_path.stat().st_size} octets)")


if __name__ == "__main__":
    md = Path(sys.argv[1]) if len(sys.argv) > 1 else RACINE / "GUIDE.md"
    pdf = Path(sys.argv[2]) if len(sys.argv) > 2 else RACINE / "GUIDE.pdf"
    rendre(md, pdf)
