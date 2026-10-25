# /// script
# requires-python = ">=3.13"
# dependencies = ["markdown"]
# ///
"""Genera APUNTES.epub y APUNTES.azw3 (Kindle) a partir de APUNTES.md y,
como anexo al final, CODIGO.md.

Uso (desde la raíz del repo):
    uv run scripts/apuntes_ebook.py

Necesita Calibre instalado (`ebook-convert`): sudo apt install calibre
"""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "APUNTES.md"
ANEXO = RAIZ / "CODIGO.md"
SALIDA = RAIZ / "APUNTES.epub"
# AZW3 (KF8): formato actual de Kindle para copiar por USB. MOBI es el antiguo.
SALIDA_KINDLE = RAIZ / "APUNTES.azw3"

# Estilos pensados para pantalla pequeña: el código hace salto de línea
# en vez de obligar a desplazarse en horizontal.
CSS = """
body { font-family: serif; line-height: 1.45; }
h1, h2, h3, h4 { font-family: sans-serif; line-height: 1.2; }
h1 { font-size: 1.6em; }
h2 { font-size: 1.4em; page-break-before: always; border-bottom: 1px solid #888; }
h3 { font-size: 1.2em; margin-top: 1.4em; }
h4 { font-size: 1.05em; margin-top: 1.2em; }
code { font-family: monospace; font-size: 0.85em; background: #eee; padding: 0 0.15em; }
pre { font-family: monospace; font-size: 0.72em; background: #f2f2f2; border-left: 3px solid #999;
      padding: 0.5em; white-space: pre-wrap; word-wrap: break-word; }
pre code { background: none; padding: 0; font-size: 1em; }
table { border-collapse: collapse; font-size: 0.8em; width: 100%; }
th, td { border: 1px solid #999; padding: 0.25em 0.4em; vertical-align: top; }
th { background: #e6e6e6; }
"""


def a_html(texto: str, nivel_base: int = 1) -> str:
    """Markdown -> HTML (tablas y bloques ``` incluidos).

    `nivel_base` desplaza los títulos: con 2, `#` sale como <h2>, `##` como <h3>...
    """
    return markdown.markdown(
        texto,
        extensions=["tables", "fenced_code", "sane_lists", "toc"],
        extension_configs={"toc": {"baselevel": nivel_base}},
    )


def main() -> None:
    if shutil.which("ebook-convert") is None:
        sys.exit("Falta `ebook-convert`. Instala Calibre: sudo apt install calibre")

    # 1. Markdown -> HTML
    cuerpo = a_html(ENTRADA.read_text(encoding="utf-8"))

    # Anexo: CODIGO.md con los títulos un nivel más abajo, para que en el índice
    # sea un solo capítulo (h2) con sus secciones (h3) y ficheros (h4) dentro.
    if ANEXO.exists():
        anexo = ANEXO.read_text(encoding="utf-8")
        anexo = re.sub(r"^# ", "# Anexo · ", anexo, count=1, flags=re.MULTILINE)
        cuerpo += a_html(anexo, nivel_base=2)

    html = (
        '<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">'
        f"<title>Apuntes</title><style>{CSS}</style></head><body>{cuerpo}</body></html>"
    )

    # 2. HTML -> EPUB con Calibre; los títulos ## / ### / #### forman el índice
    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "apuntes.html"
        html_path.write_text(html, encoding="utf-8")
        # Sin formatear: más legible con una opción y su valor por línea.
        # fmt: off
        comando = [
            "ebook-convert", str(html_path), str(SALIDA),
            "--title", "Apuntes · App de gastos",
            "--authors", "Luis",
            "--language", "es",
            "--level1-toc", "//h:h2",
            "--level2-toc", "//h:h3",
            "--level3-toc", "//h:h4",
            "--chapter", "//h:h2",
            "--chapter-mark", "pagebreak",
            "--no-default-epub-cover",
        ]
        # fmt: on
        subprocess.run(comando, check=True, stdout=subprocess.DEVNULL)

    # 3. EPUB -> AZW3: conserva índice, metadatos y estilos
    subprocess.run(
        ["ebook-convert", str(SALIDA), str(SALIDA_KINDLE)],
        check=True,
        stdout=subprocess.DEVNULL,
    )

    for fichero in (SALIDA, SALIDA_KINDLE):
        print(f"Generado: {fichero.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
