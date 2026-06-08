
# ============================================================
# -- CRÔNICAS DO DESTINO — Aplicativo RPG em Python + Flask
# -- Backend: Flask (Python)
# -- Frontend: HTML + CSS + JavaScript (em templates/)
# -- Dados: JSON em data/ (persistência local)
# ============================================================
#
# -- Como executar:
# --   1. pip install flask flask-cors
# --   2. python app.py
# --   3. Abra http://localhost:5000 no navegador
#
# -- Estrutura de pastas:
# --   app.py          → Ponto de entrada, registra rotas
# --   config.py       → Constantes e configurações globais
# --   models/         → Lógica de negócio (characters, items, etc.)
# --   routes/         → Endpoints REST da API
# --   templates/      → HTML das páginas (Jinja2)
# --   static/         → CSS, JavaScript e imagens
# --   data/           → Arquivos JSON persistentes (criados automaticamente)
# ============================================================

import os
from flask import Flask, render_template
from flask_cors import CORS

# -- Importa os Blueprints de cada módulo de rotas
from routes.characters import characters_bp
from routes.items       import items_bp
from routes.adventures  import adventures_bp
from routes.dice        import dice_bp
from routes.profiles    import profiles_bp
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG, SECRET_KEY

# ==========================================
# -- INICIALIZAÇÃO DO APP FLASK
# ==========================================

app = Flask(
    __name__,
    template_folder="templates",   # -- Pasta de templates HTML (Jinja2)
    static_folder="static",        # -- Pasta de arquivos estáticos (CSS, JS)
)

# -- Chave secreta para sessões e segurança
app.secret_key = SECRET_KEY

# -- CORS: permite chamadas da interface web ao backend
CORS(app)

# ==========================================
# -- REGISTRO DE BLUEPRINTS (ROTAS DA API)
# ==========================================

app.register_blueprint(characters_bp)  # -- /api/characters
app.register_blueprint(items_bp)       # -- /api/items
app.register_blueprint(adventures_bp)  # -- /api/adventures
app.register_blueprint(dice_bp)        # -- /api/dice
app.register_blueprint(profiles_bp)    # -- /api/profiles

# ==========================================
# -- ROTAS DO FRONTEND (PÁGINAS HTML)
# ==========================================

@app.route("/")
def index():
    """-- Página inicial: Dashboard com resumo do jogo"""
    return render_template("dashboard.html")


@app.route("/characters")
def characters_page():
    """-- Página de gerenciamento de personagens"""
    return render_template("characters.html")


@app.route("/dice")
def dice_page():
    """-- Página de rolagem de dados com animações"""
    return render_template("dice.html")


@app.route("/items")
def items_page():
    """-- Página da loja e inventário de itens"""
    return render_template("items.html")


@app.route("/adventures")
def adventures_page():
    """-- Página de aventuras e missões"""
    return render_template("adventures.html")


@app.route("/profiles")
def profiles_page():
    """-- Página de gerenciamento de perfis"""
    return render_template("profiles.html")


# ==========================================
# -- HANDLER DE ERROS
# ==========================================

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


# ==========================================
# -- PONTO DE ENTRADA
# ==========================================

if __name__ == "__main__":
    # -- Garante que as pastas de dados existem antes de iniciar
    os.makedirs("data/characters", exist_ok=True)
    os.makedirs("data/sessions",   exist_ok=True)
    os.makedirs("data/profiles",   exist_ok=True)

    print("╔══════════════════════════════════════╗")
    print("║   CRÔNICAS DO DESTINO — v1.0         ║")
    print("║   Servidor iniciado!                 ║")
    print(f"║   Acesse: http://localhost:{FLASK_PORT}      ║")
    print("╚══════════════════════════════════════╝")

    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
