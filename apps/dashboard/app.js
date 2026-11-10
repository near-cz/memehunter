/* Dashboard MVP. Data will be supplied by the API in a later step. */
(() => {
  const filters = document.querySelectorAll('.filter');
  const empty = document.getElementById('empty-state');
  const rows = document.getElementById('opportunity-rows');
  const count = document.getElementById('opportunity-count');

  // The dashboard deliberately starts with no fabricated market data.
  const opportunities = [];

  function render(filter = 'all') {
    const visible = opportunities.filter(item => {
      if (filter === 'high') return item.score >= 70;
      if (filter === 'new') return item.isNew;
      return true;
    });
    rows.replaceChildren();
    empty.hidden = visible.length > 0;
    count.textContent = visible.length + (visible.length > 1 ? ' résultats' : ' résultat');
    for (const item of visible) {
      const tr = document.createElement('tr');
      for (const value of [item.name, item.score + '/100', item.engagement, item.sourceLabel]) {
        const td = document.createElement('td');
        td.textContent = value;
        tr.appendChild(td);
      }
      rows.appendChild(tr);
    }
  }

  filters.forEach(button => button.addEventListener('click', () => {
    filters.forEach(item => item.classList.toggle('active', item === button));
    render(button.dataset.filter);
  }));
  render();
})();
