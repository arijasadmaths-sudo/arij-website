# Arij Asad Maths

Static source for [maths.arijasad.com](https://maths.arijasad.com/), hosted with GitHub Pages.

The website provides specialist online mathematics tuition information and free preparation resources for TMUA, STEP, Cambridge Mathematics interviews, A Level Mathematics and Further Mathematics.

The academic and research website is maintained separately at [www.arijasad.com](https://www.arijasad.com/).

Deployment source: the `main` branch, published from the repository root.

## Paper archives

Ten static archives cover JMC, IMC, SMC, AMC 10, AMC 12, AIME, BMO, TMUA, STEP and ESAT. The Olympiad and TMUA tuition pages link to these larger grids. The existing `tmua-past-papers.html` remains the study guide; the catalogue is `tmua-paper-archive.html`.

Reviewed source data lives in `data/paper-archives/`. After checking new papers and thresholds against their source, edit the relevant JSON and regenerate the HTML with:

```sh
python3 scripts/build-archives.py
```

Commit both the data and generated pages. The live site needs no Python, build step or client-side data loading. `archive.css` extends the shared black, cream and gold styles.

Keep answer keys distinct from worked or extended solutions. Use the exact year, round and sitting; historical formats and score scales can change. Leave missing resources explicit, and identify paid packs and community score estimates. TMUA's public official archive currently ends in 2023; do not label community mocks as official papers.

Do not add buttons to general UKMT website pages or paid paper packs. Keep direct paper/solution resources and plain source citations. Mark years without a free standalone paper explicitly.

External materials link to their original publishers. Four Beyond Horizon and Yotta paper PDFs are stored unchanged under `assets/community-papers/`. Update the catalogue's checked date and sitemap last-modified dates when making substantive changes.

### Creator attribution

Beyond Horizon and Yotta are third-party creators. Credit their mock papers prominently in the collection heading and beside the paper downloads. The covers name “Beyond Horizon” (singular) and “yotta”. Preserve the original paper contents and existing credits; Arij Asad curates this archive. Retain these attribution fields when adding or regenerating resources.

STEP uses S/1/2/3 thresholds by paper and year. STEP 1's historical papers are distinct from the current STEP 2 and 3 exams. Treat an examiner report, mark scheme, worked solution and community contribution according to their actual content; preserve creator and completeness notes.

ESAT separates official samples from historical ENGAA, NSAA and PAT practice. Old paper formats, syllabuses and admission thresholds must not be presented as current ESAT rules. British Physics Olympiad links are further physics practice.

For TMUA, show N/A for unavailable or inapplicable items. Do not publish the Beyond Horizon or Yotta answer keys. Keep their paper credits, and attribute any R2Drew2 video walkthroughs separately to Rob Drew (R2Drew2).
