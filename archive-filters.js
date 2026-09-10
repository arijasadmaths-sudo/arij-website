(() => {
  const form = document.querySelector('#archive-filters');
  if (!form) return;

  const yearSelect = form.querySelector('#archive-year');
  const typeSelect = form.querySelector('#archive-type');
  const count = form.querySelector('#archive-filter-count');
  const empty = document.querySelector('#archive-filter-empty');
  const entries = Array.from(document.querySelectorAll('[data-archive-entry]'));
  const groups = Array.from(document.querySelectorAll('[data-archive-group]'));
  const headings = document.querySelectorAll('[data-community-heading]');
  const shortcuts = document.querySelectorAll('.archive-jumps a, .archive-nav a');
  const jumps = document.querySelector('.archive-jumps');
  const types = [
    ['papers', 'Question papers'],
    ['written', 'Written solutions / mark schemes'],
    ['answers', 'Answer keys'],
    ['videos', 'Videos'],
    ['guides', 'Guides & other resources']
  ];

  const addOption = (select, value, label) => {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = label;
    select.append(option);
  };
  const years = [...new Set(entries.map(entry => entry.dataset.year))];
  years.filter(year => year !== 'undated').sort((a, b) => Number(b) - Number(a))
    .forEach(year => addOption(yearSelect, year, year));
  if (years.includes('undated')) addOption(yearSelect, 'undated', 'Undated / collections');
  const availableTypes = new Set(entries.flatMap(entry => entry.dataset.types.split(' ')));
  types.filter(([value]) => availableTypes.has(value))
    .forEach(([value, label]) => addOption(typeSelect, value, label));

  const applyFilters = () => {
    let visible = 0;
    entries.forEach(entry => {
      const yearMatches = yearSelect.value === 'all' || entry.dataset.year === yearSelect.value;
      const typeMatches = typeSelect.value === 'all' || entry.dataset.types.split(' ').includes(typeSelect.value);
      entry.hidden = !(yearMatches && typeMatches);
      if (!entry.hidden) visible += 1;
      entry.querySelectorAll('.question-videos').forEach(details => {
        if (!entry.hidden && typeSelect.value === 'videos' && !details.hasAttribute('open')) {
          details.setAttribute('open', '');
          details.dataset.filterOpened = 'true';
        } else if (typeSelect.value !== 'videos' && details.dataset.filterOpened) {
          details.removeAttribute('open');
          delete details.dataset.filterOpened;
        }
      });
    });
    groups.forEach(group => {
      group.hidden = !Array.from(group.querySelectorAll('[data-archive-entry]')).some(entry => !entry.hidden);
    });
    const hasCommunity = groups.some(group => group.hasAttribute('data-community-group') && !group.hidden);
    headings.forEach(heading => { heading.hidden = !hasCommunity; });
    shortcuts.forEach(link => {
      const href = link.getAttribute('href');
      if (!href.startsWith('#')) return;
      const target = document.getElementById(href.slice(1));
      link.hidden = Boolean(target?.hidden);
    });
    if (jumps) jumps.hidden = !Array.from(jumps.querySelectorAll('a')).some(link => !link.hidden);
    count.textContent = `${visible} of ${entries.length} entries shown`;
    empty.hidden = visible !== 0;
  };

  const clearFilters = () => {
    yearSelect.querySelector('option[value="all"]').selected = true;
    typeSelect.querySelector('option[value="all"]').selected = true;
    applyFilters();
  };
  const revealTarget = hash => {
    let id;
    try { id = decodeURIComponent(hash.slice(1)); } catch { return; }
    const target = document.getElementById(id);
    if (target && (target.hidden || target.closest('[data-archive-group]')?.hidden)) clearFilters();
  };

  form.addEventListener('submit', event => event.preventDefault());
  yearSelect.addEventListener('change', applyFilters);
  typeSelect.addEventListener('change', applyFilters);
  form.querySelector('[data-clear-filters]').addEventListener('click', clearFilters);
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href^="#"]');
    if (link) revealTarget(link.getAttribute('href'));
  });
  window.addEventListener('hashchange', () => revealTarget(window.location.hash));

  applyFilters();
  form.hidden = false;
})();
