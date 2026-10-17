_LATEX_SPECIAL = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def escape_latex(text: str) -> str:
    return "".join(_LATEX_SPECIAL.get(ch, ch) for ch in text)


PREAMBLE = r"""\documentclass[fleqn]{article}
\usepackage[left=1in, right=1in, top=1in, bottom=1in]{geometry}
\usepackage{mathexam}
\usepackage{amsmath, amssymb}

\let\ds\displaystyle
"""

INSTRUCTIONS = (
    r"Please show \textbf{all} your work! "
    r"Answers without supporting work will not be given credit."
)

WORK_SPACE = "1.5in"


def _header(exam_name: str, course: str, date_text: str) -> list[str]:
    lines = []
    if course:
        lines.append(r"\ExamClass{" + escape_latex(course) + "}")
    lines.append(r"\ExamName{" + escape_latex(exam_name) + "}")
    if date_text:
        lines.append(r"\ExamHead{" + escape_latex(date_text) + "}")
    return lines


def build_student_tex(
    test_name: str, student_name: str, problems, course: str = "", date_text: str = ""
) -> str:
    lines = [
        PREAMBLE,
        *_header(test_name, course, date_text),
        "",
        r"\begin{document}",
        r"\ExamInstrBox{" + INSTRUCTIONS + "}",
        r"\ExamNameLine",
        r"\vspace{-0.5cm}\noindent\hspace{1.5cm}\textbf{"
        + escape_latex(student_name)
        + "}",
        "",
        r"\begin{enumerate}",
        "",
    ]
    for p in problems:
        lines.append(r"\item " + p.question)
        lines.append(r"\vspace{" + WORK_SPACE + "}")
        lines.append("")
    lines.append(r"\end{enumerate}")
    lines.append(r"\end{document}")
    return "\n".join(lines)