/* MemeHunter dashboard: market discovery plus a review-only Creator Studio queue. */
(() => {
  const API = window.MEMEHUNTER_API_URL || '/api/v1';
  const filters = document.querySelectorAll('.filter');
  const empty = document.getElementById('empty-state');
  const rows = document.getElementById('opportunity-rows');
  const count = document.getElementById('opportunity-count');
  const draftGrid = document.getElementById('creator-drafts');
  const draftEmpty = document.getElementById('creator-empty');
  let opportunities = [];
  const setText = (id, value) => {
    const node = document.getElementById(id);
    if (node) node.textContent = value;
  };
  const money = value => '$' + Number(value || 0).toLocaleString('en-US', {maximumFractionDigits: 2});
  function riskLabel(item) {
    const labels = { high: 'Risque élevé', watch: 'À surveiller', unknown: 'Données insuffisantes', no_obvious_flag: 'Aucun signal évident' };
    return labels[item.risk_status] || 'Non évalué';
  }
  function riskDescription(item) {
    const labels = {
      'risk:unknown_liquidity': 'Liquidité indisponible',
      'risk:very_low_liquidity': 'Liquidité très faible',
      'risk:low_liquidity': 'Liquidité faible',
      'risk:very_low_activity': 'Activité très faible ou données manquantes',
      'risk:sell_pressure': 'Pression vendeuse',
      'risk:high_valuation_to_liquidity': 'Valorisation élevée par rapport à la liquidité',
      'risk:unknown_valuation_ratio': 'Ratio valorisation/liquidité inconnu',
      'risk:no_obvious_market_flag': 'Aucun signal de risque évident — cela ne garantit pas la sécurité'
    };
    return (item.risk_flags || []).map(flag => labels[flag] || flag).join(' · ') || 'Évaluation du risque non disponible';
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
      const label = item.token_symbol ? (item.token_name || 'Token') + ' ($' + item.token_symbol + ')' : (item.text || '').slice(0, 100);
      const isMarket = ['dexscreener', 'geckoterminal'].includes(item.source);
      const activity = isMarket ? money(item.volume_24h_usd) + ' vol. 24h' :
        (item.likes + item.reposts + item.replies + item.quotes) + ' interactions';
      const values = [label || 'Signal public', item.score + '/100', activity, riskLabel(item), isMarket ? 'Voir le token' : 'Ouvrir le post'];
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
          link.href = item.url; link.target = '_blank'; link.rel = 'noopener noreferrer'; link.textContent = value;
          td.appendChild(link);
        } else td.textContent = value;
        tr.appendChild(td);
      });
      rows.appendChild(tr);
    }
  }
  function renderDrafts(data) {
    const items = data.items || [];
    const limit = Number(data.daily_limit || 5);
    const used = Number(data.created_today || 0);
    setText('launch-count', used + ' / ' + limit);
    const progress = document.getElementById('launch-progress');
    if (progress) progress.style.width = Math.min(100, used / Math.max(1, limit) * 100) + '%';
    setText('creator-count', items.length + ' fiche' + (items.length > 1 ? 's' : '') + ' · ' + used + '/' + limit + ' aujourd’hui');
    if (!draftGrid || !draftEmpty) return;
    draftGrid.replaceChildren();
    draftEmpty.hidden = items.length > 0;
    if (!items.length) {
      draftEmpty.textContent = 'Aucune fiche pour le moment. MemeHunter cherche les posts publics sur Bluesky.';
      return;
    }
    for (const item of items) {
      const card = document.createElement('article');
      card.className = 'creator-card';
      const top = document.createElement('div'); top.className = 'creator-card-top';
      const score = document.createElement('span'); score.className = 'creator-score'; score.textContent = (item.score ?? '—') + '/100';
      const status = document.createElement('span'); status.className = 'creator-status'; status.textContent = 'À vérifier';
      top.append(score, status);
      const title = document.createElement('h4'); title.textContent = item.name || 'Concept sans nom';
      const ticker = document.createElement('div'); ticker.className = 'creator-ticker'; ticker.textContent = '$' + (item.symbol || 'TBD');
      const artwork = document.createElement('div'); artwork.className = 'creator-artwork';
      const imageUrls = Array.isArray(item.image_urls) ? item.image_urls : [];
      const altTexts = Array.isArray(item.image_alt_texts) ? item.image_alt_texts : [];
      const safeImages = imageUrls.filter(url => {
        try { const parsed = new URL(url); return parsed.protocol === 'https:' && ['pbs.twimg.com', 'cdn.bsky.app'].includes(parsed.hostname); }
        catch (_) { return false; }
      });
      if (safeImages.length) {
        safeImages.slice(0, 4).forEach((url, index) => {
          const image = document.createElement('img');
          image.src = url; image.alt = altTexts[index] || 'Image du post social source';
          image.loading = 'lazy'; image.referrerPolicy = 'no-referrer';
          artwork.append(image);
        });
      } else {
        const placeholder = document.createElement('span');
        placeholder.textContent = 'Aucune image dans le post · logo à générer';
        artwork.append(placeholder);
      }
      const description = document.createElement('p'); description.textContent = item.description || 'Description à compléter.';
      const source = document.createElement('a'); source.href = item.source_url || '#'; source.target = '_blank'; source.rel = 'noopener noreferrer'; source.textContent = 'Voir le post source ↗';
      const footer = document.createElement('div'); footer.className = 'creator-card-footer';
      const art = document.createElement('span'); art.textContent = 'Visuel à préparer';
      const launch = document.createElement('span'); launch.textContent = 'Aucun lancement';
      footer.append(art, launch);
      card.append(top, artwork, title, ticker, description, source, footer);
      draftGrid.append(card);
    }
  }
  async function load() {
    try {
      const responses = await Promise.all([
        fetch(API + '/health'),
        fetch(API + '/opportunities?limit=100'),
        fetch(API + '/creator/drafts?limit=20')
      ]);
      if (responses.some(response => !response.ok)) throw new Error('API unavailable');
      const [health, data, drafts] = await Promise.all(responses.map(response => response.json()));
      opportunities = data.items || [];
      setText('metric-total', String(data.total ?? opportunities.length));
      setText('metric-score', opportunities.length
        ? Math.round(opportunities.reduce((sum, item) => sum + item.score, 0) / opportunities.length) + '/100' : '—');
      const status = document.querySelector('.top-actions .status');
      if (status) status.textContent = health.status === 'ok'
        ? 'MemeHunter connecté · Bluesky + on-chain'
        : 'API indisponible';
      render(document.querySelector('.filter.active')?.dataset.filter || 'all');
      renderDrafts(drafts);
    } catch (_) {
      const status = document.querySelector('.top-actions .status');
      if (status) status.textContent = 'Connexion indisponible · vérifier le service MemeHunter';
      render();
      renderDrafts({items: [], created_today: 0, daily_limit: 5});
    }
  }
  filters.forEach(button => button.addEventListener('click', () => {
    filters.forEach(item => item.classList.toggle('active', item === button));
    render(button.dataset.filter);
  }));
  load();
  window.setInterval(load, 15000);
})();
