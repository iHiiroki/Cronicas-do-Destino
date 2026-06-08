
# -- Rotas de aventuras: listagem, sessões e progresso
# -- Endpoint base: /api/adventures

from flask import Blueprint, request, jsonify
from models.adventure import (
    list_adventures, get_adventure,
    create_session, load_session, list_sessions, save_session, advance_session,
)
from models.character import load_character, save_character

adventures_bp = Blueprint("adventures", __name__, url_prefix="/api/adventures")


@adventures_bp.route("/", methods=["GET"])
def get_adventures():
    """
    -- Lista aventuras disponíveis
    -- Query params: min_level, difficulty
    """
    min_level  = request.args.get("min_level", type=int)
    difficulty = request.args.get("difficulty")
    adventures = list_adventures(min_level=min_level, difficulty=difficulty)
    return jsonify(adventures)


@adventures_bp.route("/<adventure_id>", methods=["GET"])
def get_adventure_detail(adventure_id: str):
    """-- Retorna detalhes completos de uma aventura (incluindo nós de decisão)"""
    adventure = get_adventure(adventure_id)
    if not adventure:
        return jsonify({"error": "Aventura não encontrada."}), 404
    # -- Retorna sem os nós internos (segurança - cliente não vê o futuro)
    summary = {k: v for k, v in adventure.items() if k != "nodes"}
    return jsonify(summary)


# ==========================================
# -- SESSÕES DE AVENTURA
# ==========================================

@adventures_bp.route("/sessions", methods=["GET"])
def get_sessions():
    """
    -- Lista sessões de aventura com filtros
    -- Query params: character_id, status (ongoing | completed | failed)
    """
    char_id = request.args.get("character_id")
    status  = request.args.get("status")
    sessions = list_sessions(character_id=char_id, status=status)

    # -- Enriquece cada sessão com título da aventura
    enriched = []
    for s in sessions:
        adv = get_adventure(s.get("adventureId", ""))
        enriched.append({
            **s,
            "adventureTitle": adv["title"] if adv else "Aventura desconhecida",
            "adventureDifficulty": adv["difficulty"] if adv else "",
        })
    return jsonify(enriched)


@adventures_bp.route("/sessions/<session_id>", methods=["GET"])
def get_session(session_id: str):
    """-- Retorna estado atual de uma sessão, incluindo o nó atual"""
    session = load_session(session_id)
    if not session:
        return jsonify({"error": "Sessão não encontrada."}), 404

    adventure    = get_adventure(session["adventureId"])
    current_node = adventure["nodes"].get(session["currentNodeId"]) if adventure else None

    return jsonify({
        "session":     session,
        "currentNode": current_node,
        "adventure":   {k: v for k, v in adventure.items() if k != "nodes"} if adventure else None,
    })


@adventures_bp.route("/sessions/start", methods=["POST"])
def start_session():
    """
    -- Inicia uma nova sessão de aventura
    -- Body: { adventureId: str, characterId: str }
    """
    data         = request.get_json(silent=True) or {}
    adventure_id = data.get("adventureId", "").strip()
    char_id      = data.get("characterId", "").strip()

    # -- Validações
    char = load_character(char_id)
    if not char:
        return jsonify({"error": "Personagem não encontrado."}), 404

    adventure = get_adventure(adventure_id)
    if not adventure:
        return jsonify({"error": "Aventura não encontrada."}), 404

    # -- Verifica nível mínimo
    if char.level < adventure["minLevel"]:
        return jsonify({
            "error": f"Nível insuficiente. Esta aventura requer nível {adventure['minLevel']}. "
                     f"Seu personagem é nível {char.level}."
        }), 400

    try:
        session      = create_session(adventure_id, char_id)
        start_node   = adventure["nodes"]["start"]
        return jsonify({
            "session":     session,
            "currentNode": start_node,
            "adventure":   {k: v for k, v in adventure.items() if k != "nodes"},
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@adventures_bp.route("/sessions/<session_id>/choose", methods=["POST"])
def make_choice(session_id: str):
    """
    -- Faz uma escolha na aventura atual
    -- Body: { choiceId: str }
    -- Retorna a sessão atualizada e o novo nó
    """
    session = load_session(session_id)
    if not session:
        return jsonify({"error": "Sessão não encontrada."}), 404

    if session["status"] != "ongoing":
        return jsonify({"error": "Esta aventura já foi concluída."}), 400

    data      = request.get_json(silent=True) or {}
    choice_id = data.get("choiceId", "").strip()
    if not choice_id:
        return jsonify({"error": "choiceId é obrigatório."}), 400

    # -- Carrega o personagem para verificar nível
    char = load_character(session["characterId"])
    if not char:
        return jsonify({"error": "Personagem da sessão não encontrado."}), 404

    try:
        updated_session, current_node = advance_session(session, choice_id, char)

        # -- Se a aventura foi concluída, aplica recompensas ao personagem
        level_up_messages = []
        if updated_session["status"] == "completed":
            xp_total   = updated_session.get("xpGained", 0)
            gold_total  = updated_session.get("goldGained", 0)

            if xp_total > 0:
                level_up_messages = char.gain_xp(xp_total)
            if gold_total > 0:
                char.gold += gold_total

            char.adventures_completed += 1
            save_character(char)

        return jsonify({
            "session":          updated_session,
            "currentNode":      current_node,
            "character":        char.to_dict() if updated_session["status"] == "completed" else None,
            "levelUpMessages":  level_up_messages,
            "completed":        updated_session["status"] == "completed",
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@adventures_bp.route("/sessions/<session_id>/abandon", methods=["POST"])
def abandon_session(session_id: str):
    """-- Abandona uma sessão em andamento"""
    session = load_session(session_id)
    if not session:
        return jsonify({"error": "Sessão não encontrada."}), 404

    if session["status"] != "ongoing":
        return jsonify({"error": "Sessão já finalizada."}), 400

    session["status"] = "failed"
    save_session(session)
    return jsonify({"success": True, "session": session})
