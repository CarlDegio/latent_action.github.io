# What Matters for Latent Actions in Robot Learning

Static research project page, redesigned from the September 26, 2026 manuscript and supplementary materials.

## Preview

No build step or JavaScript dependencies are required. Open `index.html`, or serve the repository:

```sh
python -m http.server 8765 --bind 127.0.0.1
```

Visit `http://127.0.0.1:8765`. The site supports GitHub Pages under a repository subpath; all local asset URLs are relative. `.nojekyll` is retained.

## Content and provenance

- `index.html`, `style.css`, `app.js`: responsive project page, six research findings, benchmark explorer, paired video player, figure viewer, and citation controls.
- `assets/results.js`: the 216 values in manuscript Table 1. Displayed as percentages; paper-reported averages are preserved rather than recomputed from rounded cells.
- `assets/figures/`: WebP renders of the latest manuscript figures. The original PDFs are read only.
- `assets/videos/` and `assets/posters/`: 13 H.264 demonstration videos and existing poster frames from the supplementary package. Clips are independent recordings, not time-aligned trials.
- `analysis/index.html`: exact copy of the supplementary offline metric explorer (Chinese interface), containing 29 experiment labels and 17 metrics. Browser edits do not modify the workbook.
- `downloads/results.xlsx`: exact copy of the supplementary results workbook.
- `downloads/table-1.csv`: manuscript Table 1, with success rates in the original 0–1 scale.
- `source-manifest.json`: relative source paths and SHA-256 hashes for the imported snapshot.

Author names, affiliations, and public paper/code/model/dataset links are retained from the existing project page. The anonymous submission PDF is not republished; the paper link points to the public arXiv preprint. Website findings follow the newer local manuscript, which can differ from that public version.

The paper's scope is preserved: 32 dimensions is the best cross-benchmark average, proxy metrics support screening rather than exact ranking, corpus expansion changes both size and composition, and the real-world aggregate spans four tasks and five checkpoints. LIBERO-Plus uses liberoplus videos in Stages I/II and LIBERO-only policy training in Stage III.

## Updating assets

With Pillow and Poppler available, run `python tools/prepare_assets.py`. It reads the sibling `iclr2027` and `materials/ICLR2027_materials` directories and writes only into this website repository. It never compiles or edits the paper or material sources. Update the manually written research summaries when the manuscript changes.

```sh
python tools/verify_site.py
node --check app.js
```

The verifier checks local references, all 216 values against the paper and CSV, video/poster pairs, and unchanged source hashes. Visual and interaction checks should also cover desktop/mobile layouts, all findings and benchmarks, table ordering, paired playback, both disturbance examples, figure dialog, and citation copy.

## Publishing

Push the website changes to the existing `main` branch. The configured GitHub Pages site is `https://carldegio.github.io/latent_action.github.io/`.
