
# -- Rotas da loja de itens e sistema de compra/venda
# -- Endpoint base: /api/items

from flask import Blueprint, request, jsonify
from models.item import get_catalog, get_item
from models.character import load_character, save_character

items_bp = Blueprint("items", __name__, url_prefix="/api/items")


@items_bp.route("/", methods=["GET"])
def get_items():
    """
    -- Lista itens do catálogo com filtros
    -- Query params: type, rarity, max_value, search
    """
    item_type = request.args.get("type")
    rarity    = request.args.get("rarity")
    max_value = request.args.get("max_value", type=int)
    search    = request.args.get("search")

    items = get_catalog(
        item_type=item_type,
        rarity=rarity,
        max_value=max_value,
        search=search,
    )
    return jsonify(items)


@items_bp.route("/<item_id>", methods=["GET"])
def get_item_detail(item_id: str):
    """-- Retorna detalhes de um item específico"""
    item = get_item(item_id)
    if not item:
        return jsonify({"error": f"Item '{item_id}' não encontrado."}), 404
    return jsonify(item)


@items_bp.route("/buy", methods=["POST"])
def buy_item():
    """
    -- Personagem compra um item da loja
    -- Body: { characterId: str, itemId: str }
    -- Debita o ouro e adiciona ao inventário
    """
    data      = request.get_json(silent=True) or {}
    char_id   = data.get("characterId", "").strip()
    item_id   = data.get("itemId", "").strip()

    # -- Validações
    char = load_character(char_id)
    if not char:
        return jsonify({"error": "Personagem não encontrado."}), 404

    item = get_item(item_id)
    if not item:
        return jsonify({"error": f"Item '{item_id}' não encontrado na loja."}), 404

    # -- Verifica se tem ouro suficiente
    if char.gold < item["value"]:
        return jsonify({
            "error": f"Ouro insuficiente. Você tem {char.gold}g mas o item custa {item['value']}g."
        }), 400

    # -- Realiza a compra
    char.gold -= item["value"]
    char.add_to_inventory(item_id)
    save_character(char)

    return jsonify({
        "success":   True,
        "message":   f"Você comprou '{item['name']}' por {item['value']} de ouro!",
        "character": char.to_dict(),
        "item":      item,
    })


@items_bp.route("/sell", methods=["POST"])
def sell_item():
    """
    -- Personagem vende um item do inventário
    -- Body: { characterId: str, itemId: str }
    -- Recebe 50% do valor original
    """
    data    = request.get_json(silent=True) or {}
    char_id = data.get("characterId", "").strip()
    item_id = data.get("itemId", "").strip()

    char = load_character(char_id)
    if not char:
        return jsonify({"error": "Personagem não encontrado."}), 404

    if item_id not in char.inventory:
        return jsonify({"error": "Item não está no inventário."}), 400

    item = get_item(item_id)
    if not item:
        return jsonify({"error": "Item inválido."}), 404

    # -- Vende por 50% do valor
    sell_price = max(1, item["value"] // 2)
    char.gold += sell_price
    char.remove_from_inventory(item_id)

    # -- Remove do slot equipado se estiver equipado
    slot = item.get("slot")
    if slot and char.equipped_items.get(slot) == item_id:
        del char.equipped_items[slot]

    save_character(char)
    return jsonify({
        "success":   True,
        "message":   f"Você vendeu '{item['name']}' por {sell_price} de ouro (50% do valor).",
        "character": char.to_dict(),
        "goldReceived": sell_price,
    })
