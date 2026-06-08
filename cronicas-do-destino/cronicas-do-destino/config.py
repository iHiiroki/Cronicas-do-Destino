
# -- Configurações globais do app Crônicas do Destino

import os

# -- Diretório base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -- Diretórios de dados persistentes (JSON)
DATA_DIR      = os.path.join(BASE_DIR, "data")
CHAR_DIR      = os.path.join(DATA_DIR, "characters")
SESSION_DIR   = os.path.join(DATA_DIR, "sessions")
PROFILE_DIR   = os.path.join(DATA_DIR, "profiles")

# -- Classes disponíveis e suas estatísticas base
CLASS_STATS = {
    "Guerreiro": {"hp": 120, "attack": 18, "defense": 14, "magic": 4},
    "Mago":      {"hp": 80,  "attack": 8,  "defense": 8,  "magic": 22},
    "Ladino":    {"hp": 90,  "attack": 15, "defense": 10, "magic": 8},
    "Clérigo":   {"hp": 100, "attack": 10, "defense": 12, "magic": 16},
    "Ranger":    {"hp": 95,  "attack": 14, "defense": 11, "magic": 10},
    "Paladino":  {"hp": 110, "attack": 14, "defense": 16, "magic": 12},
}

# -- Raças disponíveis
VALID_RACES = ["Humano", "Elfo", "Anão", "Orc", "Halfling", "Tiefling"]

# -- Tabela de XP por nível (índice = nível atual, valor = XP necessário para o próximo)
XP_TABLE = [0, 100, 250, 450, 700, 1000, 1400, 1900, 2500, 3200, 4000]

# -- Tipos de dado válidos para rolagem
VALID_DICE_FACES = {2, 3, 4, 6, 8, 10, 12, 20, 100}

# -- Máximo de entradas no histórico de rolagens
MAX_DICE_HISTORY = 50

# -- Configuração do servidor Flask
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True

# -- Chave secreta para sessões Flask (altere em produção)
SECRET_KEY = "cronicas-do-destino-secret-2024"
