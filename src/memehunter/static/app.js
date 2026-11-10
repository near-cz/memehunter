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
  function riskLabel(item) {
    const labels = {
      high: 'Risque élevé',
      watch: 'À surveiller',
      unknown: 'Données insuffisantes',
      no_obvious_flag: 'Aucun signal évident'
    };
    return labels[item.risk_status] || 'Non évalué';
  }
  function riskDescription(item) {
    const labels = {
      'risk:unknown_liquidity': 'Liquidité indisponible',
      'risk:very_low_liquidity': 'Liquidité très faible',
      'risk:low_liquidity': 'Liquidité faible',
      'risk:very_low_activity': 'Activité très faible',
      'risk:sell_pressure': 'Pression vendeuse',
      'risk:high_valuation_to_liquidity': 'Valorisation élevée par rapport à la liquidité',
      'risk:unknown_valuation_ratio': 'Ratio valorisation/liquidité inconnu',
      'risk:no_obvious_market_flag': 'Aucun signal de risque évident dans les métriques disponibles — cela ne garantit pas la sécurité'
    };
    const flags = item.risk_flags || [];
    return flags.map(flag => labels[flag] || flag).join(' · ') || 'Évaluation du risque non disponible';
  }
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
      const values = [label || 'Signal public', item.score + '/100', activity, riskLabel(item), ['dexscreener', 'geckoterminal'].includes(item.source) ? 'Voir le token' : 'Ouvrir le post'];
      values.forEach((value, index) => {
        const td = document.createElement('td');
        if (index === 3) {
          const risk = document.createElement('span');
          risk.className = 'risk-pill risk-' + (item.risk_status || 'unknown');
          risk.textContent = value;
          risk.title = riskDescription(item);
          td.appendChild(risk);
        } else if (index === 4 && item.url) {
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
      if (status) status.textContent = health.status === 'ok' ? 'MemeHunter connecté · lecture seule' : 'API indisponible';
      render(document.querySelector('.filter.active')?.dataset.filter || 'all');
    } catch (_) {
      const status = document.querySelector('.top-actions .status');
      if (status) status.textContent = 'Connexion indisponible · vérifier le service MemeHunter';
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
