
# -- Rotas de personagens: CRUD completo com filtragem
# -- Endpoint base: /api/characters

from flask import Blueprint, request, jsonify
from models.character import Character, save_character, load_character, list_characters, delete_character
from config import CLASS_STATS, VALID_RACES

characters_bp = Blueprint("characters", __name__, url_prefix="/api/characters")

# -- Classes válidas extraídas do dicionário de stats
VALID_CLASSES = list(CLASS_STATS.keys())


@characters_bp.route("/", methods=["GET"])
def get_characters():
    """
    -- Lista personagens com filtros opcionais
    -- Query params: class, race, min_level, max_level, profile_id, search
    """
    chars = list_characters()

    # -- Filtro por classe
    class_filter = request.args.get("class")
    if class_filter:
        chars = [c for c in chars if c.character_class == class_filter]

    # -- Filtro por raça
    race_filter = request.args.get("race")
    if race_filter:
        chars = [c for c in chars if c.race == race_filter]

    # -- Filtro por nível mínimo
    min_level = request.args.get("min_level", type=int)
    if min_level:
        chars = [c for c in chars if c.level >= min_level]

    # -- Filtro por nível máximo
    max_level = request.args.get("max_level", type=int)
    if max_level:
        chars = [c for c in chars if c.level <= max_level]

    # -- Filtro por perfil
    profile_id = request.args.get("profile_id")
    if profile_id:
        chars = [c for c in chars if c.profile_id == profile_id]

    # -- Busca por nome
    search = request.args.get("search", "").lower()
    if search:
        chars = [c for c in chars if search in c.name.lower()]

    return jsonify([c.to_dict() for c in chars])


@characters_bp.route("/", methods=["POST"])
def create_character():
    """
    -- Cria um novo personagem
    -- Body: { name, race, characterClass, backstory?, profileId? }
    """
    data = request.get_json(silent=True) or {}

    # -- Validações obrigatórias
    name  = (data.get("name") or "").strip()
    race  = data.get("race", "").strip()
    klass = data.get("characterClass", "").strip()

    if not name:
        return jsonify({"error": "Nome é obrigatório."}), 400
    if len(name) > 50:
        return jsonify({"error": "Nome deve ter no máximo 50 caracteres."}), 400
    if race not in VALID_RACES:
        return jsonify({"error": f"Raça inválida. Escolha: {', '.join(VALID_RACES)}"}), 400
    if klass not in VALID_CLASSES:
        return jsonify({"error": f"Classe inválida. Escolha: {', '.join(VALID_CLASSES)}"}), 400

    char = Character({
        "name":           name,
        "race":           race,
        "characterClass": klass,
        "backstory":      data.get("backstory"),
        "profileId":      data.get("profileId"),
    })
    save_character(char)
    return jsonify(char.to_dict()), 201


@characters_bp.route("/<char_id>", methods=["GET"])
def get_character(char_id: str):
    """-- Retorna um personagem específico pelo ID"""
    char = load_character(char_id)
    if not char:
        return jsonify({"error": "Personagem não encontrado."}), 404
    return jsonify(char.to_dict())


@characters_bp.route("/<char_id>", methods=["PATCH"])
def update_character(char_id: str):
    """
    -- Atualiza campos do personagem (hp, gold, xp, kills, adventuresCompleted, backstory, profileId)
    -- Gain XP automaticamente sobe de nível se necessário
    """
    char = load_character(char_id)
    if not char:
        return jsonify({"error": "Personagem não encontrado."}), 404

    data     = request.get_json(silent=True) or {}
    messages = []

    # -- HP: clampado entre 0 e maxHp
    if "hp" in data and data["hp"] is not None:
        char.hp = max(0, min(char.max_hp, int(data["hp"])))

    # -- Ouro: não pode ser negativo
    if "gold" in data and data["gold"] is not None:
        char.gold = max(0, int(data["gold"]))

    # -- XP: usa gain_xp para lidar com level up
    if "xp" in data and data["xp"] is not None:
        xp_gain = int(data["xp"]) - char.xp
        if xp_gain > 0:
            messages = char.gain_xp(xp_gain)

    # -- Kills e aventuras completadas
    if "kills" in data and data["kills"] is not None:
        char.kills = max(0, int(data["kills"]))
    if "adventuresCompleted" in data and data["adventuresCompleted"] is not None:
        char.adventures_completed = max(0, int(data["adventuresCompleted"]))

    # -- Backstory e perfil
    if "backstory" in data:
        char.backstory = data["backstory"]
    if "profileId" in data:
        char.profile_id = data["profileId"]

    save_character(char)
    return jsonify({"character": char.to_dict(), "messages": messages})


@characters_bp.route("/<char_id>/gain-xp", methods=["POST"])
def gain_xp(char_id: str):
    """
    -- Adiciona XP ao personagem (pode causar level up)
    -- Body: { amount: int }
    """
    char = load_character(char_id)
    if not char:
        return jsonify({"error": "Personagem não encontrado."}), 404

    data   = request.get_json(silent=True) or {}
    amount = int(data.get("amount", 0))
    if amount <= 0:
        return jsonify({"error": "Quantidade de XP deve ser positiva."}), 400

    messages = char.gain_xp(amount)
    save_character(char)
    return jsonify({"character": char.to_dict(), "levelUpMessages": messages})


@characters_bp.route("/<char_id>/inventory", methods=["POST"])
def add_item(char_id: str):
    """
    -- Adiciona item ao inventário do personagem
    -- Body: { itemId: str }
    """
    from models.item import get_item
    char = load_character(char_id)
    if not char:
        return jsonify({"error": "Personagem não encontrado."}), 404

    data    = request.get_json(silent=True) or {}
    item_id = data.get("itemId", "").strip()
    item    = get_item(item_id)
    if not item:
        return jsonify({"error": f"Item '{item_id}' não encontrado."}), 404

    char.add_to_inventory(item_id)
    save_character(char)
    return jsonify(char.to_dict())


@characters_bp.route("/<char_id>/inventory/<item_id>", methods=["DELETE"])
def remove_item(char_id: str, item_id: str):
    """-- Remove item do inventário do personagem"""
    char = load_character(char_id)
    if not char:
        return jsonify({"error": "Personagem não encontrado."}), 404

    removed = char.remove_from_inventory(item_id)
    if not removed:
        return jsonify({"error": "Item não encontrado no inventário."}), 404

    save_character(char)
    return jsonify(char.to_dict())


@characters_bp.route("/<char_id>/equip", methods=["POST"])
def equip_item(char_id: str):
    """
    -- Equipa um item de inventário em um slot
    -- Body: { itemId: str, slot: str }
    """
    from models.item import get_item
    char = load_character(char_id)
    if not char:
        return jsonify({"error": "Personagem não encontrado."}), 404

    data    = request.get_json(silent=True) or {}
    item_id = data.get("itemId", "").strip()
    slot    = data.get("slot", "").strip()

    if item_id not in char.inventory:
        return jsonify({"error": "Item não está no inventário."}), 400

    item = get_item(item_id)
    if not item:
        return jsonify({"error": "Item inválido."}), 404

    # -- Usa o slot do item se não especificado
    slot = slot or item.get("slot") or "misc"
    char.equip_item(item_id, slot)
    save_character(char)
    return jsonify(char.to_dict())


@characters_bp.route("/<char_id>", methods=["DELETE"])
def delete_char(char_id: str):
    """-- Remove permanentemente o personagem"""
    deleted = delete_character(char_id)
    if not deleted:
        return jsonify({"error": "Personagem não encontrado."}), 404
    return jsonify({"success": True, "message": "Personagem deletado."})


@characters_bp.route("/options", methods=["GET"])
def get_options():
    """-- Retorna opções válidas de raças, classes e seus stats base"""
    return jsonify({
        "races":   VALID_RACES,
        "classes": [
            {"name": name, "stats": stats}
            for name, stats in CLASS_STATS.items()
        ],
    })
