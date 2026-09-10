"""Shared, crawlable navigation for the build-free tuition website."""
from html import escape
import re

ARCHIVES = [
    ('tmua-paper-archive.html', 'TMUA'),
    ('step-past-papers.html', 'STEP'),
    ('esat-paper-archive.html', 'ESAT'),
    ('jmc-past-papers.html', 'JMC'),
    ('imc-past-papers.html', 'IMC'),
    ('smc-past-papers.html', 'SMC'),
    ('amc10-past-papers.html', 'AMC 10'),
    ('amc12-past-papers.html', 'AMC 12'),
    ('aime-past-papers.html', 'AIME'),
    ('bmo-past-papers.html', 'BMO'),
]
STYLE = '<link rel="stylesheet" href="/paper-navigation.css?v=20260910-1">'


def archive_navigation(current_path, chinese=False):
    label = '历年试题（英文）' if chinese else 'Past paper archives'
    links = []
    for path, name in ARCHIVES:
        current = ' aria-current="page"' if path == current_path else ''
        language = ' hreflang="en-GB" lang="en"' if chinese else ''
        links.append(f'<a href="/{path}" aria-label="{escape(name)} paper archive"{current}{language}>{escape(name)}</a>')
    return ('  <!-- Shared past-paper navigation -->\n'
            f'  <nav class="paper-archive-bar" aria-label="{label}">\n'
            '    <div class="paper-archive-bar__inner">\n'
            f'      <span class="paper-archive-bar__label">{label}</span>\n'
            '      <div class="paper-archive-bar__links">' + ''.join(links) + '</div>\n'
            '    </div>\n'
            '  </nav>\n'
            '  <!-- /Shared past-paper navigation -->')


def install_archive_navigation(document, current_path):
    document = re.sub(r'\n?  <!-- Shared past-paper navigation -->.*?<!-- /Shared past-paper navigation -->', '', document, flags=re.S)
    header = re.search(r'<header\b[^>]*class="site-header"[^>]*>.*?</header>', document, re.S)
    if header is None:
        return document
    chinese = bool(re.search(r'<html[^>]+lang="zh', document))
    document = document[:header.end()] + '\n' + archive_navigation(current_path, chinese) + document[header.end():]
    document = re.sub(r'\s*<link[^>]+href="/?paper-navigation\.css[^>]*>', '', document)
    return document.replace('</head>', '  ' + STYLE + '\n</head>', 1)
