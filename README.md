# Arij Asad Maths

Static source for [maths.arijasad.com](https://maths.arijasad.com/), hosted with GitHub Pages.

The website provides specialist online mathematics tuition information and free preparation resources for TMUA, STEP, Cambridge Mathematics interviews, A Level Mathematics and Further Mathematics.

The academic and research website is maintained separately at [www.arijasad.com](https://www.arijasad.com/).

Deployment source: the `main` branch, published from the repository root.

## Paper archives

Eight static archives cover JMC, IMC, SMC, AMC 10, AMC 12, AIME, BMO and TMUA. The Olympiad and TMUA tuition pages link to these larger grids. The existing `tmua-past-papers.html` remains the study guide; the catalogue is `tmua-paper-archive.html`.

Reviewed source data lives in `data/paper-archives/`. After checking new papers and thresholds against their source, edit the relevant JSON and regenerate the HTML with:

```sh
python3 scripts/build-archives.py
```

Commit both the data and generated pages. The live site needs no Python, build step or client-side data loading. `archive.css` extends the shared black, cream and gold styles.

Keep answer keys distinct from worked or extended solutions. Use the exact year, round and sitting; historical formats and score scales can change. Leave missing resources explicit, and identify paid packs and community score estimates. TMUA's public official archive currently ends in 2023; do not label community mocks as official papers.

External materials link to their original publishers. Six supplied Beyond Horizon and Yotta files are stored unchanged under `assets/community-papers/`. Update the catalogue's checked date and sitemap last-modified dates when making substantive changes.
