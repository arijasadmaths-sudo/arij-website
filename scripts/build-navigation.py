#!/usr/bin/env python3
"""Update the shared archive bar in every existing tuition page."""
from pathlib import Path
from site_navigation import install_archive_navigation

ROOT = Path(__file__).resolve().parents[1]

if __name__ == '__main__':
    updated = 0
    for path in sorted(ROOT.glob('*.html')):
        before = path.read_text()
        after = install_archive_navigation(before, path.name)
        if after != before:
            path.write_text(after)
            updated += 1
    print(f'Updated archive navigation in {updated} pages.')
