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
    return result


def write_english(source, target):
    result = localize(source.read_text(encoding='utf-8'))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(result.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-8'))


if __name__ == '__main__':
    write_english(ROOT.parent / 'materials/ICLR2027_materials/analysis.html', ROOT / 'analysis/index.html')
    print('English explorer generated; scientific data preserved exactly.')
