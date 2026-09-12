#!/usr/bin/env python3
"""Compile original practice sheets and an editable Overleaf ZIP."""
from pathlib import Path
import json, subprocess, tempfile, zipfile, re, shutil
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/textbook-practice'
OUT.mkdir(parents=True,exist_ok=True)
DATA=json.loads((ROOT/'data/edexcel-practice.json').read_text())['books']
PREAMBLE=r'''\documentclass[10pt,a4paper]{article}
\usepackage[margin=0.85in]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern,amsmath,amssymb,graphicx,enumitem,microtype,fancyhdr,xcolor,needspace}
\usepackage[hidelinks]{hyperref}
\definecolor{lightgrey}{gray}{0.94}
\definecolor{midgrey}{gray}{0.35}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}
\setlist[enumerate]{itemsep=5pt,topsep=4pt}
\pagestyle{fancy}\fancyhf{}\renewcommand{\headrulewidth}{0pt}
\fancyfoot[L]{\footnotesize\color{midgrey}Arij Asad}
\fancyfoot[C]{\footnotesize\color{midgrey}Edexcel companion practice}
\fancyfoot[R]{\footnotesize\color{midgrey}\thepage}
\newcounter{question}
\newenvironment{question}[1]{\refstepcounter{question}\Needspace{5\baselineskip}\par\medskip\textbf{\thequestion.\ #1}\par}{\par\vspace{12mm}}
\begin{document}
'''
def tex(s):
 return s.replace('’',"'").replace('–','--').replace('—','---').replace('&','&')
for slug,b in DATA.items():
 title=b['title']
 document=PREAMBLE+r'\hypersetup{pdftitle={'+title+r' - Original practice and solutions},pdfauthor={Arij Asad}}'+'\n'
 document+=r'\begin{minipage}[c]{0.78\textwidth}{\Large\bfseries '+title+r'}\par Original practice check\end{minipage}\hfill\begin{minipage}[c]{0.17\textwidth}\IfFileExists{PS_logo.png}{\includegraphics[width=\linewidth]{PS_logo.png}}{\rule{0pt}{16mm}}\end{minipage}'+'\n\n'
 document+=r'\medskip\fcolorbox{black!20}{lightgrey}{\parbox{\dimexpr\linewidth-2\fboxsep-2\fboxrule\relax}{'+tex(b['intro'])+r' Attempt the questions before reading the solutions. These original questions sample selected skills; they are not an official Edexcel paper.}}'+'\n\n'
 for q in b['questions']:
  document+=r'\begin{question}{'+tex(q['topic'])+'}\n'+tex(q['prompt'])+'\n'+r'\end{question}'+'\n'
 document+=r'\Needspace{7\baselineskip}\textbf{Find the mistake}\par'+'\n'+tex(b['mistake']['prompt'])+'\n\n'
 document+=r'\vfill\small Further practice: \href{https://maths.arijasad.com/tmua-paper-archive.html}{TMUA papers and solutions} and \href{https://maths.arijasad.com/maths-topic-practice.html}{maths topic guides}.'+'\n'+r'\newpage'+'\n'+r'{\Large\bfseries Hints and worked solutions}\par\medskip'+'\n'
 for i,q in enumerate(b['questions'],1):
  document+=r'\Needspace{8\baselineskip}\subsection*{'+str(i)+'. '+tex(q['topic'])+'}\n'+r'\textit{Hint: '+tex(q['hint'])+r'}\par'+'\n'
  document+='\n\n'.join(tex(x) for x in q['solution'])+'\n\n'+r'\textbf{Answer:} '+tex(q['answer'])+'\n\n'
 document+=r'\Needspace{9\baselineskip}\subsection*{Find the mistake: correction}'+'\n'+'\n\n'.join(tex(x) for x in b['mistake']['solution'])+'\n\n'
 document+=r'\Needspace{6\baselineskip}\subsection*{What to practise next}\begin{enumerate}'+'\n'+''.join(r'\item '+tex(x)+'\n' for x in b['recommendations'])+r'\end{enumerate}\end{document}'+'\n'
 source=OUT/(slug+'-practice.tex');source.write_text(document)
 with tempfile.TemporaryDirectory(prefix='edexcel-tex-') as temp:
  run=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory',temp,str(source)],cwd=OUT,capture_output=True,text=True)
  log=(Path(temp)/(source.stem+'.log')).read_text(errors='replace')
  if run.returncode: raise RuntimeError(log[-5000:])
  overfull=re.findall(r'Overfull.*',log)
  if overfull: print(slug,'LAYOUT WARNING',overfull)
  output_pdf=OUT/(source.stem+'.pdf')
  built_pdf=Path(temp)/(source.stem+'.pdf')
  if shutil.which('gs'):
   subprocess.run(['gs','-sDEVICE=pdfwrite','-dCompatibilityLevel=1.7','-dPDFSETTINGS=/ebook','-dNOPAUSE','-dBATCH','-dQUIET','-sOutputFile='+str(output_pdf),str(built_pdf)],check=True)
  else: output_pdf.write_bytes(built_pdf.read_bytes())
  print(slug,re.findall(r'Output written on.*',log))
readme='''Edexcel companion practice - Arij Asad

Six original practice sheets, each with questions first and hints and worked solutions afterwards.

Upload this ZIP into a new Overleaf project. Choose the desired *-practice.tex file as the Main document and compile with pdfLaTeX. You may add PS_logo.png; the source reserves space and compiles without it.

The questions and explanations are original teaching materials. No Pearson textbook pages or third-party SolutionBank PDFs are included.
'''
with zipfile.ZipFile(OUT/'edexcel-practice-overleaf.zip','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('README.txt',readme)
 for p in sorted(OUT.glob('*.tex')): z.write(p,p.name)
print('Saved six PDFs and Overleaf ZIP')
