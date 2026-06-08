
// ============================================================
// -- items.js: Loja de itens, inventário e sistema de compra/venda
// ============================================================

let allShopItems   = [];   // -- Todos os itens do catálogo
let allCharactersItems = [];  // -- Personagens para seleção
let currentCharGold = 0;   // -- Ouro do personagem selecionado na loja

// ==========================================
// -- INICIALIZAÇÃO
// ==========================================
document.addEventListener('DOMContentLoaded', async () => {
  await Promise.all([loadShopItems(), loadCharactersForSelectors()]);
});

// ==========================================
// -- ALTERNÂNCIA DE ABAS
// ==========================================
function switchTab(tab) {
  document.getElementById('panel-shop').style.display      = tab === 'shop'      ? 'block' : 'none';
  document.getElementById('panel-inventory').style.display = tab === 'inventory' ? 'block' : 'none';

  document.getElementById('tab-shop').classList.toggle('active',      tab === 'shop');
  document.getElementById('tab-inventory').classList.toggle('active', tab === 'inventory');

  if (tab === 'inventory' && document.getElementById('invCharSelect').value) {
    loadInventory();
  }
}

// ==========================================
// -- CARREGAMENTO DE DADOS
// ==========================================
async function loadShopItems() {
  try {
    allShopItems = await api.get('/api/items/');
    renderShop(allShopItems);
  } catch(e) {
    toast.error('Erro ao carregar itens: ' + e.message);
  }
}

async function loadCharactersForSelectors() {
  try {
    allCharactersItems = await api.get('/api/characters/');

    // -- Preenche os seletores de personagem
    ['shopCharSelect', 'invCharSelect'].forEach(id => {
      const sel = document.getElementById(id);
      if (!sel) return;
      sel.innerHTML = '<option value="">Selecione um personagem</option>' +
        allCharactersItems.map(c =>
          `<option value="${c.id}" data-gold="${c.gold}">${classIcon(c.characterClass)} ${c.name} (Nível ${c.level})</option>`
        ).join('');
    });
  } catch {}
}

function updateGoldDisplay() {
  const sel     = document.getElementById('shopCharSelect');
  const opt     = sel.options[sel.selectedIndex];
  const gold    = opt ? (parseInt(opt.dataset.gold) || 0) : 0;
  currentCharGold = gold;

  const goldEl = document.getElementById('goldDisplay');
  if (sel.value) {
    goldEl.innerHTML = `🪙 <span style="color:var(--gold-300);">${gold}g</span> disponíveis`;
  } else {
    goldEl.innerHTML = '';
  }

  // -- Reaplica filtros para mostrar quais itens o personagem pode comprar
  filterShop();
}

// ==========================================
// -- FILTROS DA LOJA
// ==========================================
function filterShop() {
  const search  = document.getElementById('shopSearch').value.toLowerCase();
  const type    = document.getElementById('shopType').value;
  const rarity  = document.getElementById('shopRarity').value;
  const charId  = document.getElementById('shopCharSelect').value;

  const filtered = allShopItems.filter(it => {
    if (search && !it.name.toLowerCase().includes(search) && !it.description.toLowerCase().includes(search)) return false;
    if (type   && it.type !== type)     return false;
    if (rarity && it.rarity !== rarity) return false;
    return true;
  });

  renderShop(filtered, charId);
}

// ==========================================
// -- RENDERIZAÇÃO DA GRADE DA LOJA
// ==========================================
function renderShop(items, charId = '') {
  const grid = document.getElementById('shopGrid');
  if (items.length === 0) {
    grid.innerHTML = `
      <div class="empty-state" style="grid-column:1/-1;">
        <div class="empty-state-icon">🛒</div>
        <h3>Nenhum item encontrado</h3>
        <p>Tente ajustar os filtros.</p>
      </div>`;
    return;
  }

  grid.innerHTML = items.map((it, i) => {
    const canAfford = charId && currentCharGold >= it.value;
    const btnClass  = charId ? (canAfford ? 'btn-gold' : 'btn-ghost') : 'btn-ghost';
    const btnTitle  = !charId ? 'Selecione um personagem' : (!canAfford ? `Ouro insuficiente (${it.value}g)` : '');

    return `
      <div class="item-card fade-in-up" style="animation-delay:${i*0.03}s;">
        <div class="item-card-top">
          <div class="item-icon">${it.icon || '📦'}</div>
          <div style="flex:1;">
            <div class="item-name">${it.name}</div>
            <div class="item-desc">${it.description}</div>
          </div>
        </div>

        <!-- Raridade e tipo -->
        <div style="display:flex; gap:6px; flex-wrap:wrap; align-items:center;">
          <span class="${rarityBadgeClass(it.rarity)}">${it.rarity}</span>
          <span class="badge badge-comum">${typeLabel(it.type)}</span>
          ${it.slot ? `<span class="badge badge-comum" style="color:var(--text-faint);">slot: ${it.slot}</span>` : ''}
        </div>

        <!-- Stats do item -->
        ${renderItemStats(it)}

        <!-- Efeitos especiais -->
        ${(it.effects || []).length > 0 ? `
          <div style="font-size:11px; color:var(--purple-300);">
            ✨ ${it.effects.join(' · ')}
          </div>` : ''}

        <!-- Preço e botão de compra -->
        <div style="display:flex; align-items:center; justify-content:space-between; margin-top:4px;">
          <div>
            <span class="item-price">🪙 ${it.value}g</span>
            <div class="item-price-sub">Venda: ${Math.max(1, Math.floor(it.value/2))}g</div>
          </div>
          <button class="btn ${btnClass} btn-sm"
                  onclick="buyItem('${it.id}')"
                  ${(!charId || !canAfford) ? 'disabled style="opacity:0.4;"' : ''}
                  title="${btnTitle}">
            ${charId ? (canAfford ? '🛒 Comprar' : '💸 Sem ouro') : '🔒 Selecione'}
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function typeLabel(type) {
  const map = { weapon:'Arma', armor:'Armadura', spell:'Feitiço', potion:'Poção', accessory:'Acessório' };
  return map[type] || type;
}

// ==========================================
// -- COMPRAR ITEM
// ==========================================
async function buyItem(itemId) {
  const charId = document.getElementById('shopCharSelect').value;
  if (!charId) {
    toast.warning('Selecione um personagem antes de comprar.');
    return;
  }

  try {
    const res = await api.post('/api/items/buy', { characterId: charId, itemId });
    toast.success(res.message);

    // -- Atualiza o ouro no seletor
    currentCharGold = res.character.gold;
    document.getElementById('goldDisplay').innerHTML =
      `🪙 <span style="color:var(--gold-300);">${currentCharGold}g</span> disponíveis`;

    // -- Atualiza os dados do personagem no seletor
    const opt = document.querySelector(`#shopCharSelect option[value="${charId}"]`);
    if (opt) opt.dataset.gold = res.character.gold;

    filterShop();
  } catch(e) {
    toast.error(e.message);
  }
}

// ==========================================
// -- INVENTÁRIO DO PERSONAGEM
// ==========================================
async function loadInventory() {
  const charId = document.getElementById('invCharSelect').value;
  const content = document.getElementById('inventoryContent');

  if (!charId) {
    content.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🎒</div>
        <h3>Selecione um personagem</h3>
        <p>Escolha um personagem acima para ver seu inventário.</p>
      </div>`;
    return;
  }

  content.innerHTML = '<div class="loading-center"><div class="spinner"></div></div>';

  try {
    const [char, allItems] = await Promise.all([
      api.get(`/api/characters/${charId}`),
      api.get('/api/items/'),
    ]);

    const itemMap = {};
    allItems.forEach(it => itemMap[it.id] = it);

    if (!char.inventory || char.inventory.length === 0) {
      content.innerHTML = `
        <div style="margin-bottom:16px;">
          <div style="font-family:'Cinzel',serif; font-size:14px; color:var(--text-muted);">
            ${classIcon(char.characterClass)} ${char.name} — Nível ${char.level} &nbsp;|&nbsp;
            🪙 <span style="color:var(--gold-300);">${char.gold}g</span>
          </div>
        </div>
        <div class="empty-state">
          <div class="empty-state-icon">🎒</div>
          <h3>Inventário vazio</h3>
          <p>Visite a loja para comprar equipamentos!</p>
        </div>`;
      return;
    }

    // -- Agrupa por tipo
    const byType = {};
    char.inventory.forEach(itemId => {
      const it = itemMap[itemId];
      if (!it) return;
      if (!byType[it.type]) byType[it.type] = [];
      byType[it.type].push({ ...it, _equipped: Object.values(char.equippedItems || {}).includes(itemId) });
    });

    const typeOrder = ['weapon', 'armor', 'spell', 'accessory', 'potion'];
    const typeIcons = { weapon:'⚔️', armor:'🛡️', spell:'🔮', potion:'🧪', accessory:'💍' };

    content.innerHTML = `
      <!-- Cabeçalho do personagem -->
      <div class="card card-purple" style="margin-bottom:16px; padding:14px 20px;">
        <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
          <div style="font-family:'Cinzel',serif; font-size:16px;">
            ${classIcon(char.characterClass)} ${char.name}
          </div>
          <span class="${classBadgeClass(char.characterClass)}">${char.characterClass}</span>
          <div style="margin-left:auto; font-size:16px; font-family:'Cinzel',serif; color:var(--gold-300);">
            🪙 ${char.gold}g
          </div>
        </div>
        <div style="margin-top:8px; font-size:12px; color:var(--text-faint);">
          ${char.inventory.length} item(s) no inventário
        </div>
      </div>

      <!-- Itens agrupados por tipo -->
      ${typeOrder.filter(t => byType[t]).map(type => `
        <div style="margin-bottom:20px;">
          <div style="font-family:'Cinzel',serif; font-size:12px; color:var(--text-muted);
                      letter-spacing:1px; text-transform:uppercase; margin-bottom:10px;">
            ${typeIcons[type]} ${typeLabel(type)}s
          </div>
          <div class="grid-auto-sm">
            ${byType[type].map(it => `
              <div class="item-card" style="${it._equipped ? 'border-color:rgba(16,185,129,0.4);' : ''}">
                <div class="item-card-top">
                  <div class="item-icon">${it.icon || '📦'}</div>
                  <div>
                    <div class="item-name">${it.name}</div>
                    <span class="${rarityBadgeClass(it.rarity)}">${it.rarity}</span>
                    ${it._equipped ? `<span style="font-size:11px; color:var(--green-400); margin-left:6px;">✓ Equipado</span>` : ''}
                  </div>
                </div>
                ${renderItemStats(it)}
                <div style="display:flex; gap:6px; margin-top:8px; flex-wrap:wrap;">
                  ${it.slot && !it._equipped ? `
                    <button class="btn btn-green btn-sm"
                            onclick="equipItem('${char.id}', '${it.id}', '${it.slot}')">
                      ✅ Equipar
                    </button>` : ''}
                  <button class="btn btn-ghost btn-sm"
                          onclick="sellItem('${char.id}', '${it.id}', '${it.name}', ${Math.max(1, Math.floor(it.value/2))})">
                    💰 Vender (${Math.max(1, Math.floor(it.value/2))}g)
                  </button>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      `).join('')}
    `;
  } catch(e) {
    content.innerHTML = `<p class="text-muted">Erro ao carregar inventário: ${e.message}</p>`;
  }
}

// ==========================================
// -- EQUIPAR ITEM
// ==========================================
async function equipItem(charId, itemId, slot) {
  try {
    await api.post(`/api/characters/${charId}/equip`, { itemId, slot });
    toast.success('Item equipado!');
    loadInventory();
  } catch(e) {
    toast.error(e.message);
  }
}

// ==========================================
// -- VENDER ITEM
// ==========================================
async function sellItem(charId, itemId, itemName, price) {
  if (!confirm(`Vender "${itemName}" por ${price}g?`)) return;
  try {
    const res = await api.post('/api/items/sell', { characterId: charId, itemId });
    toast.success(res.message);
    loadInventory();
    loadCharactersForSelectors();
  } catch(e) {
    toast.error(e.message);
  }
}
