"""Import read-only research sources into the website. Run from repository root."""
import hashlib
import base64
import csv
import json
from pathlib import Path
import re
import shutil
import subprocess

from PIL import Image, ImageOps, ImageDraw
from localize_analysis import write_english

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT.parent / 'iclr2027'
MATERIALS = ROOT.parent / 'materials' / 'ICLR2027_materials'
OUT = ROOT / 'assets'
QA = ROOT / '.local' / 'qa'
QA.mkdir(parents=True, exist_ok=True)
manifest = []

def record(source, target=None):
    manifest.append({'source': str(source.relative_to(ROOT.parent)).replace('\\', '/'),
                     'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                     'output': str(target.relative_to(ROOT)).replace('\\', '/') if target else None})

def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    record(source, target)

names = {'main': 'pipeline', 'cfm': 'modeling', 'lambda_all_final': 'regularization',
         'actionhead': 'integration', 'metrics': 'metrics', 'latentdims': 'dimensions',
         'denorm': 'normalization', 'scalelaw': 'corpus', 'realworld': 'real-world',
         'training_process': 'training'}
figures = OUT / 'figures'
figures.mkdir(parents=True, exist_ok=True)
for source_name, name in names.items():
    source = PAPER / 'images' / f'{source_name}.pdf'
    target = figures / f'{name}.webp'
    subprocess.run(['pdftoppm', '-f', '1', '-singlefile', '-scale-to', '2400',
                    '-png', str(source), str(QA / name)], check=True, capture_output=True)
    im = Image.open(QA / f'{name}.png').convert('RGB')
    im.save(target, 'WEBP', quality=93, method=6)
    record(source, target)

for source in sorted((MATERIALS / 'videos').glob('*.mp4')):
    copy(source, OUT / 'videos' / source.name)
poster_source = MATERIALS / 'videos' / 'index.html'
posters = json.loads(re.search(r'const posters=(\{.*?\});', poster_source.read_text(encoding='utf-8')).group(1))
(OUT / 'posters').mkdir(parents=True, exist_ok=True)
for filename, uri in posters.items():
    (OUT / 'posters' / filename.replace('.mp4', '.jpg')).write_bytes(base64.b64decode(uri.split(',', 1)[1]))
record(poster_source)
write_english(MATERIALS / 'analysis.html', ROOT / 'analysis' / 'index.html')
record(MATERIALS / 'analysis.html', ROOT / 'analysis' / 'index.html')
copy(MATERIALS / 'results.xlsx', ROOT / 'downloads' / 'results.xlsx')

source = PAPER / 'sec' / 'results_summary.tex'
table = source.read_text(encoding='utf-8')
rows = []
for match in re.finditer(r'\\rowcolor\{design(I|II)\}\s*([^\n]+)\n(.*?)\\\\', table, re.S):
    group, name, values = match.groups()
    nums = [float(x) for x in re.findall(r'0\.\d{3}', values)]
    assert len(nums) == 18, (name, len(nums))
    rows.append({'group': group, 'method': name.strip().replace('$\\Delta$', 'Δ'),
                 'values': [nums[i:i+6] for i in range(0, 18, 6)]})
assert len(rows) == 12
(OUT / 'results.js').write_text('window.STUDY_RESULTS = ' + json.dumps(rows, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
with (ROOT / 'downloads' / 'table-1.csv').open('w', encoding='utf-8-sig', newline='') as stream:
    writer = csv.writer(stream)
    writer.writerow(['Design', 'Method', 'Benchmark', 'DAP', 'LAP', 'JAP', 'JAP-DAP', 'JAP-LAP', 'Avg.'])
    for row in rows:
        for benchmark, values in zip(['LIBERO', 'LIBERO-Plus', 'RoboTwin2.0'], row['values']):
            writer.writerow([row['group'], row['method'], benchmark] + [f'{value:.3f}' for value in values])
record(source, OUT / 'results.js')
for source in [PAPER / 'iclr2027_conference.tex', PAPER / 'iclr2027_conference.pdf',
               PAPER / 'sec' / 'experiments.tex', PAPER / 'sec' / 'introduction.tex',
               PAPER / 'sec' / 'methodology.tex', MATERIALS / 'README.md']:
    record(source)
(ROOT / 'source-manifest.json').write_text(json.dumps({'snapshot_date': '2026-09-26', 'files': manifest}, indent=2), encoding='utf-8')

sheet = Image.new('RGB', (1200, 350 * 5), '#efeee9')
d = ImageDraw.Draw(sheet)
for i, name in enumerate(names.values()):
    im = Image.open(figures / f'{name}.webp')
    im.thumbnail((570, 305))
    x, y = (i % 2) * 600, (i // 2) * 350
    d.text((x + 15, y + 10), name, fill='#111111')
    sheet.paste(im, (x + (600-im.width)//2, y + 35))
sheet.save(QA / 'figures-contact.png')
print(f'Imported {len(names)} figures, 13 videos, metric explorer and workbook; extracted {len(rows)*18} table values.')
