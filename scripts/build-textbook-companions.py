#!/usr/bin/env python3
"""Build the six Edexcel companions, preserving static content and source credits."""
from pathlib import Path
from html import escape as e
from urllib.parse import quote
import json, re, subprocess
from site_navigation import install_archive_navigation

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://maths.arijasad.com/'
CATALOGUE = json.loads((ROOT/'data/edexcel-textbooks.json').read_text())
PRACTICE = json.loads((ROOT/'data/edexcel-practice.json').read_text())['books']
BOOKS = CATALOGUE['books']
SLUGS = {'pure-maths-year-1':'pure-year-1','pure-maths-year-2':'pure-year-2','core-pure-maths-1':'core-pure-1','core-pure-maths-2':'core-pure-2'}
META = {
 'pure-year-1':('Pure mathematics','Pure Year 1','Build reliable algebra, graphs, trigonometry and introductory calculus.'),
 'pure-year-2':('Pure mathematics','Pure Year 2','Connect functions, sequences and calculus, then choose methods in mixed problems.'),
 'statistics-mechanics-year-1':('Applied mathematics','Statistics & Mechanics Year 1','Choose statistical models, interpret data and translate motion into equations.'),
 'statistics-mechanics-year-2':('Applied mathematics','Statistics & Mechanics Year 2','Develop conditional probability, normal distributions, forces and kinematics.'),
 'core-pure-1':('Further mathematics','Core Pure 1','Build fluency with complex numbers, matrices, vectors and mathematical proof.'),
 'core-pure-2':('Further mathematics','Core Pure 2','Develop complex-number methods, polar coordinates and differential equations.'),
}
TEMPLATE = (ROOT/'tmua-logic-proof.html').read_text()
HEADER = re.search(r'  <header class="site-header">.*?</header>',TEMPLATE,re.S)[0].replace(' aria-current="page"','')
FOOTER = re.search(r'  <footer>.*?</footer>',TEMPLATE,re.S)[0]

def strings(obj):
 if isinstance(obj,str): yield obj
 elif isinstance(obj,list):
  for x in obj: yield from strings(x)
 elif isinstance(obj,dict):
  for x in obj.values(): yield from strings(x)

MATH = json.loads(subprocess.run(['node',str(ROOT/'scripts/render-textbook-maths.cjs')],input=json.dumps(list(set(strings(PRACTICE)))),text=True,capture_output=True,check=True).stdout)
def m(text): return MATH.get(text,e(text))
def paras(value): return ''.join('<p>'+m(x)+'</p>' for x in (value if isinstance(value,list) else [value]))
def slug(book): return SLUGS.get(book['id'],book['id'])
def filename(book): return 'edexcel-'+slug(book)+'.html'

def page(path,title,description,content,hub=False):
 schema={'@context':'https://schema.org','@type':'CollectionPage','name':title,'description':description,'url':ORIGIN+path,'author':{'@type':'Person','name':'Arij Asad','url':ORIGIN+'about.html'}}
 return install_archive_navigation(f'''<!DOCTYPE html>
<html lang="en-GB"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)} | Arij Asad</title><meta name="description" content="{e(description)}"><link rel="canonical" href="{ORIGIN+path}">
<link rel="icon" href="/favicon.ico?v=dd9f0d4a0c"><meta name="theme-color" content="#111111">
<link rel="stylesheet" href="site.css?v=challenges-20260910"><link rel="stylesheet" href="topic-practice.css?v=20260912-1"><link rel="stylesheet" href="textbook-companions.css?v=20260912-1">
<meta property="og:type" content="website"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{ORIGIN+path}">
<script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script></head>
<body class="resource-page topic-page textbook-page"><a class="skip-link" href="#main-content">Skip to main content</a>{HEADER}<main id="main-content">{content}</main>{FOOTER}<script src="site.js" defer></script><script src="textbook-companions.js" defer></script></body></html>''',path)

def tuition():
 return '<aside class="topic-tuition"><div><h2>Specialist tuition and guided practice</h2><p>Individual online lessons, tailored problem sheets and structured practice between lessons, focused on the areas you need to strengthen.</p></div><a class="resource-button" href="contact.html#enquiry-form">Discuss your tuition package</a></aside>'

def resource_links(resources):
 return '<div class="exercise-links">'+''.join(f'<a href="{e(quote(r["url"],safe=":/%?=&+#"))}" class="{"mixed" if r["type"] != "exercise" else "exercise"}" aria-label="{e(r["label"])} worked solutions (PDF)">{e(r["label"])}<span class="sr-only"> worked solutions (PDF)</span></a>' for r in resources)+'</div>'

def related(title):
 s=title.lower()
 if 'normal distribution' in s: return ('#question-1','Normal-distribution practice check','Sketch and shade the required region. Standardise with the standard deviation, then check which tail you need.')
 if s=='statistical distributions': return ('#question-1','Binomial-probability practice check','State the random variable and check that the model fits: fixed trial count, independence and constant success probability.')
 if 'measures of location' in s: return ('#question-2','Coding and spread practice check','Distinguish a change in the centre from a change in the spread. Predict the effect of coding before calculating.')
 if 'data collection' in s: return (None,None,'Identify the population, sampling frame and sampling method. Explain a possible source of bias in the context of the question.')
 if 'representations of data' in s: return (None,None,'Read axes and units before comparing diagrams. For a histogram, use frequency density and remember that area represents frequency.')
 if 'correlation' in s or 'hypothesis' in s: return (None,None,'Define the population parameter and state hypotheses clearly. Give the conclusion in context, keeping correlation separate from causation.')
 if any(x in s for x in ['complex','argand','matrices','linear transformations','polar','hyperbolic','differential equations']): return ('step-past-papers.html','STEP papers and solutions','Extend these methods through unfamiliar Further Maths problems.')
 if any(x in s for x in ['algebra','quadratic','binomial','polynomial']): return ('algebra-and-factorisation.html','Algebra and factorisation','Practise spotting a useful structure before expanding.')
 if any(x in s for x in ['sequence','series']): return ('sequences-and-series.html','Sequences and series','Connect a formula with its terms and check the index range.')
 if any(x in s for x in ['trigon','radian','circle','straight line','vector','parametric']): return ('geometry-and-trigonometry.html','Geometry and trigonometry','Start with a labelled sketch and check every geometric constraint.')
 if any(x in s for x in ['function','graph']): return ('modulus-and-graphs.html','Modulus and graphs','Use a sketch to check the effect of transformations and domain restrictions.')
 if any(x in s for x in ['calculus','differentiat','integration','revolution','numerical']): return ('calculus-and-graph-sketches.html','Calculus and graph sketches','Check signs, turning points and the difference between signed integrals and area.')
 if any(x in s for x in ['probability','distribution']): return ('counting-and-overlap.html','Counting and overlap','Write events carefully and check whether cases overlap.')
 if 'induction' in s: return ('tmua-logic-proof.html','Logic and proof','Keep assumptions and conclusions separate in each step of a proof.')
 if any(x in s for x in ['mechanic','force','motion','acceleration','moment','projectile','kinematic']): return ('esat-paper-archive.html','ESAT and physics practice','Extend modelling skills with clearly labelled historical physics and engineering questions.')
 return (None,None,'Check the meaning of the quantities before choosing a calculation.')

def chapter_html(c,index):
 url,label,note=related(c['title'])
 route=f'<p class="practice-route">Further practice: <a href="{url}">{label}</a>.</p>' if url else ''
 return f'''<details class="chapter" id="chapter-{c['number']}"{' open' if index==0 else ''}><summary>{c['number']}. {e(c['title'])}</summary><div class="chapter-content"><p>{e(note)}</p>{resource_links(c['resources'])}{route}</div></details>'''

def credit(book=None):
 source=book['source_url'] if book else CATALOGUE['source_collection_url']
 return f'''<p class="textbook-credit">Textbooks and linked SolutionBank materials: Pearson Education, accessed through <a href="{source}">Physics &amp; Maths Tutor’s Edexcel SolutionBank</a>. Original practice questions, hints and explanations on this page: Arij Asad. This is an independent companion to the UK Edexcel 2017 series; match the chapter and exercise labels to your book. International A-level and older modular books use different numbering.</p>'''

for b in BOOKS:
 s=slug(b); category,title,description=META[s]; p=PRACTICE[s]
 switcher='<nav class="book-switcher" aria-label="Textbook companions">'+''.join(f'<a href="{filename(x)}"'+(' aria-current="page"' if x is b else '')+f'>{e(META[slug(x)][1])}</a>' for x in BOOKS)+'</nav>'
 menu=''.join(f'<a href="#chapter-{c["number"]}">{c["number"]}. {e(c["title"])}</a>' for c in b['chapters'])
 chapters=''.join(chapter_html(c,i) for i,c in enumerate(b['chapters']))
 supplements=''.join(f'<h3>{e(sec["title"])}: worked solutions</h3>{resource_links(sec["resources"])}' for sec in b['supplementary_sections'])
 questions=''
 for i,q in enumerate(p['questions'],1):
  questions+=f'''<article class="practice-card" id="question-{i}"><div class="practice-head"><h3>{i}. {e(q['topic'])}</h3>{paras(q['prompt'])}</div><div class="practice-body"><details><summary>Show a hint</summary><div>{paras(q['hint'])}</div></details><details><summary>Show the full solution</summary><div>{paras(q['solution'])}<p><strong>Answer:</strong> {m(q['answer'])}</p></div></details></div></article>'''
 mistake=p['mistake']
 questions+=f'''<article class="practice-card" id="find-the-mistake"><div class="practice-head"><h3>Find the mistake</h3>{paras(mistake['prompt'])}</div><div class="practice-body"><details><summary>Show the correction</summary><div>{paras(mistake['solution'])}</div></details></div></article>'''
 recommendations='<ol>'+''.join('<li>'+m(x)+'</li>' for x in p['recommendations'])+'</ol>'
 content=f'''<header class="textbook-hero"><div class="container"><nav class="textbook-breadcrumbs" aria-label="Breadcrumb"><a href="resources.html">Resources</a><span>/</span><a href="edexcel-textbook-companions.html">Edexcel companions</a></nav><p class="topic-kicker">{category} · UK A-level</p><h1>Edexcel {e(title)}</h1><p>{e(description)} Find your chapter, open the matching worked solutions, and try a short practice check.</p><nav class="topic-jumps" aria-label="Page sections"><a href="#chapters">Chapters &amp; solutions</a><a href="#practice">Try the practice check</a><a href="#downloads">Download the sheet</a></nav></div></header>
<div class="container">{switcher}<section class="textbook-section" id="chapters"><h2>Chapters &amp; worked solutions</h2><p>Use your textbook for the questions. Every exercise button below opens the corresponding SolutionBank PDF.</p><div class="chapter-layout"><aside class="chapter-menu"><h3>Jump to a chapter</h3><nav aria-label="Chapters">{menu}<a href="#review-solutions">Review &amp; practice papers</a></nav></aside><div class="chapter-list">{chapters}<section id="review-solutions" class="textbook-section"><h2>Review &amp; practice-paper solutions</h2>{supplements}</section></div></div>{credit(b)}</section>
<section class="textbook-section" id="practice"><p class="topic-kicker">Original practice by Arij Asad</p><h2>A short practice check</h2><p>Try these three questions before opening the hints. They sample a few useful skills; use them to choose what to revisit, rather than as a complete assessment of the book.</p>{questions}<aside class="textbook-note"><h3>Use what you found</h3>{recommendations}</aside></section>
<section class="textbook-section" id="downloads"><h2>Take the practice into a lesson</h2><p>The printable sheet contains the questions first, followed by hints and full worked solutions. The editable LaTeX source is ready for Overleaf.</p><div class="download-row"><a href="assets/textbook-practice/{s}-practice.pdf">Practice sheet &amp; solutions (PDF)</a><a href="assets/textbook-practice/edexcel-practice-overleaf.zip" download>All six sheets for Overleaf (ZIP)</a></div></section>{tuition()}</div>'''
 (ROOT/filename(b)).write_text(page(filename(b),'Edexcel '+title+' Textbook Companion & Solutions',description+' Chapter-by-chapter SolutionBank links and original questions with hints and worked solutions.',content))

cards=''.join(f'''<article class="book-card"><div class="book-card-top"><span>{META[slug(b)][0]}</span><h2><a href="{filename(b)}">{e(META[slug(b)][1])}</a></h2></div><div class="book-card-body"><p>{e(META[slug(b)][2])}</p><a class="resource-button" href="{filename(b)}">Open the companion<span class="sr-only"> for {e(META[slug(b)][1])}</span></a></div></article>''' for b in BOOKS)
content=f'''<header class="textbook-hero"><div class="container"><nav class="textbook-breadcrumbs" aria-label="Breadcrumb"><a href="resources.html">All resources</a></nav><p class="topic-kicker">UK Edexcel · A-level &amp; Further Maths</p><h1>Your textbook.<br>Practice with a purpose.</h1><p>Chapter-by-chapter worked-solution links, original practice checks and guidance for the next step. Choose the book you use in lessons.</p><nav class="topic-jumps" aria-label="Companion shortcuts"><a href="#books">Choose your book</a><a href="#using-the-companions">Plan a practice session</a><a href="maths-topic-practice.html">Topic guides</a></nav></div></header><div class="container"><section id="books" class="textbook-grid" aria-label="Edexcel textbook companions">{cards}</section>
<section class="textbook-section" id="using-the-companions"><h2>Turn a chapter into a practice session</h2><ol><li><strong>Choose one skill.</strong> Use a question you could not finish to identify the chapter you need.</li><li><strong>Work from your textbook.</strong> Attempt a small selection from the relevant exercise before opening its solutions.</li><li><strong>Review the first wrong step.</strong> Explain the correction, then retry the question from a clean page.</li><li><strong>Mix the methods.</strong> Return to the chapter’s mixed exercise once the individual techniques feel secure.</li></ol><div class="textbook-note"><p><strong>For lessons and homework:</strong> each companion has a short original practice check, a find-the-mistake example and a printable sheet with full solutions. Chapter links can be shared directly.</p></div></section>
<section class="textbook-section"><h2>From textbook techniques to unfamiliar problems</h2><p>Use the topic guides to strengthen algebra, graph sketches, calculus and reasoning. When you are ready, return to the admissions archives for longer or less familiar problems, choosing topics that fit your test’s current specification.</p><nav class="topic-jumps" aria-label="Further practice"><a href="maths-topic-practice.html">Worked topic guides</a><a href="tmua-paper-archive.html">TMUA practice</a><a href="step-past-papers.html">STEP practice</a><a href="esat-paper-archive.html">ESAT &amp; physics practice</a></nav></section>{credit()}{tuition()}</div>'''
(ROOT/'edexcel-textbook-companions.html').write_text(page('edexcel-textbook-companions.html','Edexcel Maths Textbook Companions: Exercises & Worked Solutions','Find UK Edexcel A-level and Further Maths chapter solutions, original practice checks, printable sheets and guidance for Pure, Statistics, Mechanics and Core Pure.',content,True))
print(f'Built hub and {len(BOOKS)} textbook companions')
