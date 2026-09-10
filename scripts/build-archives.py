#!/usr/bin/env python3
"""Render the reviewed paper catalogue as crawlable, build-free HTML pages."""
from pathlib import Path
from html import escape
from collections import defaultdict
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'paper-archives'
ORIGIN = 'https://maths.arijasad.com/'
EXAMS = [('jmc', 'JMC'), ('imc', 'IMC'), ('smc', 'SMC'), ('amc10', 'AMC 10'),
         ('amc12', 'AMC 12'), ('aime', 'AIME'), ('bmo', 'BMO')]
LABELS = dict(EXAMS + [('tmua', 'TMUA')])
CHECKED = '2026-09-10'


def e(value):
    return escape(str(value), quote=True)


def page_path(exam):
    return 'tmua-paper-archive.html' if exam == 'tmua' else exam + '-past-papers.html'


def text(value):
    if isinstance(value, dict):
        return '; '.join(str(k) + ': ' + text(v) for k, v in value.items() if v is not None)
    if isinstance(value, list):
        return '; '.join(text(v) for v in value)
    return str(value)


def file_link(item, context):
    kind = item.get('kind', 'solutions')
    modifier = '--paper' if kind == 'paper' else '--extended' if kind == 'extended-solutions' else ''
    label = item['label']
    return (f'<a class="file-button file-button{modifier}" href="{e(item["url"])}" '
            f'aria-label="{e(context + ": " + label)}">{e(label)}</a>')


def boundary_cell(row, exam):
    b = row.get('boundaries') or {}
    parts = []
    labels = [('bronze', 'Bronze'), ('silver', 'Silver'), ('gold', 'Gold'),
              ('merit', 'Merit'), ('distinction', 'Distinction'),
              ('distinguishedHonorRoll', 'Distinguished Honor Roll')]
    qualification = b.get('qualification')
    if qualification is not None and not isinstance(qualification, (dict, list)) and len(str(qualification)) < 18:
        label = 'AIME' if exam in ('amc10', 'amc12') else b.get('qualificationLabel', 'Qualification')
        labels.append(('qualification', label))
    awards = []
    for key, label in labels:
        value = b.get(key)
        if value is not None and not isinstance(value, (dict, list)):
            awards.append(f'<div class="award-value{" award-value--gold" if key == "gold" else ""}"><dt>{e(label)}</dt><dd>{e(value)}</dd></div>')
    if awards:
        parts.append('<dl class="award-values">' + ''.join(awards) + '</dl>')
    if isinstance(qualification, dict):
        qualifications = ''.join('<div>' + e(k) + ': <strong>' + e(text(v)) + '</strong></div>' for k, v in qualification.items() if v is not None)
        if qualifications:
            parts.append('<details class="boundary-note"><summary>Follow-on thresholds</summary>' + qualifications + '</details>')
    elif qualification is not None and len(str(qualification)) >= 18:
        parts.append('<span class="boundary-note">' + e(text(qualification)) + '</span>')
    if b.get('note'):
        parts.append('<span class="boundary-note">' + e(text(b['note'])) + '</span>')
    if b.get('url') or b.get('sourceUrl'):
        url = b.get('url') or b.get('sourceUrl')
        label = b.get('linkLabel', 'Source / full thresholds')
        parts.append(f'<a class="source-note" href="{e(url)}">{e(label)}</a>')
    if b.get('awardSourceUrl'):
        parts.append(f'<a class="source-note" href="{e(b["awardSourceUrl"])}">Distinction and honour-roll source</a>')
    for item in b.get('links', []):
        parts.append(f'<a class="source-note" href="{e(item["url"])}">{e(item["label"])}</a>')
    if not parts:
        message = 'No standalone qualifying score' if exam == 'aime' else 'Not located in the available sources'
        parts.append('<span class="unavailable">' + message + '</span>')
    return ''.join(parts)


def row_html(row, exam):
    year = row['year']
    variant = row.get('variant') or ''
    if row.get('session') and row['session'] not in variant:
        variant += (' · ' if variant else '') + row['session']
    label = row.get('label') or str(year)
    context = row.get('exam', LABELS[exam]) + ' ' + label + (' ' + variant if variant else '')
    paper_context = context + (' by ' + row['creator'] if row.get('creator') else '')
    answer_context = context + (' — ' + row['creator'] + ' collection' if row.get('creator') else '')
    links = row.get('papers', [])
    papers = [x for x in links if x.get('kind') == 'paper']
    answers = [x for x in links if x.get('kind') != 'paper']
    answers.sort(key=lambda x: {'extended-solutions': 0, 'solutions': 1, 'answers': 2}.get(x.get('kind'), 3))
    paper_content = ''.join(file_link(x, paper_context) for x in papers) or '<span class="unavailable">Paper not located</span>'
    answer_content = ''.join(file_link(x, answer_context) for x in answers) or '<span class="unavailable">Solutions not located</span>'
    if row.get('creator'):
        paper_content += '<span class="source-note">Paper by <strong>' + e(row['creator']) + '</strong></span>'
        if answers:
            answer_content += '<span class="source-note">Answer key supplied with the ' + e(row['creator']) + ' collection.</span>'
    if row.get('questionVideos'):
        videos = ''.join(f'<a href="{e(v["url"])}">{e(v["label"])}</a>' for v in row['questionVideos'])
        answer_content += '<details class="question-videos"><summary>Videos by question</summary><div>' + videos + '</div></details>'
    row_note = row.get('note') or row.get('paperNote')
    if row.get('examDate'):
        paper_content += '<span class="source-note">Sat ' + e(row['examDate']) + '</span>'
    if row_note:
        paper_content += '<span class="source-note">' + e(text(row_note)) + '</span>'
    if row.get('formatNote'):
        paper_content += '<span class="source-note">' + e(text(row['formatNote'])) + '</span>'
    score_label = 'Score conversion' if exam == 'tmua' else 'Qualification' if exam in ('amc10', 'amc12', 'aime') else 'Award boundaries'
    return (f'<tr role="row"><th role="rowheader" scope="row">{e(label)}' + (f'<span class="year-variant">{e(variant)}</span>' if variant else '') + '</th>'
            + '<td role="cell" class="paper-cell" data-label="Question papers"><div class="file-links">' + paper_content + '</div></td>'
            + '<td role="cell" class="solutions-cell" data-label="Solutions and answers"><div class="file-links">' + answer_content + '</div></td>'
            + '<td role="cell" class="bounds-cell" data-label="' + score_label + '">' + boundary_cell(row, exam) + '</td></tr>')


def table(rows, exam, caption):
    bounds_label = 'Score conversion' if exam == 'tmua' else 'Qualification' if exam in ('aime', 'amc10', 'amc12') else 'Award boundaries'
    return ('<div class="archive-table-wrap"><table role="table" class="archive-table"><caption>' + e(caption) + '</caption>'
            + '<thead role="rowgroup"><tr role="row"><th role="columnheader" scope="col">Year / paper</th><th role="columnheader" scope="col">Question papers</th><th role="columnheader" scope="col">Solutions &amp; answers</th><th role="columnheader" scope="col">' + bounds_label + '</th></tr></thead><tbody role="rowgroup">'
            + '\n'.join(row_html(r, exam) for r in rows) + '</tbody></table></div>')


def render(data):
    exam = data['exam']
    rows = data['years']
    name = LABELS[exam]
    path = page_path(exam)
    title = data.get('pageTitle') or name + ' Past Papers, Solutions & Boundaries | Arij Asad'
    description = data.get('description') or f'{name} past papers, worked solutions and historical award or qualification boundaries, organised by year. Find extended solutions where available.'
    hub = 'tmua.html' if exam == 'tmua' else 'maths-challenges.html'
    hub_label = 'TMUA tuition' if exam == 'tmua' else 'Maths challenges & Olympiads'
    template = (ROOT / 'maths-challenges.html').read_text()
    header = re.search(r'  <header class="site-header">.*?</header>', template, re.S)[0]
    header = header.replace(' aria-current="page"', '')
    footer = re.search(r'  <footer>.*?</footer>', template, re.S)[0]
    groups = defaultdict(list)
    for row in rows:
        if isinstance(row['year'], int):
            groups[f'{row["year"] // 10 * 10}s'].append(row)
        else:
            groups['Specimen papers'].append(row)
    groups = dict(sorted(groups.items(), key=lambda pair: int(pair[0][:-1]) if pair[0][:-1].isdigit() else 0, reverse=True))
    numeric_years = [r['year'] for r in rows if isinstance(r['year'], int)]
    coverage = f'{min(numeric_years)}–{max(numeric_years)}' if numeric_years else 'Specimen and practice papers'
    paper_count = sum(1 for r in rows if any(x.get('kind') == 'paper' for x in r.get('papers', [])))
    nav_exams = EXAMS if exam != 'tmua' else [('tmua', 'TMUA archive')]
    nav = ''.join(f'<a href="{page_path(k)}"' + (' aria-current="page"' if k == exam else '') + f'>{e(label)}</a>' for k, label in nav_exams)
    if exam == 'tmua':
        nav += '<a href="#community-papers">Community papers</a><a href="tmua-past-papers.html">Past-paper study guide</a>'
    jumps = ''.join(f'<a href="#{e(g.lower().replace(" ", "-"))}">{e(g)}</a>' for g in groups)
    if data.get('legacyYears'):
        jumps += '<a href="#ahsme">AHSME: 1950–1999</a>'
    for collection in data.get('community', []):
        c_id = collection.get('id') or re.sub(r'[^a-z0-9]+', '-', collection['title'].lower()).strip('-')
        jumps += f'<a href="#{e(c_id)}">{e(collection.get("navLabel", collection["title"].replace(" — supplied collection", "")))}</a>'
    for section in data.get('linkSections', []):
        jumps += f'<a href="#{e(section["id"])}">{e(section["title"])}</a>'
    sections = []
    for group, group_rows in groups.items():
        group_rows.sort(key=lambda r: (-(r['year'] if isinstance(r['year'], int) else 0), str(r.get('sortKey', r.get('variant', '')))))
        sections.append(f'<section class="archive-section" id="{e(group.lower().replace(" ", "-"))}"><h2>{e(group)}</h2>'
                        + table(group_rows, exam, name + ' papers and scores — ' + group) + '</section>')
    notes = data.get('displayNotes', [])
    notes_html = '<aside class="archive-note">' + ''.join('<p>' + e(n) + '</p>' for n in notes) + '</aside>' if notes else ''
    communities = []
    if data.get('legacyYears'):
        communities.append('<section class="archive-section" id="ahsme"><h2>Earlier papers: AHSME</h2><p class="community-description">The American High School Mathematics Examination preceded AMC 12. These papers date from 1950–1999 and use historical formats and scoring.</p>' + table(data['legacyYears'], exam, 'AHSME predecessor papers, 1950–1999') + '</section>')
    if data.get('community'):
        communities.append('<h2 class="community-heading" id="community-papers">Community <span>practice papers.</span></h2><p class="community-description">Independent practice material. These are not official TMUA papers; any suggested score conversions are the creator’s estimates.</p>')
        for collection in data['community']:
            c_id = collection.get('id') or re.sub(r'[^a-z0-9]+', '-', collection['title'].lower()).strip('-')
            communities.append(f'<section class="archive-section" id="{e(c_id)}"><h2>{e(collection["title"])}</h2>')
            if collection.get('credit'):
                communities.append('<p class="community-description"><strong>' + e(collection['credit']) + '</strong></p>')
            if collection.get('description'):
                communities.append('<p class="community-description">' + e(collection['description']) + '</p>')
            communities.append(table(collection['rows'], exam, collection['title']) + '</section>')
    if data.get('linkSections'):
        for section in data['linkSections']:
            communities.append('<section class="archive-section" id="' + e(section['id']) + '"><h2>' + e(section['title']) + '</h2><ul class="archive-link-grid">')
            for item in section['links']:
                communities.append('<li><a href="' + e(item['url']) + '">' + e(item['label']) + '</a></li>')
            communities.append('</ul></section>')
    sources = ''.join(f'<li><a href="{e(s["url"])}">{e(s["label"])}</a></li>' for s in data.get('sources', []) + data.get('legacySources', []))
    schema = {'@context':'https://schema.org','@type':'CollectionPage','name':title.split(' | ')[0],
              'url':ORIGIN + path,'description':description,'dateModified':CHECKED,
              'author':{'@type':'Person','@id':ORIGIN+'about.html#arij-asad','name':'Arij Asad'},
              'isPartOf':{'@type':'WebSite','name':'Arij Asad Maths','url':ORIGIN}}
    if data.get('community'):
        schema['editor'] = schema.pop('author')
    source_note = data.get('sourceNote', 'Resources open on their original websites unless labelled as a supplied collection. Papers and solutions remain the work of their respective authors. Missing papers or thresholds are marked explicitly.')
    intro = data.get('intro') or 'Question papers, solutions and historical thresholds, together in one place. Choose the year and paper you are practising.'
    return f'''<!DOCTYPE html>
<html lang="en-GB">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e(title)}</title>
  <meta name="description" content="{e(description)}">
  <link rel="canonical" href="{ORIGIN + path}">
  <link rel="icon" href="/favicon.ico?v=dd9f0d4a0c" sizes="16x16 32x32 48x48 64x64">
  <link rel="stylesheet" href="site.css?v=challenges-20260910">
  <link rel="stylesheet" href="archive.css?v=20260910">
  <meta name="theme-color" content="#111111">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:url" content="{ORIGIN + path}">
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
</head>
<body class="resource-page archive-page">
  <a class="skip-link" href="#main-content">Skip to main content</a>
{header}
  <main id="main-content">
    <header class="archive-intro"><div class="container">
      <nav class="archive-breadcrumbs" aria-label="Breadcrumb"><a href="{hub}">{e(hub_label)}</a><span aria-hidden="true">/</span><span>{e(name)} archive</span></nav>
      <h1>{e(name)} papers &amp; <span>solutions.</span></h1>
      <p>{e(intro)}</p>
      <div class="archive-facts"><span>{coverage}</span><span>{paper_count} paper entries</span><span>Checked 10 September 2026</span></div>
    </div></header>
    <div class="container">
      <nav class="archive-nav" aria-label="Paper archives">{nav}</nav>
      {notes_html}
      <nav class="archive-jumps" aria-label="Jump to archive sections"><strong>Jump to:</strong>{jumps}</nav>
      {''.join(sections)}
      {''.join(communities)}
      <aside class="archive-sources"><h2>Sources &amp; archive notes</h2><ul>{sources}</ul>
      <p class="source-note">{e(source_note)}</p></aside>
      <div class="archive-bottom"><p><a href="{hub}">Back to {e(hub_label.lower())}</a></p><a class="resource-button" href="contact.html?service={'TMUA%20preparation' if exam == 'tmua' else 'Maths%20challenges%20and%20Olympiads'}#enquiry-form">Enquire about {e(name)} tuition</a></div>
    </div>
  </main>
{footer}
  <script src="site.js" defer></script>
</body>
</html>
'''


if __name__ == '__main__':
    for source in sorted(DATA.glob('*.json')):
        data = json.loads(source.read_text())
        if not data.get('years'):
            continue
        path = ROOT / page_path(data['exam'])
        path.write_text(render(data))
        print(path.name, len(data['years']), 'rows')
