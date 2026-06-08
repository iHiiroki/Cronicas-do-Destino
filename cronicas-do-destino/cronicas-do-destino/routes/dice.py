
# -- Rotas do motor de dados
# -- Endpoint base: /api/dice

from flask import Blueprint, request, jsonify
from models.dice import roll, roll_attack, roll_damage, get_history, clear_history

dice_bp = Blueprint("dice", __name__, url_prefix="/api/dice")


@dice_bp.route("/roll", methods=["POST"])
def roll_dice():
    """
    -- Rola dados com notação padrão (ex: 2d6+3)
    -- Body: { notation: str, label?: str }
    """
    data     = request.get_json(silent=True) or {}
    notation = data.get("notation", "").strip()
    label    = data.get("label", "")

    if not notation:
        return jsonify({"error": "Notação de dado é obrigatória. Ex: '2d6', '1d20+3'"}), 400

    try:
        result = roll(notation, label)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@dice_bp.route("/roll-attack", methods=["POST"])
def roll_attack_route():
    """
    -- Rolagem de ataque: 1d20 com bônus
    -- Body: { bonus?: int, label?: str }
    """
    data  = request.get_json(silent=True) or {}
    bonus = int(data.get("bonus", 0))
    label = data.get("label", "Ataque")

    result = roll_attack(bonus=bonus, label=label)
    return jsonify(result)


@dice_bp.route("/roll-damage", methods=["POST"])
def roll_damage_route():
    """
    -- Rolagem de dano com dado de arma
    -- Body: { weaponDie?: str, bonus?: int, label?: str }
    """
    data       = request.get_json(silent=True) or {}
    weapon_die = data.get("weaponDie", "1d8")
    bonus      = int(data.get("bonus", 0))
    label      = data.get("label", "Dano")

    try:
        result = roll_damage(weapon_die=weapon_die, bonus=bonus, label=label)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@dice_bp.route("/history", methods=["GET"])
def get_roll_history():
    """-- Retorna o histórico de rolagens da sessão atual"""
    return jsonify(get_history())


@dice_bp.route("/history", methods=["DELETE"])
def clear_roll_history():
    """-- Limpa o histórico de rolagens"""
    clear_history()
    return jsonify({"success": True, "message": "Histórico limpo."})
