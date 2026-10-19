import subprocess
import tempfile
from pathlib import Path


class LatexError(Exception):
    pass


def compile_pdf(tex: str) -> bytes:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        (tmp_dir / "doc.tex").write_text(tex, encoding="utf-8")

        try:
            result = subprocess.run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "-no-shell-escape",
                    "doc.tex",
                ],
                cwd=tmp_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )
        except FileNotFoundError:
            raise LatexError("pdflatex was not found on this machine")
        except subprocess.TimeoutExpired:
            raise LatexError("pdflatex timed out")

        pdf_path = tmp_dir / "doc.pdf"
        if result.returncode != 0 or not pdf_path.exists():
            raise LatexError(result.stdout[-2000:])
        return pdf_path.read_bytes()