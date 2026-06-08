
// ============================================================
// -- adventures.js: Sistema de aventuras com escolhas e persistência
// -- As aventuras são salvas em arquivo JSON para continuar depois
// ============================================================

let allCharacters = [];      // -- Personagens carregados
let activeSessionId = null;  // -- Sessão de aventura atualmente ativa no modal

// ==========================================
// -- INICIALIZAÇÃO
// ==========================================
document.addEventListener('DOMContentLoaded', async () => {
  await loadCharactersForAdventures();
  loadAvailableAdventures();
});

// ==========================================
// -- ALTERNÂNCIA DE ABAS
// ==========================================
function switchAdvTab(tab) {
  ['available', 'ongoing', 'completed'].forEach(t => {
    document.getElementById(`panel-${t}`).style.display = t === tab ? 'block' : 'none';
    document.getElementById(`tab-${t}`).classList.toggle('active', t === tab);
  });

  if (tab === 'ongoing')   loadOngoingSessions();
  if (tab === 'completed') loadCompletedSessions();
}

// ==========================================
// -- CARREGAMENTO DE DADOS
// ==========================================
async function loadCharactersForAdventures() {
  try {
    allCharacters = await api.get('/api/characters/');

    // -- Preenche todos os seletores de personagem
    ['advCharSelect', 'ongoingCharSelect'].forEach(id => {
      const sel = document.getElementById(id);
      if (!sel) return;
      const placeholder = id === 'advCharSelect' ? 'Selecione um personagem' : 'Todos os personagens';
      sel.innerHTML = `<option value="">${placeholder}</option>` +
        allCharacters.map(c =>
          `<option value="${c.id}">${classIcon(c.characterClass)} ${c.name} (Nível ${c.level})</option>`
        ).join('');
    });
  } catch {}
}

async function loadAvailableAdventures() {
  const charId     = document.getElementById('advCharSelect').value;
  const difficulty = document.getElementById('advDifficulty').value;

  const list = document.getElementById('availableList');
  list.innerHTML = '<div class="loading-center" style="grid-column:1/-1;"><div class="spinner"></div></div>';

  try {
    // -- Busca aventuras com filtro de dificuldade
    let url = '/api/adventures/';
    if (difficulty) url += `?difficulty=${difficulty}`;
    const adventures = await api.get(url);

    // -- Pega nível do personagem selecionado para mostrar quais pode jogar
    let charLevel = 0;
    if (charId) {
      const char = allCharacters.find(c => c.id === charId);
      if (char) charLevel = char.level;
    }

    if (adventures.length === 0) {
      list.innerHTML = `
        <div class="empty-state" style="grid-column:1/-1;">
          <div class="empty-state-icon">🗺️</div>
          <h3>Nenhuma aventura disponível</h3>
        </div>`;
      return;
    }

    list.innerHTML = adventures.map((adv, i) => {
      const canPlay  = !charId || charLevel >= adv.minLevel;
      const lockMsg  = !charId ? 'Selecione um personagem' :
                       !canPlay ? `Requer nível ${adv.minLevel}` : '';

      return `
        <div class="adventure-card ${adv.difficulty} fade-in-up" style="animation-delay:${i*0.06}s;">
          <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:12px; margin-bottom:10px;">
            <div>
              <div class="adventure-title">${adv.title}</div>
              <div style="display:flex; gap:6px; flex-wrap:wrap; margin-top:4px;">
                <span class="difficulty-badge ${adv.difficulty}">${adv.difficulty}</span>
                <span class="badge badge-comum">Nível ${adv.minLevel}+</span>
                <span class="badge badge-comum">⏱ ${adv.estimatedTime || '20-30 min'}</span>
              </div>
            </div>
          </div>

          <div class="adventure-desc">${adv.description}</div>

          <!-- Tags -->
          <div style="display:flex; gap:6px; flex-wrap:wrap; margin-bottom:12px;">
            ${(adv.tags || []).map(t => `<span class="badge badge-raro">${t}</span>`).join('')}
          </div>

          <!-- Recompensas -->
          <div style="background:var(--bg-main); border-radius:var(--radius); padding:10px 12px; margin-bottom:12px; font-size:12px;">
            <div style="color:var(--text-faint); font-family:'Cinzel',serif; font-size:11px; margin-bottom:4px;">RECOMPENSAS</div>
            <div style="display:flex; gap:12px; flex-wrap:wrap;">
              <span>⭐ ${adv.rewards.xp} XP</span>
              <span>🪙 ${adv.rewards.gold}g</span>
              ${adv.rewards.items && adv.rewards.items.length > 0 ? `<span>📦 +${adv.rewards.items.length} item(s)</span>` : ''}
            </div>
          </div>

          <button class="btn ${canPlay && charId ? 'btn-primary' : 'btn-ghost'} w-100"
                  onclick="startAdventure('${adv.id}')"
                  ${!canPlay || !charId ? 'disabled style="opacity:0.4;"' : ''}
                  title="${lockMsg}">
            ${charId ? (canPlay ? '⚔️ Iniciar Aventura' : `🔒 Nível ${adv.minLevel} necessário`) : '🧙 Selecione um personagem'}
          </button>
        </div>
      `;
    }).join('');
  } catch(e) {
    toast.error('Erro ao carregar aventuras: ' + e.message);
  }
}

function onCharSelectChange() {
  loadAvailableAdventures();
}

// ==========================================
// -- INICIAR AVENTURA
// ==========================================
async function startAdventure(adventureId) {
  const charId = document.getElementById('advCharSelect').value;
  if (!charId) {
    toast.warning('Selecione um personagem antes de iniciar a aventura.');
    return;
  }

  try {
    const res = await api.post('/api/adventures/sessions/start', {
      adventureId,
      characterId: charId,
    });

    activeSessionId = res.session.id;
    openAdventureModal(res.adventure.title, res.session, res.currentNode);
  } catch(e) {
    toast.error(e.message);
  }
}

// ==========================================
// -- CONTINUAR AVENTURA EM ANDAMENTO
// ==========================================
async function continueAdventure(sessionId) {
  try {
    const res = await api.get(`/api/adventures/sessions/${sessionId}`);
    activeSessionId = sessionId;
    openAdventureModal(res.adventure?.title || 'Aventura', res.session, res.currentNode);
  } catch(e) {
    toast.error(e.message);
  }
}

// ==========================================
// -- MODAL DE AVENTURA ATIVA
// ==========================================
function openAdventureModal(title, session, node) {
  document.getElementById('advModalTitle').textContent = title;
  document.getElementById('advModalSubtitle').textContent =
    `XP acumulado: ${session.xpGained || 0} · Ouro acumulado: ${session.goldGained || 0}`;

  document.getElementById('advSessionInfo').textContent = `ID: ${session.id.slice(0,8)}...`;
  document.getElementById('abandonBtn').style.display = session.status === 'ongoing' ? 'flex' : 'none';

  renderAdventureNode(node, session);
  openModal('adventureModal');
}

function renderAdventureNode(node, session) {
  const panel    = document.getElementById('adventureNodePanel');
  const endPanel = document.getElementById('adventureEndPanel');

  if (session.status === 'completed' || (node && node.isEnd)) {
    panel.style.display    = 'none';
    endPanel.style.display = 'block';
    document.getElementById('abandonBtn').style.display = 'none';

    endPanel.innerHTML = `
      <div style="text-align:center; padding:20px;">
        <div style="font-size:48px; margin-bottom:12px;">🏆</div>
        <div style="font-family:'Cinzel',serif; font-size:22px; color:var(--purple-300); margin-bottom:8px;">
          ${node?.title || 'Aventura Concluída'}
        </div>
        ${node?.text ? `<p style="font-style:italic; color:var(--text-muted); line-height:1.7; margin-bottom:16px;">${node.text}</p>` : ''}
        <div style="background:var(--bg-main); border-radius:var(--radius); padding:16px; margin-bottom:20px;">
          <div style="font-family:'Cinzel',serif; font-size:12px; color:var(--text-faint); margin-bottom:8px;">RECOMPENSAS OBTIDAS</div>
          <div style="display:flex; gap:20px; justify-content:center; font-size:16px;">
            <span>⭐ <strong>${session.xpGained || 0}</strong> XP</span>
            <span>🪙 <strong>${session.goldGained || 0}</strong> ouro</span>
          </div>
        </div>
        <button class="btn btn-primary" onclick="closeModal('adventureModal'); switchAdvTab('completed');">
          Ver Aventuras Concluídas
        </button>
      </div>`;
    return;
  }

  panel.style.display    = 'block';
  endPanel.style.display = 'none';

  if (!node) {
    panel.innerHTML = '<p class="text-muted">Nó não encontrado.</p>';
    return;
  }

  // -- Pega o personagem selecionado para verificar nível nas escolhas
  const charId = document.getElementById('advCharSelect').value;
  const char   = allCharacters.find(c => c.id === (session.characterId || charId));
  const charLevel = char ? char.level : 1;

  panel.innerHTML = `
    <div class="adventure-node-panel">
      <div class="node-title">${node.title}</div>
      <div class="node-text">"${node.text}"</div>

      <div style="font-family:'Cinzel',serif; font-size:12px; color:var(--text-faint);
                  letter-spacing:1px; text-transform:uppercase; margin-bottom:10px;">
        O que você faz?
      </div>

      <div>
        ${(node.choices || []).map(choice => {
          const locked    = choice.requiresLevel && charLevel < choice.requiresLevel;
          const lockLabel = locked ? `🔒 Requer Nível ${choice.requiresLevel}` : '';
          return `
            <button class="choice-btn ${locked ? 'locked' : ''}"
                    onclick="${locked ? '' : `makeChoice('${choice.id}')`}"
                    ${locked ? 'disabled' : ''}>
              <span style="color:var(--purple-400); font-size:16px;">▶</span>
              <div>
                <div>${choice.text}</div>
                ${locked ? `<div style="font-size:11px; color:var(--red-400);">${lockLabel}</div>` :
                  choice.consequence ? `<div style="font-size:11px; color:var(--text-faint); font-style:italic;">${choice.consequence}</div>` : ''}
                ${choice.xpGain ? `<div style="font-size:11px; color:var(--purple-300);">+${choice.xpGain} XP</div>` : ''}
              </div>
            </button>
          `;
        }).join('')}
      </div>
    </div>
  `;
}

// ==========================================
// -- FAZER ESCOLHA NA AVENTURA
// ==========================================
async function makeChoice(choiceId) {
  if (!activeSessionId) return;

  // -- Desabilita todos os botões de escolha durante o carregamento
  document.querySelectorAll('.choice-btn').forEach(b => b.disabled = true);

  try {
    const res = await api.post(`/api/adventures/sessions/${activeSessionId}/choose`, {
      choiceId,
    });

    // -- Atualiza subtitle com XP acumulado
    document.getElementById('advModalSubtitle').textContent =
      `XP acumulado: ${res.session.xpGained || 0} · Ouro acumulado: ${res.session.goldGained || 0}`;

    // -- Mensagens de level up
    if (res.levelUpMessages && res.levelUpMessages.length > 0) {
      res.levelUpMessages.forEach(msg => toast.success(msg));
      // -- Atualiza personagem no array local
      if (res.character) {
        const idx = allCharacters.findIndex(c => c.id === res.character.id);
        if (idx >= 0) allCharacters[idx] = res.character;
      }
    }

    renderAdventureNode(res.currentNode, res.session);

  } catch(e) {
    toast.error(e.message);
    // -- Reabilita os botões
    document.querySelectorAll('.choice-btn').forEach(b => b.disabled = false);
  }
}

// ==========================================
// -- ABANDONAR SESSÃO
// ==========================================
async function abandonSession() {
  if (!activeSessionId) return;
  if (!confirm('Abandonar esta aventura? Você poderá iniciá-la novamente do começo.')) return;

  try {
    await api.post(`/api/adventures/sessions/${activeSessionId}/abandon`);
    toast.info('Aventura abandonada.');
    closeModal('adventureModal');
    activeSessionId = null;
    loadOngoingSessions();
  } catch(e) {
    toast.error(e.message);
  }
}

// ==========================================
// -- CARREGAR SESSÕES EM ANDAMENTO
// ==========================================
async function loadOngoingSessions() {
  const charId  = document.getElementById('ongoingCharSelect').value;
  const list    = document.getElementById('ongoingList');
  list.innerHTML = '<div class="loading-center"><div class="spinner"></div></div>';

  try {
    let url = '/api/adventures/sessions?status=ongoing';
    if (charId) url += `&character_id=${charId}`;
    const sessions = await api.get(url);

    if (sessions.length === 0) {
      list.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">📖</div>
          <h3>Nenhuma aventura em andamento</h3>
          <p>Inicie uma aventura na aba "Disponíveis".</p>
        </div>`;
      return;
    }

    list.innerHTML = `<div style="display:flex; flex-direction:column; gap:12px;">` +
      sessions.map(s => {
        const char = allCharacters.find(c => c.id === s.characterId);
        return `
          <div class="adventure-card médio">
            <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
              <div>
                <div class="adventure-title">${s.adventureTitle || 'Aventura'}</div>
                <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">
                  ${char ? `${classIcon(char.characterClass)} ${char.name}` : 'Personagem desconhecido'}
                  &nbsp;·&nbsp; XP acumulado: ${s.xpGained || 0}
                  &nbsp;·&nbsp; Salvo em: ${formatDate(s.updatedAt).split(',')[0]}
                </div>
              </div>
              <div style="display:flex; gap:8px;">
                <button class="btn btn-primary btn-sm" onclick="continueAdventure('${s.id}')">
                  ▶ Continuar
                </button>
                <button class="btn btn-red btn-sm"
                        onclick="activeSessionId='${s.id}'; abandonSession()">
                  🚪 Abandonar
                </button>
              </div>
            </div>
          </div>
        `;
      }).join('') + `</div>`;
  } catch(e) {
    toast.error('Erro ao carregar sessões: ' + e.message);
  }
}

// ==========================================
// -- CARREGAR SESSÕES CONCLUÍDAS
// ==========================================
async function loadCompletedSessions() {
  const list = document.getElementById('completedList');
  list.innerHTML = '<div class="loading-center"><div class="spinner"></div></div>';

  try {
    const sessions = await api.get('/api/adventures/sessions?status=completed');

    if (sessions.length === 0) {
      list.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">🏆</div>
          <h3>Nenhuma aventura concluída ainda</h3>
          <p>Complete aventuras para vê-las aqui!</p>
        </div>`;
      return;
    }

    list.innerHTML = `<div style="display:flex; flex-direction:column; gap:10px;">` +
      sessions.map(s => {
        const char = allCharacters.find(c => c.id === s.characterId);
        return `
          <div class="adventure-card fácil">
            <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
              <div>
                <div class="adventure-title">${s.adventureTitle || 'Aventura'}</div>
                <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">
                  ${char ? `${classIcon(char.characterClass)} ${char.name}` : 'Personagem'} &nbsp;·&nbsp;
                  ⭐ ${s.xpGained || 0} XP &nbsp;·&nbsp; 🪙 ${s.goldGained || 0}g
                  &nbsp;·&nbsp; Concluído em ${formatDate(s.updatedAt).split(',')[0]}
                </div>
              </div>
              <span class="badge badge-incomum">✓ Concluída</span>
            </div>
          </div>
        `;
      }).join('') + `</div>`;
  } catch(e) {
    toast.error('Erro ao carregar histórico: ' + e.message);
  }
}
