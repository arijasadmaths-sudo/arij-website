#!/usr/bin/env python3
"""Build original diagnostic worksheets, solutions and an Overleaf source ZIP.

Run from any directory with Python 3 and pdflatex on PATH. The PDF build is
performed in a temporary directory, leaving only the public deliverables.
"""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "algebra-diagnostic"
DATA = json.loads((ROOT / "data" / "algebra-diagnostic.json").read_text())
QUESTIONS = DATA["questions"]

PREAMBLE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[a4paper,margin=22mm,headheight=14pt]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{fancyhdr}
\usepackage[hidelinks]{hyperref}
\setlength{\parindent}{0pt}
\setlength{\parskip}{7pt}
\setlength{\emergencystretch}{2em}
\pagestyle{fancy}
\fancyhf{}
\fancyfoot[L]{\small Arij Asad\quad |\quad maths.arijasad.com}
\fancyfoot[R]{\small\thepage}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0.3pt}
\newcommand{\smallheading}[1]{\par\vspace{9pt}{\large\bfseries #1}\par\vspace{1pt}}
\begin{document}
"""


def clean(text):
    # The data contains trusted LaTeX mathematical expressions and ordinary text.
    return text.replace("\u2019", "'").replace("\u2013", "--").replace("\u2014", "---")


def worksheet(followup=False):
    subtitle = "Follow-up questions" if followup else "Student questions"
    lines = [PREAMBLE, r"\fancyhead[L]{\small Algebra to TMUA}",
             r"\fancyhead[R]{\small " + subtitle + "}"]
    for page in range(2):
        if page:
            lines.append(r"\newpage")
        lines += [r"{\LARGE\bfseries Algebra to TMUA}\par",
                  r"{\large " + subtitle + r"}\par"]
        if not page:
            lines.append(r"Name: \hrulefill\qquad Date: \hrulefill\par")
            if followup:
                lines.append(r"Return to the questions matched to your diagnostic. Work without a calculator and explain each step. Use extra paper if needed.\par")
            else:
                lines.append(r"Suggested time: 20 minutes. Work without a calculator and show your reasoning. If you get stuck, record what you tried and move on.\par")
                lines.append(r"{\small This short diagnostic helps choose practice. It is not a TMUA mock or a score predictor.}\par")
        else:
            lines.append(r"{\small Continue to show your reasoning. Use extra paper if needed.}\par")
        for question in QUESTIONS[page * 4:(page + 1) * 4]:
            text = question["followup"] if followup else question["prompt"]
            lines.append(r"\vspace{4pt}\textbf{" + str(question["number"]) + r".}\quad " + clean(text) + r"\par\vfill")
        lines.append(r"\vspace{8mm}")
    return "\n".join(lines) + "\n\\end{document}\n"


def teacher_solutions():
    lines = [PREAMBLE, r"\fancyhead[L]{\small Algebra to TMUA}",
             r"\fancyhead[R]{\small Teacher solutions}"]
    for i, question in enumerate(QUESTIONS):
        if i:
            lines.append(r"\newpage")
        lines += [r"{\LARGE\bfseries " + str(question["number"]) + ". " + clean(question["title"]) + r"}\par",
                  r"\smallheading{Diagnostic question}", clean(question["prompt"]) + r"\par",
                  r"\textbf{Hint.} " + clean(question["hint"]) + r"\par",
                  r"\smallheading{Worked solution}"]
        lines.extend(clean(p) + "\n" for p in question["solution"])
        lines += [r"\textbf{Answer:} " + clean(question["answer"]) + r"\par",
                  r"\smallheading{What to notice}", clean(question["misconception"]) + r"\par",
                  r"\smallheading{Matched follow-up}", clean(question["followup"]) + r"\par"]
        lines.extend(clean(p) + "\n" for p in question["followup_solution"])
        lines += [r"\textbf{Follow-up answer:} " + clean(question["followup_answer"]) + r"\par",
                  r"\vfill\smallheading{Teaching note}",
                  r"Ask the student to explain the step that made the difference, then try the follow-up without looking at the worked solution.\par",
                  r"{\small Further practice: " + "; ".join(r"\href{https://maths.arijasad.com/" + url + "}{" + label.replace("&", r"\&") + "}" for url, label in question["links"]) + ".}"]
    return "\n".join(lines) + "\n\\end{document}\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sources = {
        "algebra-to-tmua-questions.tex": worksheet(),
        "algebra-to-tmua-follow-up.tex": worksheet(followup=True),
        "algebra-to-tmua-teacher-solutions.tex": teacher_solutions(),
    }
    for name, source in sources.items():
        (OUT / name).write_text(source)
    with tempfile.TemporaryDirectory(prefix="algebra-diagnostic-") as scratch:
        scratch = Path(scratch)
        for name in sources:
            shutil.copyfile(OUT / name, scratch / name)
            for _ in range(2):
                result = subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", name],
                    cwd=scratch, capture_output=True, text=True,
                )
                if result.returncode:
                    raise RuntimeError(result.stdout[-6000:])
            log = (scratch / name.replace(".tex", ".log")).read_text()
            if "Overfull" in log:
                raise RuntimeError("Overfull TeX box in " + name)
            pdf_name = name.replace(".tex", ".pdf")
            shutil.copyfile(scratch / pdf_name, OUT / pdf_name)
            print(pdf_name)
    readme = """ALGEBRA TO TMUA - OVERLEAF SOURCE

Original questions and explanations prepared for Arij Asad's teaching resources.

Upload this ZIP to Overleaf and select main.tex as the main document. Compile
with pdfLaTeX. The default output is the two-page student diagnostic.

To choose another document, change the single input line in main.tex to:
  \\input{algebra-to-tmua-follow-up.tex}
or
  \\input{algebra-to-tmua-teacher-solutions.tex}

Each of the three files is also a complete standalone LaTeX document.
The student and follow-up documents deliberately omit answers. Full worked
solutions, hints and teaching notes appear in the teacher document.

Suggested diagnostic time: 20 minutes. This is a short practice diagnostic,
not a TMUA mock, a complete syllabus assessment or a score predictor.

Resource page: https://maths.arijasad.com/algebra-to-tmua-diagnostic.html
"""
    with zipfile.ZipFile(OUT / "algebra-to-tmua-overleaf.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("README.txt", readme)
        archive.writestr("main.tex", "\\input{algebra-to-tmua-questions.tex}\n")
        for name, source in sources.items():
            archive.writestr(name, source)


if __name__ == "__main__":
    main()
