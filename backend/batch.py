import io
import re
import zipfile

import models
from documents import build_student_tex
from generation import generate_problems, student_seed_key
from pdf import compile_pdf

MAX_STUDENTS = 200
MAX_NAME_LENGTH = 100
MAX_UPLOAD_BYTES = 100_000


def parse_names(raw: bytes) -> list[str]:
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("The names file must be saved as UTF-8 text")

    names = [line.strip() for line in text.splitlines()]
    names = [n for n in names if n]

    if not names:
        raise ValueError("The names file has no names in it")
    if len(names) > MAX_STUDENTS:
        raise ValueError(f"Too many names (the limit is {MAX_STUDENTS})")
    for n in names:
        if len(n) > MAX_NAME_LENGTH:
            raise ValueError(f"This name is too long: {n[:30]}...")

    duplicates = sorted({n for n in names if names.count(n) > 1})
    if duplicates:
        raise ValueError(
            "Duplicate names would get identical tests: " + ", ".join(duplicates)
        )
    return names


def _safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^\w\- .]", "_", name).strip(" .")
    return cleaned or "student"


def build_student_zip(test: models.Test, names: list[str]) -> bytes:
    buffer = io.BytesIO()
    used: set[str] = set()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in names:
            problems = generate_problems(test, student_seed_key(test, name))
            tex = build_student_tex(test.name, name, problems)
            pdf_bytes = compile_pdf(tex)

            base = _safe_filename(name)
            candidate, n = base, 2
            while candidate.lower() in used:
                candidate = f"{base} ({n})"
                n += 1
            used.add(candidate.lower())

            zf.writestr(candidate + ".pdf", pdf_bytes)

    return buffer.getvalue()