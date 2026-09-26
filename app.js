'use strict';

// All data are local; no analytics, third-party scripts, or build step are required.
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

const findingTabs = $$('[data-finding]');
function showFinding(tab) {
  findingTabs.forEach((item) => {
    const selected = item === tab;
    item.setAttribute('aria-selected', String(selected));
    item.tabIndex = selected ? 0 : -1;
    document.getElementById(item.getAttribute('aria-controls')).hidden = !selected;
  });
}
findingTabs.forEach((tab, index) => {
  tab.addEventListener('click', () => showFinding(tab));
  tab.addEventListener('keydown', (event) => {
    let next;
    if (['ArrowDown', 'ArrowRight'].includes(event.key)) next = (index + 1) % findingTabs.length;
    if (['ArrowUp', 'ArrowLeft'].includes(event.key)) next = (index - 1 + findingTabs.length) % findingTabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = findingTabs.length - 1;
    if (next === undefined) return;
    event.preventDefault();
    showFinding(findingTabs[next]);
    findingTabs[next].focus();
  });
});

const benchmarkNames = ['LIBERO', 'LIBERO-Plus', 'RoboTwin2.0'];
let selectedBenchmark = 0;
function renderResults() {
  const body = $('#result-body');
  body.replaceChildren();
  ['I', 'II'].forEach((group) => {
    const rows = window.STUDY_RESULTS.filter((row) => row.group === group);
    if ($('#result-order').value === 'average') rows.sort((a, b) => b.values[selectedBenchmark][5] - a.values[selectedBenchmark][5]);
    const best = Math.max(...rows.map((row) => row.values[selectedBenchmark][5]));
    const heading = document.createElement('tr');
    heading.className = 'group-row';
    const title = document.createElement('th');
    title.colSpan = 7;
    title.textContent = group === 'I' ? 'Design I · Latent action modeling paradigms' : 'Design II · Learning objectives and regularization';
    heading.append(title);
    body.append(heading);
    rows.forEach((row) => {
      const tr = document.createElement('tr');
      const method = document.createElement('th');
      method.scope = 'row';
      method.textContent = row.method;
      tr.append(method);
      row.values[selectedBenchmark].forEach((value, index) => {
        const cell = document.createElement('td');
        cell.textContent = (value * 100).toFixed(1);
        if (index === 5 && value === best) {
          cell.className = 'best-average';
          cell.setAttribute('aria-label', `${cell.textContent} percent, best average in this design group`);
        }
        tr.append(cell);
      });
      body.append(tr);
    });
  });
  $('#result-caption').textContent = `${benchmarkNames[selectedBenchmark]} · success rate (%) · averaged over 3 seeds`;
}
$$('[data-benchmark]').forEach((button) => button.addEventListener('click', () => {
  selectedBenchmark = Number(button.dataset.benchmark);
  $$('[data-benchmark]').forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
  renderResults();
}));
$('#result-order').addEventListener('change', renderResults);
renderResults();

const videos = [$('#video-baseline'), $('#video-tuned')];
const taskNames = {close_drawer: 'Close drawer', open_drawer: 'Open drawer', stack_bowls: 'Stack bowls', place_block: 'Place block', disturbance_recovery: 'Disturbance recovery'};
const videoNote = 'Demonstration clips are independent recordings; paired playback does not imply frame alignment. Disturbance recovery is a qualitative demonstration.';
let selectedTask = 'close_drawer';
let videoGeneration = 0;
function updatePlayButton() {
  $('#play-pair').textContent = videos.some((video) => !video.paused && !video.ended) ? 'Ⅱ Pause both' : '▶ Play both';
}
function selectTask(task) {
  selectedTask = task;
  $('#video-example').value = 'demo01';
  $('#example-label').hidden = task !== 'disturbance_recovery';
  $$('[data-task]').forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.task === task)));
  loadVideos();
}
function loadVideos() {
  videoGeneration += 1;
  $('#play-pair').disabled = false;
  const example = selectedTask === 'disturbance_recovery' ? $('#video-example').value : 'demo01';
  videos.forEach((video, index) => {
    video.pause();
    const method = index === 0 ? 'openvla_oft' : 'openvla_oft_la_tuned';
    const file = `${selectedTask}__${method}__${example}`;
    video.poster = `assets/posters/${file}.jpg`;
    video.src = `assets/videos/${file}.mp4`;
    video.load();
    video.playbackRate = Number($('#video-speed').value);
    const label = index === 0 ? 'baseline' : 'LA-Tuned';
    video.setAttribute('aria-label', `${taskNames[selectedTask]}, OpenVLA-OFT ${label} demonstration`);
    $(`#${index === 0 ? 'baseline' : 'tuned'}-caption`).textContent = `${taskNames[selectedTask]} · ${label}${selectedTask === 'disturbance_recovery' ? ' · Example ' + example.slice(-2) : ''}`;
  });
  $('#video-status').textContent = videoNote;
  updatePlayButton();
}
videos.forEach((video) => {
  video.muted = true;
  ['play', 'pause', 'ended'].forEach((event) => video.addEventListener(event, updatePlayButton));
  video.addEventListener('error', () => {
    $('#video-status').textContent = 'This video could not be loaded. Please retry or use the individual player controls.';
  });
});
$$('[data-task]').forEach((button) => button.addEventListener('click', () => selectTask(button.dataset.task)));
$$('.robot-grid a').forEach((link, index) => link.addEventListener('click', () => selectTask(Object.keys(taskNames)[index])));
$('#video-example').addEventListener('change', loadVideos);
$('#video-speed').addEventListener('change', () => videos.forEach((video) => { video.playbackRate = Number($('#video-speed').value); }));
$('#play-pair').addEventListener('click', async () => {
  if (videos.some((video) => !video.paused && !video.ended)) {
    videos.forEach((video) => video.pause());
    return;
  }
  const generation = videoGeneration;
  $('#play-pair').disabled = true;
  videos.forEach((video) => { if (video.ended) video.currentTime = 0; });
  const results = await Promise.allSettled(videos.map((video) => video.play()));
  if (generation !== videoGeneration) return;
  $('#play-pair').disabled = false;
  if (results.some((result) => result.status === 'rejected')) {
    videos.forEach((video) => video.pause());
    $('#video-status').textContent = 'Paired playback is unavailable. Please try the play control on each video.';
  } else $('#video-status').textContent = videoNote;
  updatePlayButton();
});
$('#restart-pair').addEventListener('click', () => {
  videos.forEach((video) => { video.pause(); video.currentTime = 0; });
  updatePlayButton();
});
// Stop playback when the visitor leaves the demonstration section or browser tab.
new IntersectionObserver(([entry]) => {
  if (!entry.isIntersecting) $$('#real-world video').forEach((video) => video.pause());
}).observe($('#real-world'));
document.addEventListener('visibilitychange', () => {
  if (document.hidden) $$('video').forEach((video) => video.pause());
});
$('.experiment-detail').addEventListener('toggle', (event) => {
  if (!event.currentTarget.open) $('.realworld-detail video').pause();
});

const figureDialog = $('#figure-dialog');
let figureTrigger;
$$('[data-zoom]').forEach((button) => button.addEventListener('click', () => {
  figureTrigger = button;
  const description = button.querySelector('img')?.alt || button.textContent.trim();
  $('#expanded-figure').src = button.dataset.zoom;
  $('#expanded-figure').alt = description;
  $('#figure-title').textContent = description;
  figureDialog.showModal();
  figureDialog.scrollTop = 0;
  figureDialog.scrollLeft = 0;
  document.body.classList.add('dialog-open');
}));
$('#close-figure').addEventListener('click', () => figureDialog.close());
figureDialog.addEventListener('click', (event) => {
  if (event.target !== figureDialog) return;
  const box = figureDialog.getBoundingClientRect();
  if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) figureDialog.close();
});
figureDialog.addEventListener('close', () => {
  document.body.classList.remove('dialog-open');
  figureTrigger?.focus({preventScroll: true});
});

$('#copy-citation').addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText($('#bibtex').textContent);
    $('#copy-status').textContent = 'BibTeX copied to clipboard.';
  } catch {
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents($('#bibtex'));
    selection.removeAllRanges();
    selection.addRange(range);
    $('#copy-status').textContent = 'Citation selected. Press Ctrl+C (or ⌘C) to copy.';
  }
});

const navLinks = $$('.site-header nav a');
const sections = navLinks.map((link) => document.querySelector(link.getAttribute('href')));
const activeSections = new Map();
const navigationObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => activeSections.set(entry.target.id, entry.isIntersecting));
  const active = sections.find((section) => activeSections.get(section.id));
  navLinks.forEach((link) => {
    if (active && link.hash === `#${active.id}`) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
}, {rootMargin: '-15% 0px -55% 0px'});
sections.forEach((section) => navigationObserver.observe(section));
