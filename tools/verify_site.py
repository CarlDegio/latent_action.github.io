"""Check website links, paper-table fidelity, and read-only source integrity."""
import csv
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links = [], []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for attr in ['src', 'href', 'poster', 'data-zoom']:
            if attrs.get(attr):
                self.links.append(attrs[attr])

page = Page()
page.feed((ROOT / 'index.html').read_text(encoding='utf-8'))
assert len(page.ids) == len(set(page.ids)), 'Duplicate HTML IDs'
for link in page.links:
    parsed = urlsplit(link)
    if parsed.scheme or parsed.netloc:
        continue
    if parsed.path:
        assert (ROOT / unquote(parsed.path)).is_file(), f'Missing file: {link}'
    elif parsed.fragment:
        assert parsed.fragment in page.ids, f'Missing anchor: {link}'

rows = json.loads((ROOT / 'assets/results.js').read_text(encoding='utf-8').split(' = ', 1)[1].rstrip(';\n'))
paper = (ROOT.parent / 'iclr2027/sec/results_summary.tex').read_text(encoding='utf-8')
paper_values = [float(value) for value in re.findall(r'0\.\d{3}', paper)]
site_values = [value for row in rows for benchmark in row['values'] for value in benchmark]
assert site_values == paper_values and len(site_values) == 216, 'Table 1 changed'
with (ROOT / 'downloads/table-1.csv').open(encoding='utf-8-sig', newline='') as stream:
    exported = list(csv.reader(stream))[1:]
assert [float(value) for row in exported for value in row[3:]] == paper_values
assert len(list((ROOT / 'assets/videos').glob('*.mp4'))) == 13
for video in (ROOT / 'assets/videos').glob('*.mp4'):
    assert (ROOT / 'assets/posters' / video.with_suffix('.jpg').name).exists()

manifest = json.loads((ROOT / 'source-manifest.json').read_text(encoding='utf-8'))
changed_sources = []
for record in manifest['files']:
    source = ROOT.parent / record['source']
    if hashlib.sha256(source.read_bytes()).hexdigest() != record['sha256']:
        changed_sources.append(record['source'])
assert not changed_sources, f'Source files changed since import: {changed_sources}'
for name in ['analysis/index.html', 'downloads/results.xlsx']:
    record = next(item for item in manifest['files'] if item['output'] == name)
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == record['sha256']
print(f'PASS: {len(page.links)} references; 216 paper/website/CSV values; 13 video/poster pairs; {len(manifest["files"])} source hashes unchanged.')
