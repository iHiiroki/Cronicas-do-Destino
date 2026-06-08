
# -- Sistema de aventuras com nós de decisão e persistência de sessões
# -- Cada aventura é um grafo de nós com escolhas e consequências

import json
import os
import uuid
from datetime import datetime
from config import SESSION_DIR

# ==========================================
# -- CATÁLOGO DE AVENTURAS
# ==========================================

ADVENTURE_CATALOG: list[dict] = [
    # ---- Aventura 1: Caverna das Sombras (Nível 1+) ----
    {
        "id": "cave_of_shadows",
        "title": "A Caverna das Sombras",
        "description": "Uma antiga caverna nas montanhas esconde segredos sombrios. Rumores falam de um tesouro esquecido — e de algo que o guarda.",
        "minLevel": 1,
        "difficulty": "fácil",
        "estimatedTime": "20-30 min",
        "tags": ["exploração", "combate", "tesouro"],
        "rewards": {"xp": 150, "gold": 80, "items": ["health_potion"]},
        "nodes": {
            "start": {
                "id": "start",
                "title": "A Entrada da Caverna",
                "text": "Você chega à entrada de uma caverna nas montanhas Greystone. O ar que emana de dentro é frio e cheira a terra úmida. Na parede, marcas antigas — talvez de outros aventureiros. Uma tocha apagada jaz no chão. À sua direita, um caminho estreito serpenteia pela pedra.",
                "isEnd": False,
                "choices": [
                    {"id": "take_torch", "text": "Pegar a tocha e acendê-la com seu pederneiro", "consequence": "Você ilumina o caminho principal", "requiresLevel": None, "nextNodeId": "main_corridor", "xpGain": 10, "goldGain": 0},
                    {"id": "narrow_path", "text": "Explorar o caminho estreito às escuras", "consequence": "Risco maior, mas talvez uma descoberta valiosa", "requiresLevel": None, "nextNodeId": "hidden_passage", "xpGain": 15, "goldGain": 0},
                ],
            },
            "main_corridor": {
                "id": "main_corridor",
                "title": "O Corredor Principal",
                "text": "Com a tocha iluminando o caminho, você avança. Estalactites pendem do teto. Ao dobrar uma curva, encontra dois esqueletos vestindo armaduras enferrujadas — e entre eles, uma porta de pedra com um relevo de dragão.",
                "isEnd": False,
                "choices": [
                    {"id": "open_door", "text": "Abrir a porta de pedra", "consequence": None, "requiresLevel": None, "nextNodeId": "treasure_room", "xpGain": 20, "goldGain": 0},
                    {"id": "inspect_skeletons", "text": "Inspecionar os esqueletos com cuidado", "consequence": "Você pode encontrar algo útil", "requiresLevel": None, "nextNodeId": "skeleton_clue", "xpGain": 15, "goldGain": 15},
                ],
            },
            "hidden_passage": {
                "id": "hidden_passage",
                "title": "A Passagem Oculta",
                "text": "No escuro, você tateia pelas paredes até encontrar uma câmara oculta. No centro, uma arca pequena. Mas você ouve um farfalhar. Algo está aqui.",
                "isEnd": False,
                "choices": [
                    {"id": "open_chest_quietly", "text": "Abrir a arca em silêncio total", "consequence": "Tentar ser discreto", "requiresLevel": None, "nextNodeId": "chest_treasure", "xpGain": 25, "goldGain": 40},
                    {"id": "run_back", "text": "Recuar pela passagem e ir pelo corredor principal", "consequence": None, "requiresLevel": None, "nextNodeId": "main_corridor", "xpGain": 5, "goldGain": 0},
                ],
            },
            "skeleton_clue": {
                "id": "skeleton_clue",
                "title": "Pistas dos Mortos",
                "text": "Nos bolsos de um dos esqueletos você encontra uma nota parcialmente destruída: '...a chave está atrás do dragão...' e 25 moedas de ouro antigas.",
                "isEnd": False,
                "choices": [
                    {"id": "use_clue", "text": "Usar a pista e abrir a porta", "consequence": "Você sabe o que procurar", "requiresLevel": None, "nextNodeId": "treasure_room", "xpGain": 30, "goldGain": 25},
                ],
            },
            "chest_treasure": {
                "id": "chest_treasure",
                "title": "Ouro Esquecido",
                "text": "A arca contém 40 moedas de ouro, uma gema vermelha e um anel de prata. Você sai da caverna em segurança. Uma vitória discreta, mas uma vitória.",
                "isEnd": True,
                "choices": [],
                "xpGain": 50, "goldGain": 40,
            },
            "treasure_room": {
                "id": "treasure_room",
                "title": "A Sala do Tesouro",
                "text": "A porta abre revelando uma câmara iluminada por cristais bioluminescentes. No centro, um baú dourado — mas na frente dele, uma sombra se materializa. Um guardião espectral! Ele fala com voz que ressoa nas pedras: 'Prove seu valor ou vá embora.'",
                "isEnd": False,
                "choices": [
                    {"id": "fight_guardian", "text": "Lutar contra o guardião espectral", "consequence": "Combate arriscado mas recompensador", "requiresLevel": None, "nextNodeId": "victory", "xpGain": 60, "goldGain": 80},
                    {"id": "negotiate", "text": "Tentar negociar com o espectro", "consequence": "Requer sabedoria", "requiresLevel": 3, "nextNodeId": "negotiated_end", "xpGain": 80, "goldGain": 50},
                    {"id": "flee", "text": "Recuar antes que seja tarde", "consequence": "Segurança em troca do tesouro", "requiresLevel": None, "nextNodeId": "fled_end", "xpGain": 20, "goldGain": 0},
                ],
            },
            "victory": {
                "id": "victory",
                "title": "Vitória sobre as Sombras",
                "text": "Após uma batalha épica, o guardião se dissolve em névoa escura. O baú está aberto. Dentro: ouro reluzente, joias e um amuleto encantado. Você sai da caverna como um herói.",
                "isEnd": True,
                "choices": [],
                "xpGain": 80, "goldGain": 80,
            },
            "negotiated_end": {
                "id": "negotiated_end",
                "title": "Sabedoria Recompensada",
                "text": "O espectro sorri. 'Poucos têm a sabedoria de falar antes de agir.' Ele se dissolve voluntariamente, deixando o tesouro para você. Uma vitória elegante.",
                "isEnd": True,
                "choices": [],
                "xpGain": 100, "goldGain": 50,
            },
            "fled_end": {
                "id": "fled_end",
                "title": "Recuo Estratégico",
                "text": "Você sai da caverna são e salvo. O tesouro permanece intocado por hoje. Mas você conhece o caminho — e voltará mais forte.",
                "isEnd": True,
                "choices": [],
                "xpGain": 20, "goldGain": 0,
            },
        },
    },

    # ---- Aventura 2: Floresta dos Espíritos (Nível 3+) ----
    {
        "id": "spirit_forest",
        "title": "A Floresta dos Espíritos",
        "description": "Uma floresta encantada onde os espíritos dos mortos vagam eternamente. Uma aldeia pede sua ajuda para descobrir por que os espíritos ficaram agressivos.",
        "minLevel": 3,
        "difficulty": "médio",
        "estimatedTime": "30-45 min",
        "tags": ["mistério", "magia", "espíritos"],
        "rewards": {"xp": 300, "gold": 150, "items": ["great_potion", "shadow_cloak"]},
        "nodes": {
            "start": {
                "id": "start",
                "title": "A Beira da Floresta",
                "text": "A floresta de Elmsorrow sempre foi sombria, mas pacífica. Agora os aldeões fogem dela com pavor. Você está na entrada — árvores antigas fecham o céu, e sussurros parecem vir de todo lugar.",
                "isEnd": False,
                "choices": [
                    {"id": "enter_carefully", "text": "Entrar com cautela, observando tudo", "consequence": "Abordagem sábia", "requiresLevel": None, "nextNodeId": "forest_path", "xpGain": 15, "goldGain": 0},
                    {"id": "call_spirits", "text": "Chamar os espíritos em voz alta", "consequence": "Pode atraí-los imediatamente", "requiresLevel": 4, "nextNodeId": "spirit_meeting", "xpGain": 25, "goldGain": 0},
                ],
            },
            "forest_path": {
                "id": "forest_path",
                "title": "O Caminho dos Sussurros",
                "text": "Entre as árvores, você encontra um altar antigo profanado. Símbolos foram riscados e substituídos por runas desconhecidas. Perto dali, um anel de cogumelos — um círculo feérico.",
                "isEnd": False,
                "choices": [
                    {"id": "study_altar", "text": "Examinar o altar profanado", "consequence": "Descobrir a causa da perturbação", "requiresLevel": None, "nextNodeId": "altar_discovery", "xpGain": 30, "goldGain": 0},
                    {"id": "enter_circle", "text": "Entrar no círculo feérico", "consequence": "Contato direto com o plano espiritual", "requiresLevel": None, "nextNodeId": "fairy_realm", "xpGain": 40, "goldGain": 0},
                ],
            },
            "spirit_meeting": {
                "id": "spirit_meeting",
                "title": "O Encontro dos Espíritos",
                "text": "Dezenas de luzes aparecem ao seu redor. Os espíritos respondem ao seu chamado — e estão furiosos. Um deles, maior que os outros, se aproxima. 'Vingança. Aquele que profanou nosso lar.'",
                "isEnd": False,
                "choices": [
                    {"id": "promise_help", "text": "Prometer encontrar o culpado e fazer justiça", "consequence": "Os espíritos confiam em você", "requiresLevel": None, "nextNodeId": "altar_discovery", "xpGain": 35, "goldGain": 0},
                    {"id": "fight_spirits", "text": "Lutar contra os espíritos furiosos", "consequence": "Combate difícil", "requiresLevel": None, "nextNodeId": "spirit_combat_won", "xpGain": 80, "goldGain": 0},
                ],
            },
            "altar_discovery": {
                "id": "altar_discovery",
                "title": "O Culpado Revelado",
                "text": "As runas são de um culto de necromancia. Um símbolo no altar — é o emblema de uma guilda mercante da cidade próxima. Eles perturbaram o altar para usar a floresta como rota de contrabando.",
                "isEnd": False,
                "choices": [
                    {"id": "purify_altar", "text": "Purificar o altar e restaurar a paz", "consequence": "Resolver pelo lado espiritual", "requiresLevel": None, "nextNodeId": "peaceful_end", "xpGain": 100, "goldGain": 150},
                    {"id": "go_to_city", "text": "Ir à cidade confrontar a guilda", "consequence": "Resolver pelo lado humano", "requiresLevel": 5, "nextNodeId": "guild_confrontation", "xpGain": 120, "goldGain": 100},
                ],
            },
            "fairy_realm": {
                "id": "fairy_realm",
                "title": "O Reino das Fadas",
                "text": "O círculo o transporta para um espaço entre mundos. Uma fada anciã o observa. 'Você veio para restaurar o equilíbrio? Poucos humanos têm essa coragem.' Ela oferece conhecimento.",
                "isEnd": False,
                "choices": [
                    {"id": "accept_fae_help", "text": "Aceitar a ajuda da fada", "consequence": "Aliança valiosa", "requiresLevel": None, "nextNodeId": "peaceful_end", "xpGain": 120, "goldGain": 100},
                ],
            },
            "spirit_combat_won": {
                "id": "spirit_combat_won",
                "title": "Espíritos Derrotados",
                "text": "Após um combate devastador, os espíritos se dispersam — mas não em paz. A floresta fica em silêncio pesado. Você sobreviveu, mas a causa raiz permanece.",
                "isEnd": True,
                "choices": [],
                "xpGain": 80, "goldGain": 0,
            },
            "peaceful_end": {
                "id": "peaceful_end",
                "title": "Paz Restaurada",
                "text": "O altar purificado brilha com luz dourada. Os espíritos se aquietam, e a floresta recupera sua paz antiga. A aldeia celebra sua vitória com um banquete e generosas recompensas.",
                "isEnd": True,
                "choices": [],
                "xpGain": 120, "goldGain": 150,
            },
            "guild_confrontation": {
                "id": "guild_confrontation",
                "title": "Confronto na Guilda",
                "text": "Na cidade, você apresenta as evidências. O líder da guilda tenta suborná-lo, mas você recusa. Preso e processado, ele é condenado. A aldeia e os espíritos descansam em paz.",
                "isEnd": True,
                "choices": [],
                "xpGain": 140, "goldGain": 100,
            },
        },
    },

    # ---- Aventura 3: A Torre do Arquimago (Nível 5+) ----
    {
        "id": "archmage_tower",
        "title": "A Torre do Arquimago",
        "description": "Um arquimago louco ameaça invocar uma entidade do plano das sombras. Você deve infiltrar sua torre e detê-lo — ou pagar o preço com o mundo.",
        "minLevel": 5,
        "difficulty": "difícil",
        "estimatedTime": "45-60 min",
        "tags": ["magia", "boss", "decisão moral"],
        "rewards": {"xp": 600, "gold": 400, "items": ["tome_of_power", "elixir_eternity"]},
        "nodes": {
            "start": {
                "id": "start",
                "title": "Aos Pés da Torre",
                "text": "A Torre de Krath'ul rasga o céu. Raios de energia violeta pulsam do topo. Você tem poucas horas antes que o ritual seja concluído. A porta principal está trancada, mas há uma janela aberta no segundo andar.",
                "isEnd": False,
                "choices": [
                    {"id": "climb_window", "text": "Escalar para a janela aberta", "consequence": "Entrada furtiva", "requiresLevel": None, "nextNodeId": "second_floor", "xpGain": 20, "goldGain": 0},
                    {"id": "break_door", "text": "Arrombar a porta principal com força", "consequence": "Entrada barulhenta", "requiresLevel": None, "nextNodeId": "main_hall", "xpGain": 15, "goldGain": 0},
                    {"id": "find_weakness", "text": "Estudar a torre em busca de uma fraqueza mágica", "consequence": "Requer conhecimento arcano", "requiresLevel": 6, "nextNodeId": "arcane_weakness", "xpGain": 30, "goldGain": 0},
                ],
            },
            "second_floor": {
                "id": "second_floor",
                "title": "O Laboratório",
                "text": "Você entra no laboratório do arquimago. Poções borbulham, fórmulas cobrem as paredes. Uma golem de pedra patrulha — mas está distraída. E há um grimório aberto com o plano do ritual.",
                "isEnd": False,
                "choices": [
                    {"id": "steal_grimoire", "text": "Pegar o grimório para interromper o ritual", "consequence": "Pode alertar proteções mágicas", "requiresLevel": None, "nextNodeId": "grimoire_trap", "xpGain": 40, "goldGain": 0},
                    {"id": "sneak_past_golem", "text": "Contornar o golem em silêncio e subir", "consequence": "Chegar ao arquimago diretamente", "requiresLevel": None, "nextNodeId": "final_chamber", "xpGain": 35, "goldGain": 0},
                ],
            },
            "main_hall": {
                "id": "main_hall",
                "title": "O Grande Salão",
                "text": "O salão está cheio de armadilhas mágicas e gargantas criadas pelo arquimago. Você precisa cruzá-lo. À esquerda, uma escadaria. À direita, um corredor escuro.",
                "isEnd": False,
                "choices": [
                    {"id": "take_stairs", "text": "Subir pela escadaria diretamente", "consequence": "Caminho óbvio mas perigoso", "requiresLevel": None, "nextNodeId": "trap_gauntlet", "xpGain": 25, "goldGain": 0},
                    {"id": "dark_corridor", "text": "Explorar o corredor escuro", "consequence": "Caminho alternativo", "requiresLevel": None, "nextNodeId": "second_floor", "xpGain": 30, "goldGain": 0},
                ],
            },
            "arcane_weakness": {
                "id": "arcane_weakness",
                "title": "A Falha no Escudo",
                "text": "Você identifica um ponto de ressonância mágica na fundação da torre. Uma explosão controlada ali derrubaria o campo de força do ritual — mas arriscaria destruir parte da torre.",
                "isEnd": False,
                "choices": [
                    {"id": "detonate", "text": "Detonar o ponto de ressonância", "consequence": "Solução radical e perigosa", "requiresLevel": None, "nextNodeId": "chaos_end", "xpGain": 100, "goldGain": 100},
                    {"id": "infiltrate_anyway", "text": "Usar o conhecimento para infiltrar com segurança", "consequence": "Abordagem inteligente", "requiresLevel": None, "nextNodeId": "final_chamber", "xpGain": 60, "goldGain": 0},
                ],
            },
            "grimoire_trap": {
                "id": "grimoire_trap",
                "title": "A Armadilha do Grimório",
                "text": "O grimório estava armadilhado! Uma descarga de energia te acerta — 20 HP de dano. Mas você tem o livro. Com ele, pode desmantelar o ritual de baixo. O golem te persegue pelas escadas.",
                "isEnd": False,
                "choices": [
                    {"id": "run_to_top", "text": "Correr ao topo antes do golem te alcançar", "consequence": "Uma corrida contra o tempo", "requiresLevel": None, "nextNodeId": "final_chamber", "xpGain": 50, "goldGain": 0},
                ],
            },
            "trap_gauntlet": {
                "id": "trap_gauntlet",
                "title": "O Corredor das Armadilhas",
                "text": "Raios, dardos mágicos e portais instáveis. Você atravessa perdendo 15 HP mas chegando ao topo. O arquimago está logo acima.",
                "isEnd": False,
                "choices": [
                    {"id": "enter_final", "text": "Entrar na câmara final", "consequence": None, "requiresLevel": None, "nextNodeId": "final_chamber", "xpGain": 40, "goldGain": 0},
                ],
            },
            "final_chamber": {
                "id": "final_chamber",
                "title": "A Câmara do Ritual",
                "text": "Krath'ul está no centro de um pentagrama de energia pura. A entidade das sombras está meio materializada. Ele te vê e ri. 'Tarde demais. A não ser... que você queira juntar-se a mim?'",
                "isEnd": False,
                "choices": [
                    {"id": "fight_archmage", "text": "Lutar contra Krath'ul e destruir o ritual", "consequence": "Combate de boss épico", "requiresLevel": None, "nextNodeId": "hero_end", "xpGain": 200, "goldGain": 400},
                    {"id": "join_archmage", "text": "Aceitar a oferta e virar seu aliado (fim sombrio)", "consequence": "Escolha moral radical", "requiresLevel": None, "nextNodeId": "dark_end", "xpGain": 150, "goldGain": 600},
                    {"id": "destroy_seal", "text": "Destruir o selo do pentagrama em vez de lutar", "consequence": "Requer nível alto", "requiresLevel": 7, "nextNodeId": "clever_end", "xpGain": 250, "goldGain": 350},
                ],
            },
            "hero_end": {
                "id": "hero_end",
                "title": "O Herói Triunfa",
                "text": "Após um combate devastador, Krath'ul cai. O ritual se desfaz com uma explosão de luz. A entidade é banida. Você está de pé nos escombros — exausto, mas vitorioso. O mundo está salvo.",
                "isEnd": True,
                "choices": [],
                "xpGain": 200, "goldGain": 400,
            },
            "dark_end": {
                "id": "dark_end",
                "title": "A Queda do Herói",
                "text": "Você aceita o poder das sombras. A entidade é invocada — e você se torna seu campeão. Poder inimaginável, mas a que custo? A escuridão agora vive em você.",
                "isEnd": True,
                "choices": [],
                "xpGain": 150, "goldGain": 600,
            },
            "clever_end": {
                "id": "clever_end",
                "title": "A Solução Elegante",
                "text": "Você destrói o selo antes de Krath'ul perceber. O ritual implode, suga a entidade de volta e aprisionaKrath'ul entre dimensões. A torre colapsa parcialmente. Você sai pelos escombros sorrindo.",
                "isEnd": True,
                "choices": [],
                "xpGain": 250, "goldGain": 350,
            },
            "chaos_end": {
                "id": "chaos_end",
                "title": "Fim Caótico",
                "text": "A explosão derruba o campo de força — e metade da torre. Krath'ul foge, mas o ritual é interrompido. A cidade próxima viu a explosão. Você é aclamado como herói louco.",
                "isEnd": True,
                "choices": [],
                "xpGain": 100, "goldGain": 200,
            },
        },
    },
]

# -- Índice rápido por ID
_ADVENTURE_INDEX: dict[str, dict] = {a["id"]: a for a in ADVENTURE_CATALOG}


def get_adventure(adventure_id: str) -> dict | None:
    """-- Retorna dados de uma aventura pelo ID"""
    return _ADVENTURE_INDEX.get(adventure_id)


def list_adventures(min_level: int | None = None, difficulty: str | None = None) -> list[dict]:
    """-- Lista aventuras disponíveis com filtros opcionais"""
    adventures = list(ADVENTURE_CATALOG)
    if min_level is not None:
        adventures = [a for a in adventures if a["minLevel"] <= min_level]
    if difficulty:
        adventures = [a for a in adventures if a["difficulty"] == difficulty]
    # -- Retorna sem os nós internos (resumo apenas)
    return [{k: v for k, v in a.items() if k != "nodes"} for a in adventures]


# ==========================================
# -- SESSÕES DE AVENTURA (PERSISTÊNCIA)
# ==========================================

def _ensure_dirs():
    """-- Garante que o diretório de sessões existe"""
    os.makedirs(SESSION_DIR, exist_ok=True)


def _session_path(session_id: str) -> str:
    """-- Caminho do arquivo JSON de uma sessão"""
    return os.path.join(SESSION_DIR, f"{session_id}.json")


def create_session(adventure_id: str, character_id: str) -> dict:
    """
    -- Cria uma nova sessão de aventura para um personagem
    -- Retorna o dicionário da sessão criada
    """
    _ensure_dirs()
    adventure = get_adventure(adventure_id)
    if not adventure:
        raise ValueError(f"Aventura '{adventure_id}' não encontrada.")

    now = datetime.now().isoformat()
    session = {
        "id":           str(uuid.uuid4()),
        "adventureId":  adventure_id,
        "characterId":  character_id,
        "currentNodeId": "start",
        "status":       "ongoing",   # -- ongoing | completed | failed
        "history":      [],          # -- Lista de node IDs visitados
        "choicesMade":  [],          # -- Histórico de escolhas
        "xpGained":     0,
        "goldGained":   0,
        "createdAt":    now,
        "updatedAt":    now,
    }

    save_session(session)
    return session


def save_session(session: dict) -> None:
    """-- Salva sessão de aventura em arquivo JSON"""
    _ensure_dirs()
    session["updatedAt"] = datetime.now().isoformat()
    with open(_session_path(session["id"]), "w", encoding="utf-8") as f:
        json.dump(session, f, ensure_ascii=False, indent=2)


def load_session(session_id: str) -> dict | None:
    """-- Carrega sessão do arquivo JSON"""
    path = _session_path(session_id)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_sessions(character_id: str | None = None, status: str | None = None) -> list[dict]:
    """
    -- Lista todas as sessões salvas
    -- character_id: filtrar por personagem
    -- status: filtrar por estado (ongoing, completed, failed)
    """
    _ensure_dirs()
    sessions = []
    for fname in os.listdir(SESSION_DIR):
        if not fname.endswith(".json"):
            continue
        session = load_session(fname[:-5])
        if session:
            if character_id and session.get("characterId") != character_id:
                continue
            if status and session.get("status") != status:
                continue
            sessions.append(session)
    # -- Ordena por data de atualização (mais recente primeiro)
    return sorted(sessions, key=lambda s: s.get("updatedAt", ""), reverse=True)


def advance_session(session: dict, choice_id: str, character) -> tuple[dict, dict]:
    """
    -- Avança a aventura com base na escolha feita
    -- Retorna (sessão_atualizada, nó_atual)
    -- Lança ValueError se a escolha for inválida
    """
    adventure   = get_adventure(session["adventureId"])
    current_id  = session["currentNodeId"]
    current_node = adventure["nodes"].get(current_id)

    if not current_node:
        raise ValueError(f"Nó '{current_id}' não encontrado.")

    # -- Encontra a escolha pelo ID
    choice = next((c for c in current_node.get("choices", []) if c["id"] == choice_id), None)
    if not choice:
        raise ValueError(f"Escolha '{choice_id}' não encontrada neste nó.")

    # -- Verifica requisito de nível
    if choice.get("requiresLevel") and character.level < choice["requiresLevel"]:
        raise ValueError(f"Requer nível {choice['requiresLevel']}. Seu personagem é nível {character.level}.")

    # -- Recompensas da escolha
    xp_gain   = choice.get("xpGain", 0)
    gold_gain = choice.get("goldGain", 0)

    # -- Atualiza a sessão
    session["history"].append(current_id)
    session["choicesMade"].append({"nodeId": current_id, "choiceId": choice_id})
    session["xpGained"]  = session.get("xpGained", 0) + xp_gain
    session["goldGained"] = session.get("goldGained", 0) + gold_gain

    next_node_id = choice.get("nextNodeId")
    if next_node_id:
        next_node = adventure["nodes"].get(next_node_id)
        session["currentNodeId"] = next_node_id

        # -- Verifica se chegou ao fim
        if next_node and (next_node.get("isEnd") or choice.get("isEnd")):
            session["status"]    = "completed"
            session["xpGained"]  += next_node.get("xpGain", 0)
            session["goldGained"] += next_node.get("goldGain", 0)
            # -- Adiciona recompensas da aventura completa
            adventure_rewards = adventure.get("rewards", {})
            session["xpGained"]  += adventure_rewards.get("xp", 0)
            session["goldGained"] += adventure_rewards.get("gold", 0)
    else:
        session["status"] = "completed"

    save_session(session)
    return session, adventure["nodes"].get(session["currentNodeId"], current_node)
