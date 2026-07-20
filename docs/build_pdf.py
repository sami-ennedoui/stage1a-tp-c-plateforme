"""Génère les PDF de la documentation à partir des .md de docs/.

Convertit chaque Markdown en HTML (avec un CSS d'impression) puis imprime en PDF avec
Microsoft Edge en mode headless. Sortie dans docs/pdf/ (git-ignoré, regénérable).

Prérequis : Windows avec Edge, et `pip install markdown pygments`.
Usage : python docs/build_pdf.py
"""
import subprocess
import time
from pathlib import Path

import markdown

DOCS = Path(__file__).resolve().parent
OUT = DOCS / "pdf"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

CSS = """
@page { size: A4; margin: 20mm 18mm; }
* { box-sizing: border-box; }
body { font-family: 'Segoe UI', 'Calibri', system-ui, sans-serif; font-size: 11pt;
       line-height: 1.5; color: #1a1a1a; }
h1 { font-size: 22pt; color: #14364a; border-bottom: 3px solid #2c7a7b;
     padding-bottom: 6px; margin-top: 0; }
h2 { font-size: 15pt; color: #14364a; margin-top: 22px;
     border-bottom: 1px solid #d0d7de; padding-bottom: 3px; }
h3 { font-size: 12.5pt; color: #21506b; margin-top: 16px; }
code { font-family: 'Cascadia Code', 'Consolas', monospace; font-size: 9.5pt;
       background: #f2f4f6; padding: 1px 4px; border-radius: 3px; }
pre { background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px;
      padding: 10px 12px; overflow-x: auto; page-break-inside: avoid; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 12px 0;
        page-break-inside: avoid; font-size: 10pt; }
th, td { border: 1px solid #d0d7de; padding: 6px 9px; text-align: left;
         vertical-align: top; }
th { background: #eef2f5; color: #14364a; }
tr:nth-child(even) td { background: #fafbfc; }
blockquote { border-left: 4px solid #2c7a7b; margin: 12px 0; padding: 4px 14px;
             background: #f0f6f6; color: #333; }
a { color: #2c7a7b; }
h1, h2, h3 { page-break-after: avoid; }
"""

GABARIT = ('<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">'
           "<style>{css}</style></head><body>{corps}</body></html>")


def construire() -> int:
    OUT.mkdir(exist_ok=True)
    fichiers = sorted(DOCS.glob("*.md"))
    reussis = 0
    for md in fichiers:
        corps = markdown.markdown(
            md.read_text(encoding="utf-8"),
            extensions=["tables", "fenced_code", "toc", "sane_lists"])
        html_path = OUT / (md.stem + ".html")
        html_path.write_text(GABARIT.format(css=CSS, corps=corps), encoding="utf-8")
        pdf_path = OUT / (md.stem + ".pdf")
        subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf_path}", html_path.as_uri()],
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
        for _ in range(20):
            if pdf_path.exists() and pdf_path.stat().st_size > 0:
                break
            time.sleep(0.3)
        html_path.unlink(missing_ok=True)
        ok = pdf_path.exists() and pdf_path.stat().st_size > 0
        print(f"{'OK ' if ok else 'ECHEC'} {md.name} -> {pdf_path.name}")
        reussis += ok
    print(f"PDF generes : {reussis}/{len(fichiers)}")
    return 0 if reussis == len(fichiers) else 1


if __name__ == "__main__":
    raise SystemExit(construire())
