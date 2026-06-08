
// ============================================================
// -- app.js: Utilitários globais compartilhados por todas as páginas
// -- Contém: API helper, sistema de toasts, formatadores
// ============================================================

// ==========================================
// -- API HELPER: Simplifica chamadas fetch à API REST
// ==========================================
const api = {
  /**
   * -- GET request para a API
   * -- Retorna JSON parseado ou lança erro com mensagem da API
   */
  async get(url) {
    const res = await fetch(url);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `Erro ${res.status}`);
    }
    return res.json();
  },

  /**
   * -- POST request com corpo JSON
   */
  async post(url, body = {}) {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || `Erro ${res.status}`);
    return data;
  },

  /**
   * -- PATCH request com corpo JSON
   */
  async patch(url, body = {}) {
    const res = await fetch(url, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || `Erro ${res.status}`);
    return data;
  },

  /**
   * -- DELETE request
   */
  async del(url) {
    const res = await fetch(url, { method: 'DELETE' });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || `Erro ${res.status}`);
    return data;
  },
};

// ==========================================
// -- SISTEMA DE TOASTS (Notificações visuais)
// ==========================================
const toast = {
  /**
   * -- Exibe uma notificação temporária
   * -- type: 'success' | 'error' | 'info' | 'warning'
   */
  show(message, type = 'info', duration = 3500) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.innerHTML = `<span>${icons[type] || 'ℹ️'}</span> <span>${message}</span>`;

    container.appendChild(el);

    // -- Remove automaticamente após duração
    setTimeout(() => {
      el.classList.add('hiding');
      setTimeout(() => el.remove(), 350);
    }, duration);
  },

  success(msg) { this.show(msg, 'success'); },
  error(msg)   { this.show(msg, 'error', 5000); },
  info(msg)    { this.show(msg, 'info'); },
  warning(msg) { this.show(msg, 'warning'); },
};

// ==========================================
// -- FORMATADORES E UTILITÁRIOS
// ==========================================

/**
 * -- Retorna emoji/ícone para cada classe de personagem
 */
function classIcon(cls) {
  const map = {
    Guerreiro: '⚔️', Mago: '🔮', Ladino: '🗡️',
    Clérigo: '✝️', Ranger: '🏹', Paladino: '🛡️',
  };
  return map[cls] || '🧙';
}

/**
 * -- Retorna CSS class para badge de raridade
 */
function rarityBadgeClass(rarity) {
  const map = {
    'comum': 'badge-comum', 'incomum': 'badge-incomum',
    'raro': 'badge-raro', 'épico': 'badge-épico', 'lendário': 'badge-lendário',
  };
  return `badge ${map[rarity] || 'badge-comum'}`;
}

/**
 * -- Retorna CSS class para badge de classe de personagem
 */
function classBadgeClass(cls) {
  const map = {
    Guerreiro: 'badge-warrior', Mago: 'badge-mage', Ladino: 'badge-rogue',
    Clérigo: 'badge-cleric', Ranger: 'badge-ranger', Paladino: 'badge-paladin',
  };
  return `badge ${map[cls] || 'badge-comum'}`;
}

/**
 * -- Formata data ISO para string legível em pt-BR
 */
function formatDate(iso) {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleDateString('pt-BR', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  } catch { return iso; }
}

/**
 * -- Renderiza uma barra de progresso HTML
 * -- val: valor atual, max: valor máximo, cssClass: classe CSS da barra
 */
function progressBar(val, max, cssClass = 'progress-hp') {
  const pct = max > 0 ? Math.round((val / max) * 100) : 0;
  return `
    <div class="progress-bar-wrap">
      <div class="progress-bar-fill ${cssClass}" style="width:${pct}%"></div>
    </div>
    <div style="font-size:11px; color:var(--text-faint); margin-top:3px;">${val} / ${max} (${pct}%)</div>
  `;
}

/**
 * -- Abre um modal pelo ID
 */
function openModal(modalId) {
  const el = document.getElementById(modalId);
  if (el) el.classList.add('open');
}

/**
 * -- Fecha um modal pelo ID
 */
function closeModal(modalId) {
  const el = document.getElementById(modalId);
  if (el) el.classList.remove('open');
}

// -- Fecha modal ao clicar no overlay (fundo escuro)
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
  }
});

// -- Fecha modal ao pressionar Escape
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.open').forEach(m => m.classList.remove('open'));
  }
});

/**
 * -- Renderiza os efeitos de um item como tags coloridas
 */
function renderItemStats(item) {
  const tags = [];
  if (item.attackBonus  > 0) tags.push(`<span class="item-stat-tag atk">⚔️ +${item.attackBonus} ATK</span>`);
  if (item.defenseBonus > 0) tags.push(`<span class="item-stat-tag def">🛡️ +${item.defenseBonus} DEF</span>`);
  if (item.magicBonus   > 0) tags.push(`<span class="item-stat-tag mag">✨ +${item.magicBonus} MAG</span>`);
  if (item.healAmount   > 0) tags.push(`<span class="item-stat-tag heal">💚 Cura ${item.healAmount} HP</span>`);
  if (item.weaponDie)         tags.push(`<span class="item-stat-tag">🎲 ${item.weaponDie}</span>`);
  (item.effects || []).forEach(ef => tags.push(`<span class="item-stat-tag">${ef}</span>`));
  return `<div class="item-stats">${tags.join('')}</div>`;
}
