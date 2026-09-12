#!/usr/bin/env python3
"""Render the reviewed paper catalogue as crawlable, build-free HTML pages."""
from pathlib import Path
from html import escape
from collections import defaultdict
import json
import re
from site_navigation import install_archive_navigation

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'paper-archives'
ORIGIN = 'https://maths.arijasad.com/'
EXAMS = [('jmc', 'JMC'), ('imc', 'IMC'), ('smc', 'SMC'), ('amc10', 'AMC 10'),
         ('amc12', 'AMC 12'), ('aime', 'AIME'), ('bmo', 'BMO')]
ADMISSIONS = [('tmua', 'TMUA'), ('mat', 'MAT'), ('step', 'STEP'), ('esat', 'ESAT')]
LABELS = dict(EXAMS + ADMISSIONS)
CHECKED = '2026-09-10'


def e(value):
    return escape(str(value), quote=True)


def page_path(exam):
    return exam + '-paper-archive.html' if exam in ('tmua', 'esat') else exam + '-past-papers.html'


def score_heading(exam, overall_raw=False):
    if exam == 'mat':
        return 'Historical averages /100'
    if exam == 'tmua':
        return 'Raw total /40' if overall_raw else 'Score guidance'
    if exam == 'step':
        return 'Grade boundaries'
    if exam == 'esat':
        return 'Score guidance'
    return 'Qualification' if exam in ('aime', 'amc10', 'amc12') else 'Award boundaries'


def text(value):
    if isinstance(value, dict):
        return '; '.join(str(k) + ': ' + text(v) for k, v in value.items() if v is not None)
    if isinstance(value, list):
        return '; '.join(text(v) for v in value)
    return str(value)


def resource_types(item):
    """Use reviewed types where supplied; older paper rows retain their kinds."""
    if 'filterTypes' in item:
        return set(item['filterTypes'])
    kind = item.get('kind')
    label = item.get('label', '').lower()
    if kind == 'video' or re.search(r'video|youtu\.be|youtube\.com|vimeo\.com', label + ' ' + item.get('url', '')):
        return {'videos'}
    result = {'paper': {'papers'}, 'extended-solutions': {'written'},
              'solutions': {'written'}, 'answers': {'answers'}}.get(kind, {'guides'})
    if kind == 'paper' and ('answers' in label or 'answer review' in label):
        result.add('answers')
    return result


def filter_attributes(year, types):
    year = str(year) if isinstance(year, int) else 'undated'
    return f'data-archive-entry data-year="{e(year)}" data-types="{e(" ".join(sorted(types)))}"'


def filter_controls():
    return '''<form class="archive-filters" id="archive-filters" aria-label="Filter archive resources" aria-describedby="archive-filter-help" hidden>
      <div class="archive-filter-fields">
        <label for="archive-year">Year<select id="archive-year" name="year"><option value="all" selected>All years</option></select></label>
        <label for="archive-type">Entries with<select id="archive-type" name="type"><option value="all" selected>All resource types</option></select></label>
        <button class="archive-filter-reset" type="button" data-clear-filters>Clear filters</button>
      </div>
      <p id="archive-filter-help">Choose a year and resource type. Matching entries keep their papers, solutions, credits and score information together.</p>
      <p class="archive-filter-count" id="archive-filter-count" role="status" aria-live="polite" aria-atomic="true"></p>
    </form>
    <p class="archive-filter-empty" id="archive-filter-empty" hidden>No entries match these filters. Try another year or clear the filters.</p>'''


def file_link(item, context):
    kind = item.get('kind', 'solutions')
    modifier = '--paper' if kind == 'paper' else '--extended' if kind == 'extended-solutions' else ''
    label = item['label']
    link = (f'<a class="file-button file-button{modifier}" href="{e(item["url"])}" '
            f'aria-label="{e(context + ": " + label)}">{e(label)}</a>')
    if item.get('credit') or item.get('note'):
        detail = ' '.join(str(item[k]) for k in ('credit', 'note') if item.get(k))
        return '<span class="resource-item">' + link + '<span class="source-note">' + e(detail) + '</span></span>'
    return link


def boundary_cell(row, exam):
    b = row.get('boundaries') or {}
    parts = []
    if exam == 'mat':
        means = b.get('means', {})
        for key, label in [('all', 'All applicants'), ('shortlisted', 'Shortlisted'), ('offers', 'Offer holders')]:
            if key in means:
                parts.append(f'<div class="boundary-note">{label}: <strong>{float(means[key]):.1f}</strong></div>')
        if b.get('note'):
            parts.append('<span class="source-note">' + e(b['note']) + '</span>')
        if b.get('sourceUrl'):
            parts.append(f'<a class="source-note" href="{e(b["sourceUrl"])}">Oxford score statistics</a>')
        return ''.join(parts) or '<span class="unavailable">N/A</span>'
    if exam == 'tmua' and b.get('overallRawThresholds'):
        thresholds = b['overallRawThresholds']
        badges = []
        for score in ('7', '8', '9'):
            if score in thresholds:
                label = score if score == '9' else score + '+'
                modifier = ' award-value--gold' if score == '9' else ''
                badges.append(f'<div class="award-value{modifier}"><dt>{label}</dt><dd>{e(thresholds[score])}</dd></div>')
        parts.append('<dl class="award-values">' + ''.join(badges) + '</dl>')
        extra = [f'{score}+: <strong>{e(thresholds[score])}</strong>' for score in ('5', '6') if score in thresholds]
        if extra:
            parts.append('<span class="source-note">' + ' · '.join(extra) + '</span>')
        if b.get('sourceUrl'):
            parts.append(f'<a class="source-note" href="{e(b["sourceUrl"])}">Full conversion table</a>')
        return ''.join(parts)
    labels = [('bronze', 'Bronze'), ('silver', 'Silver'), ('gold', 'Gold'),
              ('merit', 'Merit'), ('distinction', 'Distinction'),
              ('distinguishedHonorRoll', 'Distinguished Honor Roll')]
    if exam == 'step':
        labels = [('gradeS', 'S'), ('grade1', '1'), ('grade2', '2'), ('grade3', '3')]
    qualification = b.get('qualification')
    if qualification is not None and not isinstance(qualification, (dict, list)) and len(str(qualification)) < 18:
        label = 'AIME' if exam in ('amc10', 'amc12') else b.get('qualificationLabel', 'Qualification')
        labels.append(('qualification', label))
    awards = []
    for key, label in labels:
        value = b.get(key)
        if value is not None and not isinstance(value, (dict, list)):
            awards.append(f'<div class="award-value{" award-value--gold" if key in ("gold", "gradeS") else ""}"><dt>{e(label)}</dt><dd>{e(value)}</dd></div>')
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
        message = 'N/A' if exam in ('tmua', 'step', 'esat') else 'No standalone qualifying score' if exam == 'aime' else 'Not located in the available sources'
        parts.append('<span class="unavailable">' + message + '</span>')
    return ''.join(parts)


def row_html(row, exam, overall_raw=False):
    year = row['year']
    variant = row.get('variant') or ''
    if row.get('session') and row['session'] not in variant:
        variant += (' · ' if variant else '') + row['session']
    label = row.get('label') or str(year)
    context = row.get('exam', LABELS[exam]) + ' ' + label + (' ' + variant if variant else '')
    paper_context = context + (' by ' + row['creator'] if row.get('creator') else '')
    answer_context = context + (' — ' + row['creator'] + ' collection' if row.get('creator') else '')
    links = row.get('papers', [])
    types = set().union(*(resource_types(item) for item in links))
    if row.get('questionVideos'):
        types.add('videos')
    papers = [x for x in links if x.get('kind') == 'paper']
    answers = [x for x in links if x.get('kind') != 'paper']
    answers.sort(key=lambda x: {'extended-solutions': 0, 'solutions': 1, 'answers': 2}.get(x.get('kind'), 3))
    missing_paper = 'N/A' if exam == 'tmua' else row.get('paperUnavailable', 'Paper not located')
    missing_solutions = 'N/A' if exam == 'tmua' else row.get('solutionsUnavailable', 'Solutions not located')
    paper_content = ''.join(file_link(x, paper_context) for x in papers) or '<span class="unavailable">' + e(missing_paper) + '</span>'
    answer_content = ''.join(file_link(x, answer_context) for x in answers) or '<span class="unavailable">' + e(missing_solutions) + '</span>'
    if row.get('creator'):
        paper_content += '<span class="source-note">Paper by <strong>' + e(row['creator']) + '</strong></span>'
        if any(item.get('kind') == 'answers' for item in answers):
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
    if row.get('solutionNote'):
        answer_content += '<span class="source-note">' + e(row['solutionNote']) + '</span>'
    score_label = score_heading(exam, overall_raw)
    return (f'<tr role="row" {filter_attributes(year, types)}><th role="rowheader" scope="row">{e(label)}' + (f'<span class="year-variant">{e(variant)}</span>' if variant else '') + '</th>'
            + '<td role="cell" class="paper-cell" data-label="Question papers"><div class="file-links">' + paper_content + '</div></td>'
            + '<td role="cell" class="solutions-cell" data-label="Solutions and answers"><div class="file-links">' + answer_content + '</div></td>'
            + '<td role="cell" class="bounds-cell" data-label="' + score_label + '">' + boundary_cell(row, exam) + '</td></tr>')


def table(rows, exam, caption):
    overall_raw = exam == 'tmua' and any((r.get('boundaries') or {}).get('overallRawThresholds') for r in rows)
    bounds_label = score_heading(exam, overall_raw)
    return ('<div class="archive-table-wrap"><table role="table" class="archive-table"><caption>' + e(caption) + '</caption>'
            + '<thead role="rowgroup"><tr role="row"><th role="columnheader" scope="col">Year / paper</th><th role="columnheader" scope="col">Question papers</th><th role="columnheader" scope="col">Solutions &amp; answers</th><th role="columnheader" scope="col">' + bounds_label + '</th></tr></thead><tbody role="rowgroup">'
            + '\n'.join(row_html(r, exam, overall_raw) for r in rows) + '</tbody></table></div>')


def practice_guidance(exam):
    if exam == 'mat':
        return '''<section class="archive-guidance archive-section" id="practice-guidance"><h2>Using historical MAT questions</h2><p>For shorter practice, use the multiple-choice part of a paper or one of the additional tests below. For interview preparation, take a longer question and explain why each step works. Follow the instructions on the original paper: formats and the questions required for different courses changed over time.</p><p>Start untimed, record the point where you became stuck, then redo the question without the solution. Use the <a href="maths-topic-practice.html">maths topic-practice guides</a> to strengthen the underlying skill before another attempt. These papers provide extra practice; use <a href="tmua-paper-archive.html">TMUA papers and current official guidance</a> for TMUA-specific preparation.</p></section>'''
    if exam == 'step':
        return '''<aside class="archive-note"><p>Working through a STEP paper? Read <a href="strong-step-solution.html">how to write a strong STEP solution</a> for advice on complete arguments and clear working, or <a href="when-to-start-step.html">plan when to start STEP preparation</a>.</p></aside>'''
    if exam != 'tmua':
        return ''
    return '''<section class="archive-guidance archive-section" id="practice-guidance" aria-labelledby="practice-guidance-title">
      <h2 id="practice-guidance-title">How I recommend using these TMUA past papers</h2>
      <p class="community-description">A paper is most useful when it changes what you practise next. Look for gaps in knowledge, inefficient methods, misread questions and problems with timing. Preparation advice by <a href="about.html">Arij Asad</a>.</p>
      <ol class="archive-guidance-grid">
        <li><h3>1. Start with a diagnosis</h3><p>Attempt an earlier official paper before working through lots of mocks. Mark questions you guessed or solved slowly as well as those you got wrong. Keep some complete paper pairs unseen for later timed practice. Use the <a href="tmua-study-plan.html">TMUA study plan</a> to turn your first attempt into a preparation schedule.</p></li>
        <li><h3>2. Repair the recurring weakness</h3><p>If logic is causing difficulty, write the direction of each implication explicitly. A counterexample must satisfy the premise while breaking the conclusion: for “if x² = 9, then x = 3”, x = −3 works. Use my <a href="tmua-logic-proof.html">logic and proof guide</a>, then practise with the <a href="#jz-maths-logic-worksheets">JZ Maths logic worksheets</a>.</p></li>
        <li><h3>3. Find the decision that cost you marks</h3><p>Before opening a worked solution or video, note where your approach stopped working. Would a sketch, a special case or eliminating an option have helped? Close the solution and redo the question after a few days. Review correct answers reached through guesswork too. My <a href="tmua-past-papers.html">past-paper study guide</a> explains how to keep a useful error log.</p></li>
        <li><h3>4. Practise timing and working on screen</h3><p>Use complete official papers for timed practice, then use the <a href="https://www.pearsonvue.com/us/en/uatuk.html">official computer-based practice tests</a> to get used to reading on screen and navigating the test. <a href="#community-papers">Community mocks</a> provide more unfamiliar questions; use them to identify weaknesses and treat suggested score conversions as estimates.</p></li>
      </ol>
      <p>For focused work between papers, try my <a href="maths-topic-practice.html">maths topic-practice guides</a>: modulus, factorisation, sequences, calculus, geometry and counting, with worked examples and questions to try independently. The <a href="mat-past-papers.html#additional-tests">historical MAT additional tests</a> provide more multiple-choice practice.</p>
      <p class="source-note">For the current specification and test instructions, see <a href="https://esat-tmua.ac.uk/prepare/">UAT-UK’s official preparation guidance</a>.</p>
    </section>'''


def render(data):
    exam = data['exam']
    rows = data['years']
    name = LABELS[exam]
    path = page_path(exam)
    title = data.get('pageTitle') or name + ' Past Papers, Solutions & Boundaries | Arij Asad'
    description = data.get('description') or f'{name} past papers, worked solutions and historical award or qualification boundaries, organised by year. Find extended solutions where available.'
    hub = data.get('hub') or ('tmua.html' if exam == 'tmua' else 'step.html' if exam == 'step' else 'resources.html' if exam == 'esat' else 'maths-challenges.html')
    hub_label = data.get('hubLabel') or ('TMUA tuition' if exam == 'tmua' else 'STEP tuition' if exam == 'step' else 'Free preparation resources' if exam == 'esat' else 'Maths challenges & Olympiads')
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
    nav = ''
    if exam == 'tmua':
        nav = '<nav class="archive-nav" aria-label="TMUA archive shortcuts"><a href="#2020s">Official past papers</a><a href="#community-papers">Community papers</a><a href="#practice-guidance">How to practise</a><a href="tmua-past-papers.html">Past-paper study guide</a></nav>'
    archive_sections = data.get('archiveSections') or [{'id':g.lower().replace(' ', '-'), 'title':g, 'rows':r} for g,r in groups.items()]
    jumps = ''.join(f'<a href="#{e(g["id"])}">{e(g.get("navLabel", g["title"]))}</a>' for g in archive_sections)
    if data.get('legacyYears'):
        jumps += '<a href="#ahsme">AHSME: 1950–1999</a>'
    for collection in data.get('community', []):
        c_id = collection.get('id') or re.sub(r'[^a-z0-9]+', '-', collection['title'].lower()).strip('-')
        jumps += f'<a href="#{e(c_id)}">{e(collection.get("navLabel", collection["title"].replace(" — supplied collection", "")))}</a>'
    for section in data.get('linkSections', []):
        jumps += f'<a href="#{e(section["id"])}">{e(section["title"])}</a>'
    sections = []
    for group in archive_sections:
        group_rows = group['rows']
        if not group.get('preserveOrder'):
            group_rows.sort(key=lambda r: (-(r['year'] if isinstance(r['year'], int) else 0), str(r.get('sortKey', r.get('variant', '')))))
        group_intro = '<p class="community-description">' + e(group['description']) + '</p>' if group.get('description') else ''
        sections.append(f'<section class="archive-section" data-archive-group id="{e(group["id"])}"><h2>{e(group["title"])}</h2>' + group_intro
                        + table(group_rows, exam, name + ' papers and scores — ' + group['title']) + '</section>')
    notes = data.get('displayNotes', [])
    notes_html = '<aside class="archive-note">' + ''.join('<p>' + e(n) + '</p>' for n in notes) + '</aside>' if notes else ''
    communities = []
    if data.get('legacyYears'):
        communities.append('<section class="archive-section" data-archive-group id="ahsme"><h2>Earlier papers: AHSME</h2><p class="community-description">The American High School Mathematics Examination preceded AMC 12. These papers date from 1950–1999 and use historical formats and scoring.</p>' + table(data['legacyYears'], exam, 'AHSME predecessor papers, 1950–1999') + '</section>')
    if data.get('community'):
        communities.append('<h2 class="community-heading" data-community-heading id="community-papers">Community <span>practice papers.</span></h2><p class="community-description" data-community-heading>Independent practice material. These are not official TMUA papers; any suggested score conversions are the creator’s estimates.</p>')
        for collection in data['community']:
            c_id = collection.get('id') or re.sub(r'[^a-z0-9]+', '-', collection['title'].lower()).strip('-')
            communities.append(f'<section class="archive-section" data-archive-group data-community-group id="{e(c_id)}"><h2>{e(collection["title"])}</h2>')
            if collection.get('credit'):
                communities.append('<p class="community-description"><strong>' + e(collection['credit']) + '</strong></p>')
            if collection.get('description'):
                communities.append('<p class="community-description">' + e(collection['description']) + '</p>')
            communities.append(table(collection['rows'], exam, collection['title']) + '</section>')
    if data.get('linkSections'):
        for section in data['linkSections']:
            communities.append('<section class="archive-section" data-archive-group id="' + e(section['id']) + '"><h2>' + e(section['title']) + '</h2>')
            if section.get('description'):
                communities.append('<p class="community-description">' + e(section['description']) + '</p>')
            if section.get('credit'):
                communities.append('<p class="source-note">' + e(section['credit']) + '</p>')
            communities.append('<ul class="archive-link-grid">')
            for item in section['links']:
                detail = '<span class="source-note">' + e(item['description']) + '</span>' if item.get('description') else ''
                attrs = filter_attributes(item.get('filterYear'), resource_types(item))
                communities.append('<li ' + attrs + '><a href="' + e(item['url']) + '">' + e(item['label']) + '</a>' + detail + '</li>')
            communities.append('</ul></section>')
    sources = ''.join(f'<li><a href="{e(s["url"])}">{e(s["label"])}</a></li>' for s in data.get('sources', []) + data.get('legacySources', []))
    schema = {'@context':'https://schema.org','@type':'CollectionPage','name':title.split(' | ')[0],
              'url':ORIGIN + path,'description':description,'dateModified':data.get('dateModified', CHECKED),
              'author':{'@type':'Person','@id':ORIGIN+'about.html#arij-asad','name':'Arij Asad'},
              'isPartOf':{'@type':'WebSite','name':'Arij Asad Maths','url':ORIGIN}}
    if data.get('community') or exam in ('step', 'esat', 'mat'):
        schema['editor'] = schema.pop('author')
    source_note = data.get('sourceNote', 'Resources open on their original websites unless labelled as a supplied collection. Papers and solutions remain the work of their respective authors. Missing papers or thresholds are marked explicitly.')
    intro = data.get('intro') or 'Question papers, solutions and historical thresholds, together in one place. Choose the year and paper you are practising.'
    service = {'tmua':'TMUA%20preparation', 'mat':'TMUA%20preparation', 'step':'STEP%20preparation', 'esat':'ESAT%20mathematics%20preparation'}.get(exam, 'Maths%20challenges%20and%20Olympiads')
    enquiry_label = 'admissions preparation' if exam == 'mat' else 'ESAT maths' if exam == 'esat' else name
    css_version = '20260910-filters1'
    paper_heading = 'practice papers' if exam == 'esat' else 'past papers'
    curator = '<p class="archive-curator">Curated by <a href="about.html">Arij Asad</a>. Papers, worked solutions and videos are credited to their original creators.</p>' if exam == 'tmua' else ''
    return install_archive_navigation(f'''<!DOCTYPE html>
<html lang="en-GB">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e(title)}</title>
  <meta name="description" content="{e(description)}">
  <link rel="canonical" href="{ORIGIN + path}">
  <link rel="icon" href="/favicon.ico?v=dd9f0d4a0c" sizes="16x16 32x32 48x48 64x64">
  <link rel="stylesheet" href="site.css?v=challenges-20260910">
  <link rel="stylesheet" href="archive.css?v={css_version}">
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
      <h1>{e(name)} {paper_heading} &amp; <span>solutions.</span></h1>
      <p>{e(intro)}</p>
{curator}
    </div></header>
    <div class="container">
{nav}
      {notes_html}
      <aside class="archive-tuition" aria-label="{e(enquiry_label)} tuition packages">
        <div><h2>Individual {e(enquiry_label)} tuition packages</h2><p>One-to-one online lessons, tailored problem sheets and structured practice between lessons, planned around your goals and the areas you need to strengthen.</p></div>
        <a class="resource-button" href="contact.html?service={service}#enquiry-form">Discuss your tuition package</a>
      </aside>
      {filter_controls()}
      <nav class="archive-jumps" aria-label="Jump to archive sections"><strong>Jump to:</strong>{jumps}</nav>
      {''.join(sections)}
{practice_guidance(exam)}
      {''.join(communities)}
      <aside class="archive-sources"><h2>Sources &amp; archive notes</h2><ul>{sources}</ul>
      <p class="source-note">{e(source_note)}</p></aside>
      <div class="archive-bottom"><p><a href="{hub}">Back to {e(hub_label.lower())}</a></p><a class="resource-button" href="contact.html?service={service}#enquiry-form">Enquire about {e(enquiry_label)} tuition</a></div>
    </div>
  </main>
{footer}
  <script src="site.js" defer></script>
  <script src="archive-filters.js?v=20260910-1" defer></script>
</body>
</html>
''', path)


if __name__ == '__main__':
    for source in sorted(DATA.glob('*.json')):
        data = json.loads(source.read_text())
        if not data.get('years'):
            continue
        path = ROOT / page_path(data['exam'])
        path.write_text(render(data))
        print(path.name, len(data['years']), 'rows')
