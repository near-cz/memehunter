/* Dashboard client: source-neutral, read-only MemeHunter API. */
(() => {
  const API = window.MEMEHUNTER_API_URL || '/api/v1';
  const filters = document.querySelectorAll('.filter');
  const empty = document.getElementById('empty-state');
  const rows = document.getElementById('opportunity-rows');
  const count = document.getElementById('opportunity-count');
  let opportunities = [];
  const setText = (id, value) => {
    const node = document.getElementById(id);
    if (node) node.textContent = value;
  };
  function render(filter = 'all') {
    const visible = opportunities.filter(item => {
      if (filter === 'high') return item.score >= 70;
      if (filter === 'new') return Date.now() - Date.parse(item.created_at) < 86400000;
      return true;
    });
    rows.replaceChildren();
    empty.hidden = visible.length > 0;
    count.textContent = visible.length + (visible.length > 1 ? ' résultats' : ' résultat');
    for (const item of visible) {
      const tr = document.createElement('tr');
      const label = item.token_symbol ? item.token_name + ' ($' + item.token_symbol + ')' : (item.text || '').slice(0, 100);
      const activity = ['dexscreener', 'geckoterminal'].includes(item.source)
        ? '$' + Math.round(item.volume_24h_usd || 0).toLocaleString('en-US') + ' vol. 24h'
        : (item.likes + item.reposts + item.replies + item.quotes) + ' interactions';
      const values = [label || 'Signal public', item.score + '/100', activity, ['dexscreener', 'geckoterminal'].includes(item.source) ? 'Voir le token' : 'Ouvrir le post'];
      values.forEach((value, index) => {
        const td = document.createElement('td');
        if (index === 3 && item.url) {
          const link = document.createElement('a');
          link.href = item.url;
          link.target = '_blank';
          link.rel = 'noopener noreferrer';
          link.textContent = value;
          td.appendChild(link);
        } else td.textContent = value;
        tr.appendChild(td);
      });
      rows.appendChild(tr);
    }
  }
  async function load() {
    try {
      const [healthResponse, dataResponse] = await Promise.all([fetch(API + '/health'), fetch(API + '/opportunities?limit=100')]);
      if (!healthResponse.ok || !dataResponse.ok) throw new Error('API unavailable');
      const health = await healthResponse.json();
      const data = await dataResponse.json();
      opportunities = data.items || [];
      setText('metric-total', String(data.total ?? opportunities.length));
      setText('metric-score', opportunities.length
        ? Math.round(opportunities.reduce((sum, item) => sum + item.score, 0) / opportunities.length) + '/100' : '—');
      const status = document.querySelector('.top-actions .status');
      if (status) status.textContent = health.status === 'ok' ? 'API locale connectée · lecture seule' : 'API indisponible';
      render(document.querySelector('.filter.active')?.dataset.filter || 'all');
    } catch (_) {
      const status = document.querySelector('.top-actions .status');
      if (status) status.textContent = 'API non connectée · démarrer memehunter-api';
      render();
    }
  }
  filters.forEach(button => button.addEventListener('click', () => {
    filters.forEach(item => item.classList.toggle('active', item === button));
    render(button.dataset.filter);
  }));
  load();
  window.setInterval(load, 15000);
})();
