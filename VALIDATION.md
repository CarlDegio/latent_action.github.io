# Website validation — 2026-09-26

## English metric explorer

- Translated controls, experiment group headings, all 17 metric explanations, chart labels, accessibility text, export messages, and session errors. Updated the homepage link and removed its Chinese-language badge.
- Compared every scientific field with the published page before translation, including experiment identifiers, values, missing entries, source columns, and workbook SHA-256: identical. The downloaded workbook, Table 1, figures, and videos were not changed.
- Executed both versions of the calculation code: all 2,142 statistical results and 378 rankings matched exactly across datasets, heads, probe directions, experiment groups, empty selections, and small samples. Local edits, reset, and session round trips also matched. All inline scripts compiled.
- Checked desktop (1280 px) and mobile (390 / 320 px) layouts. Added wrapping for the long workbook hash to prevent mobile overflow. Verified group selection, dataset changes, empty-state messages, CSV export status, English text, and no browser console errors.
- The external materials were updated during this check, including an English explorer with a different workbook hash. This release deliberately translates the existing published snapshot and preserves its workbook and session compatibility. The full source-snapshot verifier still reports external source drift; the manifest was not refreshed to hide it. Website references, Table 1 values, English text, video/poster pairs, and the downloaded workbook snapshot pass their checks.

## Original redesign checks

- Parsed all 216 Table 1 values from the active manuscript and verified an exact match in both the website data and downloadable CSV.
- Checked 56 local asset/anchor references, 13 video/poster pairs, and 33 source hashes. Paper/material imports are read only; all outputs are in this website repository.
- Confirmed JavaScript syntax and whitespace checks.
- Inspected the desktop homepage and findings layout in the browser, and the mobile homepage at 390 px. Checked document overflow at 320, 390, and 768 px; none found. Tables scroll within their own region.
- Switched all six research panels and all three benchmarks. Verified the two highlighted group winners for each benchmark and descending average sorting.
- Opened and closed the figure dialog. On mobile, full-size figures scroll in a dedicated viewport (900 px image within a 341 px viewport).
- Switched all five demonstration tasks and both disturbance examples. Verified video source names, 1.5× playback rate, and actual paired H.264 playback with both players ready and no media errors. Restart pauses both players and returns them to time zero.
- Confirmed citation clipboard copy and no browser console errors on the main page.
- Opened the copied metric explorer, selected the five main configurations with RoboTwin / DAP–LAP mean / MSE Gain, and confirmed recomputed correlations and plotted data.

The source manuscript PDF was recompiled externally during the work (11:42 local time). Its current text was checked against the displayed recommendations and real-world totals; the other imported source hashes remained unchanged. The manifest records the final observed PDF hash. The website does not distribute the anonymous manuscript PDF.
