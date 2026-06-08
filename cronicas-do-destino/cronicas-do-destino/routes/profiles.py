
# -- Rotas de perfis de jogador
# -- Perfis agrupam personagens para diferentes jogadores ou campanhas
# -- Endpoint base: /api/profiles

import json
import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from config import PROFILE_DIR

profiles_bp = Blueprint("profiles", __name__, url_prefix="/api/profiles")


def _ensure_dirs():
    os.makedirs(PROFILE_DIR, exist_ok=True)


def _profile_path(profile_id: str) -> str:
    return os.path.join(PROFILE_DIR, f"{profile_id}.json")


def _load_profile(profile_id: str) -> dict | None:
    path = _profile_path(profile_id)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_profile(profile: dict) -> None:
    _ensure_dirs()
    profile["updatedAt"] = datetime.now().isoformat()
    with open(_profile_path(profile["id"]), "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)


def _list_profiles() -> list[dict]:
    _ensure_dirs()
    profiles = []
    for fname in os.listdir(PROFILE_DIR):
        if fname.endswith(".json"):
            p = _load_profile(fname[:-5])
            if p:
                profiles.append(p)
    return sorted(profiles, key=lambda p: p.get("name", ""))


@profiles_bp.route("/", methods=["GET"])
def get_profiles():
    """-- Lista todos os perfis de jogador"""
    return jsonify(_list_profiles())


@profiles_bp.route("/", methods=["POST"])
def create_profile():
    """
    -- Cria um novo perfil de jogador
    -- Body: { name: str, avatar?: str, description?: str }
    """
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()

    if not name:
        return jsonify({"error": "Nome do perfil é obrigatório."}), 400
    if len(name) > 40:
        return jsonify({"error": "Nome deve ter no máximo 40 caracteres."}), 400

    now     = datetime.now().isoformat()
    profile = {
        "id":          str(uuid.uuid4()),
        "name":        name,
        "avatar":      data.get("avatar", "🧙"),   # -- Emoji como avatar padrão
        "description": data.get("description", ""),
        "createdAt":   now,
        "updatedAt":   now,
    }
    _save_profile(profile)
    return jsonify(profile), 201


@profiles_bp.route("/<profile_id>", methods=["GET"])
def get_profile(profile_id: str):
    """-- Retorna um perfil específico"""
    profile = _load_profile(profile_id)
    if not profile:
        return jsonify({"error": "Perfil não encontrado."}), 404
    return jsonify(profile)


@profiles_bp.route("/<profile_id>", methods=["PATCH"])
def update_profile(profile_id: str):
    """-- Atualiza nome, avatar ou descrição do perfil"""
    profile = _load_profile(profile_id)
    if not profile:
        return jsonify({"error": "Perfil não encontrado."}), 404

    data = request.get_json(silent=True) or {}
    if "name" in data and data["name"]:
        profile["name"] = data["name"].strip()[:40]
    if "avatar" in data:
        profile["avatar"] = data["avatar"]
    if "description" in data:
        profile["description"] = data["description"]

    _save_profile(profile)
    return jsonify(profile)


@profiles_bp.route("/<profile_id>", methods=["DELETE"])
def delete_profile(profile_id: str):
    """-- Remove um perfil (não remove os personagens associados)"""
    path = _profile_path(profile_id)
    if not os.path.exists(path):
        return jsonify({"error": "Perfil não encontrado."}), 404
    os.remove(path)
    return jsonify({"success": True, "message": "Perfil removido."})
