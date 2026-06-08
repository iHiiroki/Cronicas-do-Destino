
# -- Catálogo de itens e lógica de compra/venda
# -- Itens têm raridades, bônus de stats e efeitos especiais

# ==========================================
# -- CATÁLOGO COMPLETO DE ITENS
# ==========================================

ITEM_CATALOG: list[dict] = [
    # -- ============ ARMAS COMUNS ============
    {
        "id": "iron_sword", "name": "Espada de Ferro", "type": "weapon", "rarity": "comum",
        "description": "Uma espada de ferro simples, porém confiável em batalha.",
        "value": 30, "attackBonus": 5, "defenseBonus": 0, "magicBonus": 0,
        "healAmount": 0, "weaponDie": "1d8", "slot": "weapon",
        "effects": [], "icon": "⚔️",
    },
    {
        "id": "dagger", "name": "Adaga Afiada", "type": "weapon", "rarity": "comum",
        "description": "Pequena, rápida e letal de perto.",
        "value": 15, "attackBonus": 3, "defenseBonus": 0, "magicBonus": 0,
        "healAmount": 0, "weaponDie": "1d4", "slot": "weapon",
        "effects": [], "icon": "🗡️",
    },
    {
        "id": "wooden_staff", "name": "Cajado de Madeira", "type": "weapon", "rarity": "comum",
        "description": "Um cajado simples que canaliza energia mágica básica.",
        "value": 20, "attackBonus": 1, "defenseBonus": 0, "magicBonus": 4,
        "healAmount": 0, "weaponDie": "1d6", "slot": "weapon",
        "effects": [], "icon": "🪄",
    },
    # -- ============ ARMADURAS COMUNS ============
    {
        "id": "leather_armor", "name": "Armadura de Couro", "type": "armor", "rarity": "comum",
        "description": "Proteção básica feita de couro endurecido.",
        "value": 25, "attackBonus": 0, "defenseBonus": 5, "magicBonus": 0,
        "healAmount": 0, "weaponDie": None, "slot": "armor",
        "effects": [], "icon": "🛡️",
    },
    {
        "id": "cloth_robe", "name": "Robe de Pano", "type": "armor", "rarity": "comum",
        "description": "Robe leve que favorece movimentação e conjuração.",
        "value": 18, "attackBonus": 0, "defenseBonus": 2, "magicBonus": 3,
        "healAmount": 0, "weaponDie": None, "slot": "armor",
        "effects": ["Conjuração +1"], "icon": "👘",
    },
    # -- ============ POÇÕES ============
    {
        "id": "health_potion", "name": "Poção de Vida", "type": "potion", "rarity": "comum",
        "description": "Uma poção vermelha borbulhante que restaura vitalidade.",
        "value": 20, "attackBonus": 0, "defenseBonus": 0, "magicBonus": 0,
        "healAmount": 30, "weaponDie": None, "slot": None,
        "effects": ["Cura 30 HP"], "icon": "🧪",
    },
    {
        "id": "mana_potion", "name": "Poção de Mana", "type": "potion", "rarity": "comum",
        "description": "Poção azul que restaura energia mágica.",
        "value": 20, "attackBonus": 0, "defenseBonus": 0, "magicBonus": 5,
        "healAmount": 0, "weaponDie": None, "slot": None,
        "effects": ["Mágica +5 por 3 turnos"], "icon": "💧",
    },
    # -- ============ INCOMUNS ============
    {
        "id": "steel_sword", "name": "Espada de Aço", "type": "weapon", "rarity": "incomum",
        "description": "Forjada em aço temperado, com equilíbrio perfeito.",
        "value": 80, "attackBonus": 9, "defenseBonus": 0, "magicBonus": 0,
        "healAmount": 0, "weaponDie": "1d10", "slot": "weapon",
        "effects": [], "icon": "⚔️",
    },
    {
        "id": "chain_mail", "name": "Cota de Malha", "type": "armor", "rarity": "incomum",
        "description": "Elos de metal entrelaçados oferecem boa proteção.",
        "value": 75, "attackBonus": 0, "defenseBonus": 9, "magicBonus": 0,
        "healAmount": 0, "weaponDie": None, "slot": "armor",
        "effects": [], "icon": "🛡️",
    },
    {
        "id": "magic_staff", "name": "Cajado Arcano", "type": "spell", "rarity": "incomum",
        "description": "Um cajado imbuído de energia mágica que amplifica feitiços.",
        "value": 90, "attackBonus": 2, "defenseBonus": 0, "magicBonus": 8,
        "healAmount": 0, "weaponDie": "1d6", "slot": "weapon",
        "effects": ["Amplifica magia +20%"], "icon": "🔮",
    },
    {
        "id": "great_potion", "name": "Poção Maior de Vida", "type": "potion", "rarity": "incomum",
        "description": "Poção concentrada que restaura vitalidade significativa.",
        "value": 50, "attackBonus": 0, "defenseBonus": 0, "magicBonus": 0,
        "healAmount": 60, "weaponDie": None, "slot": None,
        "effects": ["Cura 60 HP"], "icon": "🧪",
    },
    {
        "id": "shadow_cloak", "name": "Manto das Sombras", "type": "accessory", "rarity": "incomum",
        "description": "Um manto que mescla seu portador com as sombras.",
        "value": 70, "attackBonus": 4, "defenseBonus": 3, "magicBonus": 0,
        "healAmount": 0, "weaponDie": None, "slot": "accessory",
        "effects": ["Furtividade +15%"], "icon": "🌑",
    },
    # -- ============ RAROS ============
    {
        "id": "elven_bow", "name": "Arco Élfico", "type": "weapon", "rarity": "raro",
        "description": "Arco artesanal éfico com precisão sobrenatural.",
        "value": 200, "attackBonus": 13, "defenseBonus": 0, "magicBonus": 4,
        "healAmount": 0, "weaponDie": "1d8", "slot": "weapon",
        "effects": ["Alcance dobrado", "Precisão +10%"], "icon": "🏹",
    },
    {
        "id": "plate_armor", "name": "Armadura de Placas", "type": "armor", "rarity": "raro",
        "description": "Placas de aço reforçadas, a armadura mais pesada disponível.",
        "value": 250, "attackBonus": 0, "defenseBonus": 18, "magicBonus": 0,
        "healAmount": 0, "weaponDie": None, "slot": "armor",
        "effects": ["Redução de dano físico +5"], "icon": "🛡️",
    },
    {
        "id": "tome_of_power", "name": "Tomo do Poder", "type": "spell", "rarity": "raro",
        "description": "Um grimório antigo com feitiços de poder devastador.",
        "value": 300, "attackBonus": 5, "defenseBonus": 0, "magicBonus": 15,
        "healAmount": 0, "weaponDie": "2d8", "slot": "weapon",
        "effects": ["Feitiços causam +30% de dano"], "icon": "📖",
    },
    {
        "id": "healing_amulet", "name": "Amuleto de Cura", "type": "accessory", "rarity": "raro",
        "description": "Um amuleto que emite luz suave e regenera vitalidade.",
        "value": 180, "attackBonus": 0, "defenseBonus": 2, "magicBonus": 6,
        "healAmount": 20, "weaponDie": None, "slot": "accessory",
        "effects": ["Regenera 5 HP por turno"], "icon": "💎",
    },
    # -- ============ ÉPICOS ============
    {
        "id": "dragon_blade", "name": "Lâmina do Dragão", "type": "weapon", "rarity": "épico",
        "description": "Forjada com escamas de dragão, queima com chamas eternas.",
        "value": 800, "attackBonus": 22, "defenseBonus": 3, "magicBonus": 8,
        "healAmount": 0, "weaponDie": "2d10", "slot": "weapon",
        "effects": ["Dano de fogo +15", "Ignora armadura leve"], "icon": "🔥",
    },
    {
        "id": "arcane_robe", "name": "Robe Arcano", "type": "armor", "rarity": "épico",
        "description": "Tecido com fios mágicos, protege corpo e mente.",
        "value": 750, "attackBonus": 5, "defenseBonus": 12, "magicBonus": 20,
        "healAmount": 0, "weaponDie": None, "slot": "armor",
        "effects": ["Resistência mágica +25%", "Regeneração de mana"], "icon": "✨",
    },
    # -- ============ LENDÁRIOS ============
    {
        "id": "excalibur", "name": "Excalibur", "type": "weapon", "rarity": "lendário",
        "description": "A espada lendária dos reis. Brilha com luz divina.",
        "value": 2000, "attackBonus": 35, "defenseBonus": 10, "magicBonus": 15,
        "healAmount": 0, "weaponDie": "3d10", "slot": "weapon",
        "effects": ["Dano sagrado +25", "Imunidade a maldições", "Crítico em 19-20"], "icon": "👑",
    },
    {
        "id": "elixir_eternity", "name": "Elixir da Eternidade", "type": "potion", "rarity": "lendário",
        "description": "Uma poção de ouro líquido que restaura completamente.",
        "value": 1000, "attackBonus": 0, "defenseBonus": 0, "magicBonus": 0,
        "healAmount": 999, "weaponDie": None, "slot": None,
        "effects": ["Cura HP completo", "Remove todas as condições negativas"], "icon": "⚗️",
    },
]

# -- Índice rápido por ID
_CATALOG_INDEX: dict[str, dict] = {item["id"]: item for item in ITEM_CATALOG}


def get_item(item_id: str) -> dict | None:
    """-- Retorna dados de um item pelo ID, ou None se não existir"""
    return _CATALOG_INDEX.get(item_id)


def get_catalog(
    item_type: str | None = None,
    rarity: str | None = None,
    max_value: int | None = None,
    search: str | None = None,
) -> list[dict]:
    """
    -- Retorna o catálogo filtrado
    -- item_type: weapon, armor, spell, potion, accessory
    -- rarity: comum, incomum, raro, épico, lendário
    -- max_value: preço máximo em ouro
    -- search: busca por nome ou descrição
    """
    items = list(ITEM_CATALOG)

    if item_type:
        items = [i for i in items if i["type"] == item_type]
    if rarity:
        items = [i for i in items if i["rarity"] == rarity]
    if max_value is not None:
        items = [i for i in items if i["value"] <= max_value]
    if search:
        s = search.lower()
        items = [i for i in items if s in i["name"].lower() or s in i["description"].lower()]

    return items
