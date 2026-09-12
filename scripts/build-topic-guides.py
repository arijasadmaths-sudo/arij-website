#!/usr/bin/env python3
"""Build original teaching guides and their hub as readable static HTML."""
from pathlib import Path
from html import escape as e
import json
import re
from site_navigation import install_archive_navigation

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://maths.arijasad.com/'
DATA = json.loads((ROOT / 'data/topic-guides.json').read_text())
TEMPLATE = (ROOT / 'tmua-logic-proof.html').read_text()
HEADER = re.search(r'  <header class="site-header">.*?</header>', TEMPLATE, re.S)[0].replace(' aria-current="page"', '')
FOOTER = re.search(r'  <footer>.*?</footer>', TEMPLATE, re.S)[0]


def page(path, title, description, content, hub=False):
    schema = {'@context': 'https://schema.org', '@type': 'CollectionPage' if hub else 'Article',
              'name': title, 'description': description, 'url': ORIGIN + path,
              'datePublished': '2026-09-12', 'dateModified': '2026-09-12',
              'author': {'@type': 'Person', 'name': 'Arij Asad', 'url': ORIGIN+'about.html'}}
    return install_archive_navigation(f'''<!DOCTYPE html>
<html lang="en-GB"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)} | Arij Asad</title><meta name="description" content="{e(description)}">
<link rel="canonical" href="{ORIGIN+path}"><link rel="icon" href="/favicon.ico?v=dd9f0d4a0c">
<link rel="stylesheet" href="site.css?v=challenges-20260910"><link rel="stylesheet" href="topic-practice.css?v=20260912-1">
<meta name="theme-color" content="#111111"><meta property="og:type" content="{'website' if hub else 'article'}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{ORIGIN+path}">
<script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script>
</head><body class="resource-page topic-page">
<a class="skip-link" href="#main-content">Skip to main content</a>
{HEADER}<main id="main-content">{content}</main>{FOOTER}
<script src="site.js" defer></script></body></html>''', path)


def tuition():
    return '''<aside class="topic-tuition"><div><h2>Specialist tuition and guided practice</h2><p>Individual online lessons, tailored problem sheets and structured practice between lessons, focused on the areas you need to strengthen.</p></div><a class="resource-button" href="contact.html#enquiry-form">Discuss your tuition package</a></aside>'''


def links(items):
    return '<ul class="topic-resources">'+''.join(f'<li><a href="{e(x["url"])}">{e(x["label"])}</a><p>{e(x["note"])}</p></li>' for x in items)+'</ul>'


for t in DATA:
    path=t['slug']+'.html'
    actions='<nav class="topic-jumps" aria-label="Guide sections"><a href="#approach">The approach</a><a href="#worked-example">Worked example</a><a href="#try-it">Try a question</a><a href="#next-practice">Further practice</a></nav>'
    mistakes=''.join('<li>'+x+'</li>' for x in t['mistakes'])
    steps=''.join('<li>'+x+'</li>' for x in t['steps'])
    content=f'''<header class="topic-hero"><div class="container"><nav class="topic-breadcrumbs" aria-label="Breadcrumb"><a href="resources.html">Resources</a><span>/</span><a href="maths-topic-practice.html">Maths topic practice</a></nav><p class="topic-kicker">{e(t['label'])}</p><h1>{e(t['title'])}</h1><p class="topic-lede">{e(t['intro'])}</p><p class="topic-byline">Teaching guide by <a href="about.html">Arij Asad</a></p>{actions}</div></header>
<div class="container topic-layout"><article class="topic-article">
<section id="approach"><h2>{e(t['approachTitle'])}</h2>{t['approach']}<ol class="topic-steps">{steps}</ol></section>
<aside class="topic-note"><h2>Watch for these mistakes</h2><ul>{mistakes}</ul></aside>
<section id="worked-example"><p class="topic-kicker">Worked example</p><h2>{e(t['exampleTitle'])}</h2><div class="topic-question">{t['exampleQuestion']}</div><div class="topic-solution">{t['exampleSolution']}</div></section>
<section id="try-it"><p class="topic-kicker">Your turn</p><h2>{e(t['practiceTitle'])}</h2><div class="topic-question">{t['practiceQuestion']}</div><details class="topic-reveal"><summary>Show a hint</summary><div>{t['hint']}</div></details><details class="topic-reveal"><summary>Show the full solution</summary><div>{t['solution']}</div></details><p class="topic-review">{e(t['review'])}</p></section>
<section id="next-practice"><h2>What to practise next</h2><p>{e(t['sequence'])}</p>{links(t['resources'])}<p class="topic-credit">The examples and explanations on this page are part of Arij Asad’s teaching guides. Linked papers and worksheets belong to their named creators and publishers. PMT’s topic collections include exam-board questions and other credited materials.</p></section>
</article><aside class="topic-sidebar"><h2>Choose another topic</h2><nav aria-label="Other topic guides">{''.join(f'<a href="{e(x["slug"])}.html"'+(' aria-current="page"' if x is t else '')+f'>{e(x["title"])}</a>' for x in DATA)}<a href="tmua-logic-proof.html">Logic and proof</a></nav><p>These guides develop mathematical skills. For the scope of a particular test, use its current official specification.</p><a href="https://esat-tmua.ac.uk/prepare/">Current TMUA and ESAT guidance</a></aside></div>
<div class="container">{tuition()}</div>'''
    (ROOT/path).write_text(page(path,t['title'],t['description'],content))

cards=''.join(f'''<article class="topic-card"><p class="topic-kicker">{e(t['label'])}</p><h2><a href="{e(t['slug'])}.html">{e(t['title'])}</a></h2><p>{e(t['intro'])}</p><a class="topic-card-link" href="{e(t['slug'])}.html">Open the guide<span class="sr-only">: {e(t['title'])}</span></a></article>''' for t in DATA)
content=f'''<header class="topic-hero"><div class="container"><nav class="topic-breadcrumbs" aria-label="Breadcrumb"><a href="resources.html">All resources</a></nav><p class="topic-kicker">Build the skill behind the answer</p><h1>Maths practice by topic.</h1><p class="topic-lede">Work on the step that keeps costing marks: a sign, an unfamiliar identity, a missing case or a diagram that never became an equation.</p><p class="topic-byline">Guidance by <a href="about.html">Arij Asad</a>, drawing on the difficulties addressed in individual lessons.</p><nav class="topic-jumps" aria-label="Topic practice shortcuts"><a href="#topics">Choose a topic</a><a href="mat-past-papers.html">MAT past papers</a><a href="tmua-paper-archive.html">TMUA past papers</a></nav></div></header>
<div class="container"><section class="topic-start"><h2>Start with a question you could not finish</h2><p>Identify the mathematical decision you missed. Work through the relevant example below, try the practice question before revealing its solution, then return to the original paper. A correct answer you guessed deserves a review too.</p></section><section id="topics" class="topic-grid" aria-label="Maths topic guides">{cards}<article class="topic-card"><p class="topic-kicker">Reasoning</p><h2><a href="tmua-logic-proof.html">Logic and proof</a></h2><p>Separate an implication from its converse, test counterexamples and distinguish necessary from sufficient conditions.</p><a class="topic-card-link" href="tmua-logic-proof.html">Open the logic guide</a></article></section>
<section class="topic-return"><h2>Put the skill back into a paper</h2><p>Use these guides for focused practice, then return to unfamiliar problems. Historical MAT questions are supplementary practice; the MAT is no longer held from 2026. Use current official specifications when preparing for TMUA, ESAT or STEP.</p><div class="topic-jumps"><a href="mat-past-papers.html">Historical MAT papers</a><a href="tmua-paper-archive.html">TMUA papers and mocks</a><a href="step-past-papers.html">STEP papers and solutions</a><a href="esat-paper-archive.html">ESAT practice</a></div></section>{tuition()}</div>'''
(ROOT/'maths-topic-practice.html').write_text(page('maths-topic-practice.html','Maths Topic Practice: Worked Examples, Hints & Solutions','Strengthen modulus, algebra, sequences, calculus, geometry, counting and logic with Arij Asad’s worked examples, practice questions and credited resources.',content,True))
print(f'Built {len(DATA)} topic guides and maths-topic-practice.html')
