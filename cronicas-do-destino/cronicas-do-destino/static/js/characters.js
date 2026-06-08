
// ============================================================
// -- characters.js: Gerenciamento completo de personagens
// -- Funcionalidades: CRUD, filtragem, detalhes, inventário
// ============================================================

// -- Dados globais da página
let allCharacters = [];   // -- Todos os personagens carregados
let allProfiles   = [];   // -- Todos os perfis carregados

// -- Stats base por classe (para preview no formulário)
const CLASS_STATS = {
  Guerreiro: { hp: 120, attack: 18, defense: 14, magic: 4 },
  Mago:      { hp: 80,  attack: 8,  defense: 8,  magic: 22 },
  Ladino:    { hp: 90,  attack: 15, defense: 10, magic: 8 },
  Clérigo:   { hp: 100, attack: 10, defense: 12, magic: 16 },
  Ranger:    { hp: 95,  attack: 14, defense: 11, magic: 10 },
  Paladino:  { hp: 110, attack: 14, defense: 16, magic: 12 },
};

// ==========================================
// -- INICIALIZAÇÃO
// ==========================================
document.addEventListener('DOMContentLoaded', async () => {
  await Promise.all([loadProfiles(), loadCharacters()]);

  // -- Verifica se há filtro de perfil na URL
  const urlParams = new URLSearchParams(window.location.search);
  const profileId = urlParams.get('profile');
  if (profileId) {
    document.getElementById('filterProfile').value = profileId;
    filterCharacters();
  }
});

// ==========================================
// -- CARREGAMENTO DE DADOS
// ==========================================
async function loadCharacters() {
  try {
    allCharacters = await api.get('/api/characters/');
    renderCharacters(allCharacters);
  } catch(e) {
    toast.error('Erro ao carregar personagens: ' + e.message);
    document.getElementById('charactersGrid').innerHTML = `
      <div class="empty-state" style="grid-column:1/-1;">
        <div class="empty-state-icon">⚠️</div>
        <h3>Erro ao carregar</h3>
        <p>${e.message}</p>
      </div>`;
  }
}

async function loadProfiles() {
  try {
    allProfiles = await api.get('/api/profiles/');

    // -- Preenche o filtro de perfil no topo
    const filterSel = document.getElementById('filterProfile');
    if (filterSel) {
      filterSel.innerHTML = '<option value="">Todos os perfis</option>' +
        allProfiles.map(p => `<option value="${p.id}">${p.avatar} ${p.name}</option>`).join('');
    }

    // -- Preenche o seletor no formulário de criação
    const formSel = document.getElementById('charProfile');
    if (formSel) {
      formSel.innerHTML = '<option value="">Sem perfil</option>' +
        allProfiles.map(p => `<option value="${p.id}">${p.avatar} ${p.name}</option>`).join('');
    }
  } catch {}
}

// ==========================================
// -- RENDERIZAÇÃO DA GRADE DE PERSONAGENS
// ==========================================
function renderCharacters(chars) {
  const grid = document.getElementById('charactersGrid');

  if (chars.length === 0) {
    grid.innerHTML = `
      <div class="empty-state" style="grid-column:1/-1;">
        <div class="empty-state-icon">🧙</div>
        <h3>Nenhum personagem encontrado</h3>
        <p>Crie seu primeiro personagem ou ajuste os filtros.</p>
      </div>`;
    return;
  }

  grid.innerHTML = chars.map((c, i) => `
    <div class="character-card fade-in-up" style="animation-delay:${i*0.04}s;">
      <!-- -- Cabeçalho do card -->
      <div style="display:flex; align-items:flex-start; gap:12px; margin-bottom:12px;">
        <div class="character-avatar">${classIcon(c.characterClass)}</div>
        <div style="flex:1; min-width:0;">
          <div class="character-name">${c.name}</div>
          <div class="character-sub">
            <span class="${classBadgeClass(c.characterClass)}">${c.characterClass}</span>
            &nbsp;${c.race}
          </div>
        </div>
        <div style="text-align:right; flex-shrink:0;">
          <div style="font-family:'Cinzel',serif; font-size:13px; color:var(--purple-300);">Nível ${c.level}</div>
          <div style="font-size:12px; color:var(--gold-300);">🪙 ${c.gold}g</div>
        </div>
      </div>

      <!-- -- Barras de HP e XP -->
      <div style="margin-bottom:8px;">
        <div style="font-size:11px; color:var(--text-faint); margin-bottom:3px;">
          HP: ${c.hp}/${c.maxHp}
        </div>
        ${progressBar(c.hp, c.maxHp, 'progress-hp')}
      </div>
      <div style="margin-bottom:12px;">
        <div style="font-size:11px; color:var(--text-faint); margin-bottom:3px;">
          XP: ${c.xp}/${c.xpToNextLevel}
        </div>
        ${progressBar(c.xp, c.xpToNextLevel, 'progress-xp')}
      </div>

      <!-- -- Stats principais -->
      <div class="character-stats-row">
        <div class="char-stat">
          <span class="char-stat-val" style="color:var(--red-400);">${c.attack}</span>
          <span class="char-stat-lbl">ATK</span>
        </div>
        <div class="char-stat">
          <span class="char-stat-val" style="color:var(--cyan-400);">${c.defense}</span>
          <span class="char-stat-lbl">DEF</span>
        </div>
        <div class="char-stat">
          <span class="char-stat-val" style="color:var(--purple-300);">${c.magic}</span>
          <span class="char-stat-lbl">MAG</span>
        </div>
      </div>

      <!-- -- Info adicional -->
      <div style="margin-top:10px; font-size:11px; color:var(--text-faint); display:flex; gap:12px;">
        <span>⚔️ ${c.kills} abates</span>
        <span>🗺️ ${c.adventuresCompleted} aventuras</span>
        <span>🎒 ${(c.inventory||[]).length} itens</span>
      </div>

      <!-- -- Botões de ação -->
      <div style="margin-top:14px; display:flex; gap:8px; flex-wrap:wrap;">
        <button class="btn btn-ghost btn-sm" onclick="openCharDetail('${c.id}')">
          👁️ Detalhes
        </button>
        <button class="btn btn-primary btn-sm" onclick="openGainXpModal('${c.id}', '${c.name}')">
          ⬆️ XP
        </button>
        <button class="btn btn-red btn-sm" onclick="deleteCharacter('${c.id}', '${c.name}')">
          🗑️
        </button>
      </div>
    </div>
  `).join('');
}

// ==========================================
// -- FILTRAGEM DE PERSONAGENS
// ==========================================
function filterCharacters() {
  const search    = document.getElementById('searchInput').value.toLowerCase();
  const cls       = document.getElementById('filterClass').value;
  const race      = document.getElementById('filterRace').value;
  const profileId = document.getElementById('filterProfile').value;

  const filtered = allCharacters.filter(c => {
    if (search && !c.name.toLowerCase().includes(search)) return false;
    if (cls   && c.characterClass !== cls)   return false;
    if (race  && c.race !== race)             return false;
    if (profileId && c.profileId !== profileId) return false;
    return true;
  });

  renderCharacters(filtered);
}

// ==========================================
// -- CRIAÇÃO DE PERSONAGEM
// ==========================================
async function createCharacter(e) {
  e.preventDefault();
  try {
    const char = await api.post('/api/characters/', {
      name:           document.getElementById('charName').value,
      race:           document.getElementById('charRace').value,
      characterClass: document.getElementById('charClass').value,
      profileId:      document.getElementById('charProfile').value || null,
      backstory:      document.getElementById('charBackstory').value || null,
    });

    toast.success(`Personagem "${char.name}" criado com sucesso!`);
    closeModal('createCharModal');
    document.getElementById('createCharForm').reset();
    document.getElementById('classPreview').style.display = 'none';

    // -- Recarrega a lista
    await loadCharacters();
  } catch(e) {
    toast.error(e.message);
  }
}

// -- Atualiza preview de stats ao selecionar classe
function updateClassPreview() {
  const cls     = document.getElementById('charClass').value;
  const preview = document.getElementById('classPreview');
  const row     = document.getElementById('classStatsRow');

  if (!cls || !CLASS_STATS[cls]) {
    preview.style.display = 'none';
    return;
  }

  const stats = CLASS_STATS[cls];
  preview.style.display = 'block';
  row.innerHTML = [
    { label: 'HP',  value: stats.hp,      color: 'var(--green-400)' },
    { label: 'ATK', value: stats.attack,   color: 'var(--red-400)' },
    { label: 'DEF', value: stats.defense,  color: 'var(--cyan-400)' },
    { label: 'MAG', value: stats.magic,    color: 'var(--purple-300)' },
  ].map(s => `
    <div class="char-stat">
      <span class="char-stat-val" style="color:${s.color};">${s.value}</span>
      <span class="char-stat-lbl">${s.label}</span>
    </div>
  `).join('');
}

// ==========================================
// -- DETALHES DO PERSONAGEM (MODAL)
// ==========================================
async function openCharDetail(charId) {
  openModal('charDetailModal');
  document.getElementById('charDetailContent').innerHTML =
    '<div class="loading-center"><div class="spinner"></div></div>';

  try {
    const c = await api.get(`/api/characters/${charId}`);
    document.getElementById('detailCharName').textContent =
      `${classIcon(c.characterClass)} ${c.name}`;

    // -- Busca detalhes dos itens do inventário
    let inventoryHtml = '';
    if (c.inventory && c.inventory.length > 0) {
      try {
        const allItems = await api.get('/api/items/');
        const itemMap  = {};
        allItems.forEach(it => itemMap[it.id] = it);

        inventoryHtml = `
          <div style="margin-top:16px;">
            <div style="font-family:'Cinzel',serif; font-size:13px; color:var(--text-muted); margin-bottom:8px;">
              🎒 INVENTÁRIO (${c.inventory.length} itens)
            </div>
            <div style="display:flex; flex-direction:column; gap:6px;">
              ${c.inventory.map(itemId => {
                const it = itemMap[itemId];
                if (!it) return `<div class="badge badge-comum">${itemId}</div>`;
                const equipped = Object.values(c.equippedItems || {}).includes(itemId);
                return `
                  <div style="background:var(--bg-main); border-radius:var(--radius); padding:8px 12px;
                               display:flex; align-items:center; gap:8px; font-size:13px;">
                    <span>${it.icon || '📦'}</span>
                    <span style="flex:1;">${it.name}</span>
                    <span class="${rarityBadgeClass(it.rarity)}">${it.rarity}</span>
                    ${equipped ? `<span style="font-size:11px; color:var(--green-400);">✓ Equipado</span>` : ''}
                  </div>
                `;
              }).join('')}
            </div>
          </div>`;
      } catch {}
    }

    // -- Profile info
    const profile = c.profileId ? allProfiles.find(p => p.id === c.profileId) : null;

    document.getElementById('charDetailContent').innerHTML = `
      <!-- Stats principais -->
      <div class="character-stats-row" style="grid-template-columns:repeat(4,1fr); margin-bottom:16px;">
        <div class="char-stat">
          <span class="char-stat-val" style="color:var(--red-400);">${c.attack}</span>
          <span class="char-stat-lbl">ATK</span>
        </div>
        <div class="char-stat">
          <span class="char-stat-val" style="color:var(--cyan-400);">${c.defense}</span>
          <span class="char-stat-lbl">DEF</span>
        </div>
        <div class="char-stat">
          <span class="char-stat-val" style="color:var(--purple-300);">${c.magic}</span>
          <span class="char-stat-lbl">MAG</span>
        </div>
        <div class="char-stat">
          <span class="char-stat-val" style="color:var(--gold-300);">${c.gold}</span>
          <span class="char-stat-lbl">OURO</span>
        </div>
      </div>

      <!-- Detalhes textuais -->
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; font-size:13px; margin-bottom:12px;">
        <div><span class="text-muted">Raça:</span> ${c.race}</div>
        <div><span class="text-muted">Classe:</span> ${c.characterClass}</div>
        <div><span class="text-muted">Nível:</span> ${c.level}</div>
        <div><span class="text-muted">HP:</span> ${c.hp}/${c.maxHp}</div>
        <div><span class="text-muted">XP:</span> ${c.xp}/${c.xpToNextLevel}</div>
        <div><span class="text-muted">Abates:</span> ${c.kills}</div>
        <div><span class="text-muted">Missões:</span> ${c.adventuresCompleted}</div>
        ${profile ? `<div><span class="text-muted">Perfil:</span> ${profile.avatar} ${profile.name}</div>` : ''}
      </div>

      <!-- Barras HP e XP -->
      <div style="margin-bottom:12px;">
        <div style="font-size:11px; color:var(--text-faint); margin-bottom:4px;">HP</div>
        ${progressBar(c.hp, c.maxHp, 'progress-hp')}
      </div>
      <div style="margin-bottom:12px;">
        <div style="font-size:11px; color:var(--text-faint); margin-bottom:4px;">XP para próximo nível</div>
        ${progressBar(c.xp, c.xpToNextLevel, 'progress-xp')}
      </div>

      <!-- Backstory -->
      ${c.backstory ? `
        <div style="background:var(--bg-main); border-radius:var(--radius); padding:12px; margin-bottom:12px;">
          <div style="font-size:11px; color:var(--text-faint); margin-bottom:4px; font-family:'Cinzel',serif;">HISTÓRIA</div>
          <div style="font-size:13px; color:var(--text-muted); font-style:italic; line-height:1.6;">${c.backstory}</div>
        </div>
      ` : ''}

      ${inventoryHtml}

      <!-- Criado em -->
      <div style="margin-top:16px; font-size:11px; color:var(--text-faint);">
        Criado em ${formatDate(c.createdAt)} &nbsp;·&nbsp; Atualizado em ${formatDate(c.updatedAt)}
      </div>
    `;
  } catch(e) {
    document.getElementById('charDetailContent').innerHTML =
      `<p class="text-muted">Erro ao carregar: ${e.message}</p>`;
  }
}

// ==========================================
// -- GANHAR XP (modal inline rápido)
// ==========================================
function openGainXpModal(charId, charName) {
  const amount = prompt(`Quanto XP dar para ${charName}?`, '100');
  if (!amount || isNaN(+amount)) return;
  giveXp(charId, parseInt(amount));
}

async function giveXp(charId, amount) {
  try {
    const res = await api.post(`/api/characters/${charId}/gain-xp`, { amount });
    if (res.levelUpMessages && res.levelUpMessages.length > 0) {
      res.levelUpMessages.forEach(msg => toast.success(msg));
    } else {
      toast.success(`+${amount} XP concedido!`);
    }
    await loadCharacters();
  } catch(e) {
    toast.error(e.message);
  }
}

// ==========================================
// -- DELETAR PERSONAGEM
// ==========================================
async function deleteCharacter(charId, charName) {
  if (!confirm(`Deletar "${charName}" permanentemente? Esta ação não pode ser desfeita.`)) return;
  try {
    await api.del(`/api/characters/${charId}`);
    toast.success(`Personagem "${charName}" removido.`);
    await loadCharacters();
  } catch(e) {
    toast.error(e.message);
  }
}
