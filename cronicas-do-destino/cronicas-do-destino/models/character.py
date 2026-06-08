
# -- Modelo de personagem com persistência em JSON
# -- Gerencia criação, atualização, nível e inventário

import json
import os
import uuid
from datetime import datetime
from config import CHAR_DIR, CLASS_STATS, XP_TABLE


def _ensure_dirs():
    """-- Garante que os diretórios de dados existem"""
    os.makedirs(CHAR_DIR, exist_ok=True)


def _char_path(char_id: str) -> str:
    """-- Retorna o caminho do arquivo JSON de um personagem"""
    return os.path.join(CHAR_DIR, f"{char_id}.json")


# ==========================================
# -- CLASSE PERSONAGEM
# ==========================================

class Character:
    """
    -- Representa um personagem jogável com stats, inventário e progressão de nível
    """

    def __init__(self, data: dict):
        stats = CLASS_STATS.get(data.get("characterClass", "Guerreiro"), CLASS_STATS["Guerreiro"])
        now   = datetime.now().isoformat()

        self.id                   = data.get("id") or str(uuid.uuid4())
        self.name                 = data["name"]
        self.race                 = data["race"]
        self.character_class      = data["characterClass"]
        self.backstory            = data.get("backstory")
        self.profile_id           = data.get("profileId")           # -- Perfil ao qual pertence
        self.level                = data.get("level", 1)
        self.max_hp               = data.get("maxHp", stats["hp"])
        self.hp                   = data.get("hp", self.max_hp)
        self.xp                   = data.get("xp", 0)
        self.xp_to_next           = data.get("xpToNextLevel", XP_TABLE[1])
        self.gold                 = data.get("gold", 50)
        self.attack               = data.get("attack", stats["attack"])
        self.defense              = data.get("defense", stats["defense"])
        self.magic                = data.get("magic", stats["magic"])
        self.inventory            = data.get("inventory", [])        # -- Lista de IDs de itens
        self.equipped_items       = data.get("equippedItems", {})    # -- slot -> item_id
        self.kills                = data.get("kills", 0)
        self.adventures_completed = data.get("adventuresCompleted", 0)
        self.created_at           = data.get("createdAt", now)
        self.updated_at           = data.get("updatedAt", now)

    def gain_xp(self, amount: int) -> list[str]:
        """
        -- Adiciona XP e sobe de nível automaticamente se necessário
        -- Retorna lista de mensagens de level up
        """
        self.xp += amount
        messages = []

        while self.level < len(XP_TABLE) - 1 and self.xp >= self.xp_to_next:
            self.level += 1
            self.xp_to_next = XP_TABLE[self.level] if self.level < len(XP_TABLE) else self.xp_to_next * 2

            # -- Bônus de stats ao subir de nível
            stats = CLASS_STATS.get(self.character_class, CLASS_STATS["Guerreiro"])
            self.max_hp  += stats["hp"] // 10
            self.hp       = self.max_hp  # -- Recupera HP ao subir de nível
            self.attack  += stats["attack"] // 10
            self.defense += stats["defense"] // 10
            self.magic   += stats["magic"] // 10

            messages.append(f"🎉 Level up! Agora você é nível {self.level}!")

        self.updated_at = datetime.now().isoformat()
        return messages

    def add_to_inventory(self, item_id: str) -> None:
        """-- Adiciona item ao inventário do personagem"""
        self.inventory.append(item_id)
        self.updated_at = datetime.now().isoformat()

    def remove_from_inventory(self, item_id: str) -> bool:
        """-- Remove item do inventário; retorna True se removido"""
        if item_id in self.inventory:
            self.inventory.remove(item_id)
            self.updated_at = datetime.now().isoformat()
            return True
        return False

    def equip_item(self, item_id: str, slot: str) -> None:
        """-- Equipa um item em um slot (weapon, armor, accessory, etc.)"""
        self.equipped_items[slot] = item_id
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """-- Serializa o personagem para dicionário (usado para JSON e API)"""
        return {
            "id":                   self.id,
            "name":                 self.name,
            "race":                 self.race,
            "characterClass":       self.character_class,
            "backstory":            self.backstory,
            "profileId":            self.profile_id,
            "level":                self.level,
            "hp":                   self.hp,
            "maxHp":                self.max_hp,
            "xp":                   self.xp,
            "xpToNextLevel":        self.xp_to_next,
            "gold":                 self.gold,
            "attack":               self.attack,
            "defense":              self.defense,
            "magic":                self.magic,
            "inventory":            self.inventory,
            "equippedItems":        self.equipped_items,
            "kills":                self.kills,
            "adventuresCompleted":  self.adventures_completed,
            "createdAt":            self.created_at,
            "updatedAt":            self.updated_at,
        }


# ==========================================
# -- FUNÇÕES DE PERSISTÊNCIA
# ==========================================

def save_character(char: Character) -> None:
    """-- Salva personagem em arquivo JSON"""
    _ensure_dirs()
    with open(_char_path(char.id), "w", encoding="utf-8") as f:
        json.dump(char.to_dict(), f, ensure_ascii=False, indent=2)


def load_character(char_id: str) -> Character | None:
    """-- Carrega personagem do arquivo JSON; retorna None se não existir"""
    path = _char_path(char_id)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return Character(json.load(f))


def list_characters() -> list[Character]:
    """-- Lista todos os personagens salvos"""
    _ensure_dirs()
    chars = []
    for fname in os.listdir(CHAR_DIR):
        if fname.endswith(".json"):
            char_id = fname[:-5]
            char    = load_character(char_id)
            if char:
                chars.append(char)
    # -- Ordena por nome para consistência
    return sorted(chars, key=lambda c: c.name)


def delete_character(char_id: str) -> bool:
    """-- Remove o arquivo do personagem; retorna True se deletado"""
    path = _char_path(char_id)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
