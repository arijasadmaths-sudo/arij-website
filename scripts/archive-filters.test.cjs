const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { parseHTML } = require('linkedom');

const root = path.resolve(__dirname, '..');
const script = fs.readFileSync(path.join(root, 'archive-filters.js'), 'utf8');
const archives = ['tmua-paper-archive', 'step-past-papers', 'esat-paper-archive',
  'jmc-past-papers', 'imc-past-papers', 'smc-past-papers', 'amc10-past-papers',
  'amc12-past-papers', 'aime-past-papers', 'bmo-past-papers'];

function load(name, run = true) {
  const { window } = parseHTML(fs.readFileSync(path.join(root, name + '.html'), 'utf8'));
  window.location = { hash: '' };
  const document = window.document;
  if (run) vm.runInNewContext(script, { window, document });
  return {
    document,
    select(id, value) {
      const select = document.getElementById(id);
      const option = select.querySelector(`option[value="${value}"]`);
      assert.ok(option, `${name}: ${id} lacks ${value}`);
      option.selected = true;
      select.dispatchEvent(new window.Event('change'));
    },
    visible() { return Array.from(document.querySelectorAll('[data-archive-entry]')).filter(node => !node.hidden); },
    clear() { document.querySelector('[data-clear-filters]').click(); }
  };
}

test('all ten archives preserve complete resources without JavaScript and after reset', () => {
  for (const name of archives) {
    const plain = load(name, false);
    assert.ok(plain.document.getElementById('archive-filters').hidden);
    assert.ok(plain.visible().length > 0);
    const page = load(name);
    assert.equal(page.visible().length, plain.visible().length);
    assert.equal(page.document.getElementById('archive-filters').hidden, false);
    const years = page.document.querySelectorAll('#archive-year option');
    page.select('archive-year', years[1].value);
    const types = page.document.querySelectorAll('#archive-type option');
    page.select('archive-type', types[types.length - 1].value);
    page.clear();
    assert.equal(page.visible().length, plain.visible().length);
    assert.deepEqual(
      page.visible().flatMap(node => Array.from(node.querySelectorAll('a')).map(a => a.getAttribute('href'))),
      plain.visible().flatMap(node => Array.from(node.querySelectorAll('a')).map(a => a.getAttribute('href')))
    );
    assert.match(page.document.getElementById('archive-filter-count').textContent, new RegExp(`^${plain.visible().length} of ${plain.visible().length}`));
  }
});

test('BMO filters use exam year, even when the filename uses the following season', () => {
  const page = load('bmo-past-papers');
  page.select('archive-year', '2025');
  page.select('archive-type', 'videos');
  assert.ok(page.visible().length > 0);
  assert.ok(page.visible().every(row => row.dataset.year === '2025'));
  assert.ok(page.visible().some(row => row.innerHTML.includes('bmo1-2026')));
});

test('undated TMUA video results include real walkthroughs and preserve creator credits', () => {
  const page = load('tmua-paper-archive');
  page.select('archive-year', 'undated');
  page.select('archive-type', 'videos');
  const text = page.visible().map(row => row.textContent).join('\n');
  assert.match(text, /Gresty Academy/);
  assert.match(text, /Yotta Paper 1/);
  assert.match(text, /Beyond Horizon/);
  assert.equal(page.document.querySelector('#beyond-horizon-supplied-collection tbody tr').hidden, true);
  assert.ok(page.document.querySelector('#gresty-academy .question-videos').hasAttribute('open'));
  assert.equal(page.document.getElementById('gresty-academy').hidden, false);
});

test('combined booklets match answer-key filter without restoring removed community keys', () => {
  const page = load('tmua-paper-archive');
  page.select('archive-year', 'undated');
  page.select('archive-type', 'answers');
  const text = page.visible().map(row => row.textContent).join('\n');
  assert.match(text, /Practice booklet: Level 1/);
  assert.match(text, /Practice booklet: Level 2/);
  assert.doesNotMatch(text, /Yotta|Beyond Horizon/);
});

test('STEP video filter finds standalone collections even though no paper rows contain videos', () => {
  const page = load('step-past-papers');
  page.select('archive-type', 'videos');
  assert.equal(page.visible().length, 3);
  assert.ok(page.visible().every(entry => entry.tagName === 'LI'));
  assert.match(page.visible().map(entry => entry.textContent).join('\n'), /Foundation video solutions/);
  assert.equal(page.document.getElementById('mathsaurus-step-video-solutions').hidden, false);
});

test('empty results, section shortcuts and reset remain consistent', () => {
  const page = load('step-past-papers');
  page.select('archive-year', '1986');
  page.select('archive-type', 'written');
  assert.equal(page.visible().length, 0);
  assert.equal(page.document.getElementById('archive-filter-empty').hidden, false);
  assert.ok(Array.from(page.document.querySelectorAll('[data-archive-group]')).every(group => group.hidden));
  assert.ok(page.document.querySelector('.archive-jumps').hidden);
  page.clear();
  assert.ok(page.visible().length > 100);
  assert.ok(page.document.getElementById('archive-filter-empty').hidden);
  assert.equal(page.document.querySelector('.archive-jumps').hidden, false);
});

test('dated mirror resources and Cambridge solutions follow the labelled exam year', () => {
  const tmua = load('tmua-paper-archive');
  tmua.select('archive-year', '2023');
  tmua.select('archive-type', 'written');
  assert.equal(tmua.visible().filter(entry => entry.tagName === 'LI').length, 2);
  const step = load('step-past-papers');
  step.select('archive-year', '2025');
  step.select('archive-type', 'written');
  assert.ok(step.visible().some(entry => entry.innerHTML.includes('/2026-04/STEP2_2025')));
});

test('a teaching-guide anchor reveals a section hidden by filters', () => {
  const page = load('tmua-paper-archive');
  page.select('archive-year', '2023');
  const target = page.document.getElementById('jz-maths-logic-worksheets');
  assert.ok(target.hidden);
  page.document.querySelector('#practice-guidance a[href="#jz-maths-logic-worksheets"]').click();
  assert.equal(target.hidden, false);
  assert.equal(page.document.getElementById('archive-year').value, 'all');
});
