# Arij Asad Maths

Static source for [maths.arijasad.com](https://maths.arijasad.com/), hosted with GitHub Pages.

The website provides specialist online mathematics tuition information and free preparation resources for TMUA, STEP, Cambridge Mathematics interviews, A Level Mathematics and Further Mathematics.

The academic and research website is maintained separately at [www.arijasad.com](https://www.arijasad.com/).

Deployment source: the `main` branch, published from the repository root.

## Paper archives

Eleven static archives cover JMC, IMC, SMC, AMC 10, AMC 12, AIME, BMO, TMUA, MAT, STEP and ESAT. The Olympiad and TMUA tuition pages link to these larger grids. The existing `tmua-past-papers.html` remains the study guide; the catalogue is `tmua-paper-archive.html`.

Reviewed source data lives in `data/paper-archives/`. After checking new papers and thresholds against their source, edit the relevant JSON and regenerate the HTML with:

```sh
python3 scripts/build-archives.py
python3 scripts/build-topic-guides.py
python3 scripts/build-navigation.py
```

Commit both the data and generated pages. The live site needs no Python, build step or client-side data loading. `archive.css` extends the shared black, cream and gold styles.

`data/topic-guides.json` contains the original examples, hints, solutions and credited resource links for the six topic guides. `scripts/build-topic-guides.py` renders those pages and `maths-topic-practice.html`; their styles live in `topic-practice.css`. Keep student identities and individual feedback out of public source. Topic guidance is general skill practice, not a claim that every linked topic is on every test specification.

MAT is historical from 2026, when Oxford replaced it with TMUA. `data/paper-archives/mat.json` preserves the distinction between main papers, specimens and additional tests. Its three means are Oxford Mathematics-group applicant, shortlisted and offer-holder averages out of 100, not grade boundaries. Keep them labelled as such. Update both `years` and the matching `archiveSections` rows when modifying the catalogue.

`scripts/site_navigation.py` owns the separate past-paper archive bar. `scripts/build-navigation.py` installs it below the main header on every root HTML page; archive generation also includes it automatically. Its scoped styles live in `paper-navigation.css`, including the scrollable row for smaller screens. Keep links root-relative so they also work on the 404 page.

Keep answer keys distinct from worked or extended solutions. Use the exact year, round and sitting; historical formats and score scales can change. Leave missing resources explicit, and identify paid packs and community score estimates. TMUA's public official archive currently ends in 2023; do not label community mocks as official papers.

Do not add buttons to general UKMT website pages or paid paper packs. Keep direct paper/solution resources and plain source citations. Mark years without a free standalone paper explicitly.

External materials link to their original publishers. Four Beyond Horizon and Yotta paper PDFs are stored unchanged under `assets/community-papers/`. Update the catalogue's checked date and sitemap last-modified dates when making substantive changes.

### Creator attribution

Beyond Horizon and Yotta are third-party creators. Credit their mock papers prominently in the collection heading and beside the paper downloads. The covers name “Beyond Horizon” (singular) and “yotta”. Preserve the original paper contents and existing credits; Arij Asad curates this archive. Retain these attribution fields when adding or regenerating resources.

STEP uses S/1/2/3 thresholds by paper and year. STEP 1's historical papers are distinct from the current STEP 2 and 3 exams. Treat an examiner report, mark scheme, worked solution and community contribution according to their actual content; preserve creator and completeness notes.

ESAT separates official samples from historical ENGAA, NSAA and PAT practice. Old paper formats, syllabuses and admission thresholds must not be presented as current ESAT rules. British Physics Olympiad links are further physics practice.

For TMUA, show N/A for unavailable or inapplicable items. Do not publish the Beyond Horizon or Yotta answer keys. Keep their paper credits, and attribute any R2Drew2 video walkthroughs separately to Rob Drew (R2Drew2).

Historical TMUA score cells show the minimum combined raw total out of 40 for overall scores of at least 7, 8 and 9, with 5 and 6 as secondary values. Read the overall conversion column for the exact year; never average the two individual paper scores or interpolate between published raw marks. Keep source-table links neutral and label 2016 as practice papers. Community estimates stay separate from historical official-paper conversions.

Archive filters use the actual exam year on each row and preserve the whole matching row, including credits and boundaries. Undated mocks, specimens and multi-year collections share the “Undated / collections” option. Link-section cards use reviewed `filterTypes` (`papers`, `written`, `answers`, `videos`, `guides`) and optional numeric `filterYear`; never infer an exam year from an upload URL. Combined resources can have multiple types. `archive-filters.js` enhances the static HTML: without JavaScript every original resource remains visible. Run `node --test scripts/archive-filters.test.cjs` after installing `linkedom` in a separate QA directory and setting `NODE_PATH` to its `node_modules` directory.
