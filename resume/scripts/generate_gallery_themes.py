#!/usr/bin/env python3
"""Generate 10 visually distinct LaTeX theme preambles for the CV gallery.

Each preamble defines the full document setup + the shared macro contract:
  \\resumeItem, \\resumeSubheading, resumeSubHeadingList, resumeItemList, \\cvheader
Body (sections + generated inputs) lives in body.tex; CI assembles:
  \\newcommand{\\cvvariant}{<v>} + preamble-NN + body.tex
All fonts are guaranteed present (latex-base psnfss, lmodern, tex-gyre, ebgaramond).
"""
import pathlib

OUT = pathlib.Path(__file__).resolve().parents[1] / "industrial" / "theme-gallery"
OUT.mkdir(parents=True, exist_ok=True)

CONTACT_LINES = [
    r"\href{mailto:alinkkh9@gmail.com}{alinkkh9@gmail.com} $|$",
    r"+98 991 296 3951 $|$",
    r"\href{https://alinikkhah2001.github.io}{alinikkhah2001.github.io} $|$",
    r"\href{https://linkedin.com/in/alinikkhah2001}{linkedin.com/in/alinikkhah2001}",
]

BASE_PKGS = [
    r"\usepackage{latexsym}",
    r"\usepackage[T1]{fontenc}",
    r"\usepackage[empty]{fullpage}",
    r"\usepackage{titlesec}",
    r"\usepackage[usenames,dvipsnames]{color}",
    r"\usepackage{verbatim}",
    r"\usepackage{enumitem}",
    r"\usepackage[hidelinks]{hyperref}",
    r"\usepackage{fancyhdr}",
    r"\usepackage[english]{babel}",
    r"\usepackage{tabularx}",
    r"\usepackage{microtype}",
]

MACROS = r"""
\newcommand{\resumeItem}[1]{%
  \item\small{#1 \vspace{-1pt}}%
}
\newcommand{\resumeSubheading}[4]{%
  \vspace{-2pt}\item
  \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
    \textbf{#1} & \small #2 \\
    \textit{\small#3} & \textit{\small #4} \\
  \end{tabular*}\vspace{-7pt}%
}
\renewcommand\labelitemii{--}
\newenvironment{resumeSubHeadingList}{%
  \begin{itemize}[leftmargin=0.15in, label={}]%
}{\end{itemize}}
\newenvironment{resumeItemList}{%
  \begin{itemize}[leftmargin=0.2in, topsep=2pt, itemsep=1pt, parsep=0pt]%
}{\end{itemize}\vspace{-3pt}}
"""

GEOM_TIGHT = "\n".join([
    r"\addtolength{\oddsidemargin}{-0.65in}",
    r"\addtolength{\evensidemargin}{-0.65in}",
    r"\addtolength{\textwidth}{1.3in}",
    r"\addtolength{\topmargin}{-.65in}",
    r"\addtolength{\textheight}{1.3in}",
])


def header_center(name_cmd, sub="Open to Relocation \\& Remote"):
    lines = "\n".join(["    " + ln for ln in CONTACT_LINES])
    return (
        "\\newcommand{\\cvheader}{%\n"
        "\\begin{center}\n"
        f"  {name_cmd} \\\\ \\vspace{{2pt}}\n"
        "\\small\n"
        f"  {sub} $|$\n"
        f"{lines}\n"
        "\\end{center}}\n"
    )


def section_rule(color="black"):
    return (
        "\\titleformat{\\section}{\n"
        "  \\vspace{-4pt}\\scshape\\raggedright\\large\n"
        f"}}{{0em}}{{}}[\\color{{{color}}}\\titlerule \\vspace{{-5pt}}]\n"
    )


THEMES = {}

# 01 classic — lmodern serif, black rules (current house style baseline)
THEMES["01-classic"] = "\n".join([
    r"\documentclass[letterpaper,11pt]{article}",
    *BASE_PKGS,
    r"\usepackage{lmodern}",
    GEOM_TIGHT,
    r"\urlstyle{same}\raggedbottom\raggedright",
    section_rule("black"),
    header_center(r"{\Huge \textsc{Ali Nikkhah}}"),
    MACROS,
])

# 02 teal — sans + Awesome-CV teal accent
THEMES["02-teal"] = "\n".join([
    r"\documentclass[letterpaper,11pt]{article}",
    *BASE_PKGS,
    r"\usepackage[scaled]{helvet}\renewcommand{\familydefault}{\sfdefault}",
    r"\definecolor{accent}{HTML}{2A7F62}",
    GEOM_TIGHT,
    r"\urlstyle{same}\raggedbottom\raggedright",
    "\\titleformat{\\section}{\n  \\vspace{-4pt}\\color{accent}\\bfseries\\raggedright\\large\n}{0em}{}[\\color{accent}\\titlerule \\vspace{-5pt}]\n",
    header_center(r"{\Huge \textbf{\color{accent}Ali Nikkhah}}"),
    MACROS,
])

# 03 blue — tex-gyre heros + modern blue
THEMES["03-blue"] = "\n".join([
    r"\documentclass[letterpaper,11pt]{article}",
    *BASE_PKGS,
    r"\usepackage{tgheros}\renewcommand{\familydefault}{\sfdefault}",
    r"\definecolor{accent}{HTML}{0E6EB0}",
    GEOM_TIGHT,
    r"\urlstyle{same}\raggedbottom\raggedright",
    "\\titleformat{\\section}{\n  \\vspace{-6pt}\\color{accent}\\bfseries\\raggedright\\Large\n}{0em}{}[\\vspace{-6pt}]\n",
    header_center(r"{\Huge \textbf{Ali Nikkhah}}"),
    MACROS,
])

# 04 slate band — dark header band, pagella serif body
THEMES["04-slate"] = "\n".join([
    r"\documentclass[letterpaper,11pt]{article}",
    *BASE_PKGS,
    r"\usepackage{tgpagella}",
    r"\definecolor{band}{HTML}{1A3A4A}",
    r"\definecolor{accent}{HTML}{1A3A4A}",
    GEOM_TIGHT,
    r"\urlstyle{same}\raggedbottom\raggedright",
    section_rule("accent"),
    "\\newcommand{\\cvheader}{%\n\\noindent\\colorbox{band}{\\parbox{\\dimexpr\\textwidth-2\\fboxsep}{\\color{white}\\begin{center}\\LARGE \\textsc{Ali Nikkhah} \\\\ \\small Open to Relocation \\& Remote $|$ \\href{mailto:alinkkh9@gmail.com}{\\color{white}alinkkh9@gmail.com} $|$ +98 991 296 3951 \\\\ \\href{https://alinikkhah2001.github.io}{\\color{white}alinikkhah2001.github.io} $|$ \\href{https://linkedin.com/in/alinikkhah2001}{\\color{white}linkedin.com/in/alinikkhah2001}\\end{center}}}\\vspace{4pt}}\n",
    MACROS,
])

# 05 deedy — tight helvetica, compact
THEMES["05-deedy"] = "\n".join([
    r"\documentclass[letterpaper,10pt]{article}",
    *BASE_PKGS,
    r"\usepackage[scaled=0.92]{helvet}\renewcommand{\familydefault}{\sfdefault}",
    r"\setlength{\parskip}{0pt}\setlength{\parindent}{0pt}",
    "\n".join([
        r"\addtolength{\oddsidemargin}{-0.7in}",
        r"\addtolength{\evensidemargin}{-0.7in}",
        r"\addtolength{\textwidth}{1.4in}",
        r"\addtolength{\topmargin}{-.7in}",
        r"\addtolength{\textheight}{1.4in}",
    ]),
    r"\urlstyle{same}\raggedbottom\raggedright",
    "\\titleformat{\\section}{\n  \\vspace{-6pt}\\bfseries\\raggedright\\normalsize\\uppercase\n}{0em}{}[\\titlerule \\vspace{-6pt}]\n",
    header_center(r"{\Large \textbf{Ali Nikkhah}}"),
    MACROS,
])

# 06 plasmati — palatino + muted slate
THEMES["06-plasmati"] = "\n".join([
    r"\documentclass[letterpaper,11pt]{article}",
    *BASE_PKGS,
    r"\usepackage[sc]{mathpazo}",
    r"\definecolor{accent}{HTML}{4A6572}",
    GEOM_TIGHT,
    r"\urlstyle{same}\raggedbottom\raggedright",
    "\\titleformat{\\section}{\n  \\vspace{-4pt}\\color{accent}\\scshape\\raggedright\\large\n}{0em}{}[\\color{accent}\\titlerule \\vspace{-5pt}]\n",
    header_center(r"{\Huge \textsc{\color{accent}Ali Nikkhah}}"),
    MACROS,
])

# 07 mono — courier headings, franco minimal
THEMES["07-mono"] = "\n".join([
    r"\documentclass[letterpaper,11pt]{article}",
    *BASE_PKGS,
    r"\usepackage{lmodern}",
    r"\usepackage[scaled=0.95]{courier}",
    GEOM_TIGHT,
    r"\urlstyle{same}\raggedbottom\raggedright",
    "\\titleformat{\\section}{\n  \\vspace{-4pt}\\ttfamily\\raggedright\\large\n}{0em}{}[\\titlerule \\vspace{-5pt}]\n",
    header_center(r"{\Huge \texttt{Ali Nikkhah}}"),
    MACROS,
])

# 08 ieee — two column, times
THEMES["08-ieee"] = "\n".join([
    r"\documentclass[letterpaper,10pt,twocolumn]{article}",
    *BASE_PKGS,
    r"\usepackage{mathptmx}",
    r"\setlength{\columnsep}{0.3in}",
    r"\urlstyle{same}\raggedbottom",
    "\\titleformat{\\section}{\n  \\vspace{-4pt}\\scshape\\centering\\normalsize\n}{0em}{}[\\vspace{-4pt}]\n",
    "\\newcommand{\\cvheader}{%\n\\twocolumn[{\\begin{center}\\Large \\textsc{Ali Nikkhah} \\\\ \\small Open to Relocation \\& Remote $|$ alinkkh9@gmail.com $|$ +98 991 296 3951 \\\\ alinikkhah2001.github.io $|$ linkedin.com/in/alinikkhah2001\\end{center}\\vspace{4pt}}]}\n",
    MACROS,
])

# 09 garamond — ebgaramond, airy
THEMES["09-garamond"] = "\n".join([
    r"\documentclass[letterpaper,11.5pt]{article}",
    *BASE_PKGS,
    r"\usepackage{ebgaramond}",
    GEOM_TIGHT,
    r"\urlstyle{same}\raggedbottom\raggedright",
    "\\titleformat{\\section}{\n  \\vspace{-2pt}\\itshape\\raggedright\\Large\n}{0em}{}[\\vspace{-4pt}]\n",
    header_center(r"{\Huge Ali Nikkhah}"),
    MACROS,
])

# 10 executive — bookman + burgundy, generous rules
THEMES["10-executive"] = "\n".join([
    r"\documentclass[letterpaper,11pt]{article}",
    *BASE_PKGS,
    r"\usepackage{bookman}",
    r"\definecolor{accent}{HTML}{7B1E26}",
    GEOM_TIGHT,
    r"\urlstyle{same}\raggedbottom\raggedright",
    "\\titleformat{\\section}{\n  \\vspace{-4pt}\\color{accent}\\bfseries\\raggedright\\large\n}{0em}{}[{\\color{accent}\\rule{\\textwidth}{1.5pt}} \\vspace{-5pt}]\n",
    header_center(r"{\Huge \textbf{Ali Nikkhah}}"),
    MACROS,
])

for slug, tex in THEMES.items():
    (OUT / f"preamble-{slug}.tex").write_text("% THEME " + slug + " — gallery preamble (auto-generated, do not edit)\n" + tex + "\n", encoding="utf-8")
    print("preamble", slug)

BODY = r"""\begin{document}
\cvheader

\section{Summary}
\input{segments/generated/\cvvariant/summary.tex}

\section{Technical Skills}
\input{segments/generated/\cvvariant/skills.tex}

\section{Professional Experience}
\begin{resumeSubHeadingList}
\input{segments/generated/\cvvariant/experience.tex}
\end{resumeSubHeadingList}

\section{Selected Projects \& Research}
\begin{resumeSubHeadingList}
\input{segments/generated/\cvvariant/projects.tex}
\end{resumeSubHeadingList}

\section{Education}
\begin{resumeSubHeadingList}
\input{segments/common/education.tex}
\end{resumeSubHeadingList}

\end{document}
"""
(OUT / "body.tex").write_text("% Shared gallery body — variant picked via \\cvvariant\n" + BODY, encoding="utf-8")
print("body.tex")
