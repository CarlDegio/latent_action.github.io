// Check sorting independently of coefficient sign, including ties and missing values.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync('analysis/index.html', 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(match => match[1]);
scripts.forEach(script => new vm.Script(script));
const context = {window: {}};
vm.createContext(context);
scripts.slice(0, 3).forEach(script => vm.runInContext(script, context));
const {CorrelationCore: core, AnalysisWorkbench: work, window: {ANALYSIS_DATA: data}} = context;
const plain = value => JSON.parse(JSON.stringify(value));
const names = ['negative', 'positive', 'weak', 'missing', 'tied', 'zero'];
const analyses = Object.fromEntries(names.map((name, index) => [name, {
  r: [-0.95, 0.8, -0.2, null, 0.95, 0][index],
  rho: [-0.1, 0.6, -0.9, null, 0.2, 0][index]
}]));
const pearson = core.rankResults(names, analyses, 'pearson');
assert.deepEqual(plain(pearson.map(row => row.name)), ['negative', 'tied', 'positive', 'weak', 'zero', 'missing']);
assert.deepEqual(plain(pearson.map(row => row.rank)), [1, 1, 3, 4, 5, null]);
assert.deepEqual(plain(core.rankResults(names, analyses, 'spearman').map(row => row.name)), ['weak', 'positive', 'tied', 'negative', 'zero', 'missing']);
assert.equal(pearson[0].value, -0.95, 'Sorting must preserve the coefficient sign');
assert.deepEqual(plain(core.rankResults(names, analyses, 'original')), plain(pearson), 'Legacy source order must fall back to absolute Pearson ranking');
const session = work.create(data);
const settings = {selected: ['row16'], dataset: 'LIBERO', head: 'Head1', metric: 'MLP', ranking: 'original', paperDirection: false};
assert.equal(session.restore(session.snapshot(settings)).ranking, 'pearson');
let checked = 0;
for (const dataset of data.datasets) for (const head of data.heads) for (const direction of [false, true]) {
  const results = Object.fromEntries(data.metric_names.map(metric => [metric, core.analyze(data.experiments.map(e => ({
    x: work.metricValue(e, data.proxy_dataset[dataset], metric, direction), y: e.success[dataset][head]
  })))]));
  for (const mode of ['pearson', 'spearman']) {
    const rows = core.rankResults(data.metric_names, results, mode);
    let last = Infinity;
    for (const row of rows) {
      const value = row.value === null ? -Infinity : Math.abs(row.value);
      assert.ok(value <= last, `${dataset}/${head}/${mode} is not descending`);
      last = value;
    }
    checked++;
  }
}
// Exercise the actual statistics-export handler with mixed-sign fixtures.
const exportCode = scripts[3].match(/\$\('exportStats'\)\.onclick=\(\)=>\{[\s\S]*?\n  \};/)[0];
for (const mode of ['pearson', 'spearman']) {
  let output;
  const button = {};
  const exportContext = {$: () => button, core, work, analyses, data: {...data, metric_names: names},
    dataset: 'LIBERO', head: 'Head1', metricLabel: value => value, paperDirection: false,
    ranking: mode, session: {changed: 0}, selected: new Set(['row16']), stem: () => 'test',
    download: (name, content) => {output = content;}, stamp: () => {}};
  vm.runInNewContext(exportCode, exportContext);
  button.onclick();
  const [headers, ...rows] = output.trim().split('\r\n').map(line => line.replace(/^\uFEFF/, '').split(','));
  const absolute = headers.indexOf('absolute_correlation');
  const signed = headers.indexOf(mode === 'pearson' ? 'pearson_r' : 'spearman_rho');
  let last = Infinity;
  for (const row of rows) {
    const magnitude = row[absolute] === '' ? -Infinity : Number(row[absolute]);
    assert.ok(magnitude <= last);
    if (magnitude !== -Infinity) assert.equal(magnitude, Math.abs(Number(row[signed])));
    last = magnitude;
  }
}
console.log(`PASS: signed values, ties, zeros, undefined values, legacy sessions, both CSV export modes, and ${checked} real-data absolute rankings; all scripts compile.`);
