"""Translate the supplementary explorer without changing its scientific data."""
import copy
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TRANSLATIONS = json.loads((Path(__file__).with_name('analysis-en.json')).read_text(encoding='utf-8'))
PATTERN = re.compile('|'.join(re.escape(s) for s in sorted(TRANSLATIONS, key=len, reverse=True)))


def analysis_data(html):
    return json.JSONDecoder().raw_decode(html.split('window.ANALYSIS_DATA=', 1)[1])[0]


def scientific_data(data):
    """Only prose and group display labels may differ between language versions."""
    result = copy.deepcopy(data)
    for key in ['reference', 'head_labels', 'pairing_note', 'mean_note']:
        result.pop(key)
    for experiment in result['experiments']:
        experiment.pop('group')
    return result


def translate_text(text):
    return PATTERN.sub(lambda match: TRANSLATIONS[match.group()], text)


def translate_data(value):
    if isinstance(value, str):
        return translate_text(value)
    if isinstance(value, list):
        return [translate_data(item) for item in value]
    if isinstance(value, dict):
        return {key: translate_data(item) for key, item in value.items()}
    return value


def absolute_ranking(html):
    """Keep every ranking path absolute and expose the magnitude used to sort."""
    if 'id="absoluteHeading"' in html:
        return html
    changes = [
        ("    if(mode==='original')return rows;\n", ''),
        ("      return clone(s);", "      return {...clone(s),ranking:s.ranking==='spearman'?'spearman':'pearson'};"),
        ('<th scope="col">Proxy metric</th>', '<th scope="col">Proxy metric</th><th scope="col" id="absoluteHeading">|Pearson r| ↓</th>'),
        ("    $('rankHeading').textContent=ranking==='original'?'Index':'Rank';", "    $('absoluteHeading').textContent=ranking==='spearman'?'|Spearman ρ| ↓':'|Pearson r| ↓';"),
        ('.map(({name,index,rank})=>{const a=analyses[name];', '.map(({name,index,rank,value})=>{const a=analyses[name];'),
        ("${ranking==='original'?index+1:rank??'—'}", "${rank??'—'}"),
        ('</button></td><td title="${esc(a.reason)}">${coefficient(a.r)}', '</button></td><td class="absolute-coef">${number(value===null?null:Math.abs(value))}</td><td title="${esc(a.reason)}">${coefficient(a.r)}'),
        ("'rank_mode','rank','n'", "'rank_mode','rank','absolute_correlation','n'"),
        ('.forEach(({name,rank})=>{const a=analyses[name];', '.forEach(({name,rank,value})=>{const a=analyses[name];'),
        ('ranking,rank,a.n,a.r', 'ranking,rank,value===null?null:Math.abs(value),a.n,a.r'),
        ("enum:['pearson','spearman','original']", "enum:['pearson','spearman']"),
        ('ranking=input.ranking??ranking;', "ranking=input.ranking==='original'?'pearson':input.ranking??ranking;"),
    ]
    for old, new in changes:
        assert html.count(old) == 1, f'Ranking source changed: {old}'
        html = html.replace(old, new)
    html, count = re.subn(r'<div class="ranking-control">.*?</div>', '<div class="ranking-control"><label for="ranking">Sort by absolute value</label><select id="ranking"><option value="pearson">|Pearson r|: descending</option><option value="spearman">|Spearman ρ|: descending</option></select></div>', html, count=1)
    assert count == 1
    html, count = re.subn(r'<p class="table-note">.*?</p>', '<p class="table-note">Sorted by absolute correlation, highest first. The highlighted column shows the value used for sorting; the original coefficients keep their signs. Equal magnitudes share a rank; undefined values appear last.<br>Positive <span class="legend-swatch positive"></span> Negative <span class="legend-swatch negative"></span> — means undefined. Scroll horizontally on small screens to see all columns.</p>', html, count=1)
    assert count == 1
    return html.replace('</style>', '\n.correlations table{min-width:520px}.correlations .absolute-coef{font-weight:600;color:#174e96;background:#edf3ff}#absoluteHeading{color:#174e96;font-weight:600}.analysis-grid{grid-template-columns:minmax(540px,1.1fr) minmax(380px,.9fr)}@media(max-width:1350px){.analysis-grid{grid-template-columns:minmax(0,1fr)}}\n</style>')


def localize(html):
    before, tail = html.split('window.ANALYSIS_DATA=', 1)
    original, end = json.JSONDecoder().raw_decode(tail)
    translated = translate_data(original)
    assert scientific_data(original) == scientific_data(translated), 'Scientific data changed during translation'
    # Escape less-than characters so JSON stays safely inside its script element.
    payload = json.dumps(translated, ensure_ascii=False).replace('<', '\\u003c')
    result = translate_text(before) + 'window.ANALYSIS_DATA=' + payload + translate_text(tail[end:])
    result = result.replace('lang="zh-CN"', 'lang="en"')
    # Keep the workbook hash within the mobile viewport.
    result = result.replace('</style>', '\nfooter{overflow-wrap:anywhere}\n</style>')
    remaining = re.findall(r'.{0,35}[\u3400-\u9fff]+.{0,35}', result)
    if remaining:
        raise ValueError('Untranslated text: ' + '\n'.join(remaining))
    return absolute_ranking(result)


def write_english(source, target):
    result = localize(source.read_text(encoding='utf-8'))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(result.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-8'))


if __name__ == '__main__':
    write_english(ROOT.parent / 'materials/ICLR2027_materials/analysis.html', ROOT / 'analysis/index.html')
    print('English explorer generated; scientific data preserved exactly.')
