
# -- Motor de rolagem de dados para Crônicas do Destino
# -- Suporta d4, d6, d8, d10, d12, d20, d100 com modificadores

import re
import random
import uuid
from datetime import datetime
from config import VALID_DICE_FACES, MAX_DICE_HISTORY

# -- Padrão regex para notação de dados: NdX+M (ex: 2d6+3, 1d20, 3d8-1)
DICE_PATTERN = re.compile(r'^(\d+)d(\d+)([+-]\d+)?$', re.IGNORECASE)

# -- Histórico de rolagens (mantido em memória durante a sessão)
_history: list[dict] = []


def parse_dice(notation: str) -> tuple[int, int, int]:
    """
    -- Analisa a notação do dado (ex: '2d6+3')
    -- Retorna (num_dados, faces, modificador)
    -- Lança ValueError se inválido
    """
    notation = notation.strip().lower()
    match = DICE_PATTERN.match(notation)
    if not match:
        raise ValueError(f"Notação inválida: '{notation}'. Use formato como '2d6', '1d20+3', '3d8-1'.")

    num_dice = int(match.group(1))
    faces    = int(match.group(2))
    modifier = int(match.group(3)) if match.group(3) else 0

    if num_dice < 1 or num_dice > 20:
        raise ValueError("Número de dados deve ser entre 1 e 20.")
    if faces not in VALID_DICE_FACES:
        raise ValueError(f"d{faces} não é válido. Use: d4, d6, d8, d10, d12, d20 ou d100.")

    return num_dice, faces, modifier


def roll(notation: str, label: str = "") -> dict:
    """
    -- Realiza a rolagem dos dados e retorna resultado completo
    -- Detecta critico (20 natural em 1d20) e falha critica (1 natural em 1d20)
    """
    num_dice, faces, modifier = parse_dice(notation)

    # -- Rola cada dado individualmente
    rolls = [random.randint(1, faces) for _ in range(num_dice)]
    total = sum(rolls) + modifier

    # -- Critico e falha critica só se aplicam ao d20 com um único dado
    is_critical      = (num_dice == 1 and faces == 20 and rolls[0] == 20)
    is_critical_fail = (num_dice == 1 and faces == 20 and rolls[0] == 1)

    result = {
        "id":           str(uuid.uuid4()),
        "dice":         notation,
        "faces":        faces,
        "rolls":        rolls,
        "modifier":     modifier,
        "total":        total,
        "label":        label or f"Rolagem de {notation}",
        "critical":     is_critical,
        "criticalFail": is_critical_fail,
        "timestamp":    datetime.now().isoformat(),
    }

    # -- Adiciona ao histórico, mantendo tamanho máximo
    _history.append(result)
    if len(_history) > MAX_DICE_HISTORY:
        _history.pop(0)

    return result


def roll_attack(bonus: int = 0, label: str = "Ataque") -> dict:
    """-- Rolagem de ataque padrão: 1d20 com bônus"""
    notation = f"1d20+{bonus}" if bonus >= 0 else f"1d20{bonus}"
    return roll(notation, label)


def roll_damage(weapon_die: str = "1d8", bonus: int = 0, label: str = "Dano") -> dict:
    """-- Rolagem de dano com dado de arma e bônus"""
    notation = weapon_die
    if bonus > 0:
        notation += f"+{bonus}"
    elif bonus < 0:
        notation += str(bonus)
    return roll(notation, label)


def get_history() -> list[dict]:
    """-- Retorna o histórico de rolagens em ordem decrescente (mais recente primeiro)"""
    return list(reversed(_history))


def clear_history() -> None:
    """-- Limpa o histórico de rolagens"""
    _history.clear()
