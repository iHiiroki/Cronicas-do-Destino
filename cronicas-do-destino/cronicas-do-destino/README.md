# ⚔️ Crônicas do Destino

RPG de mesa digital completo em Python + Flask.

---

## 🚀 Como executar

### 1. Instalar dependências
```bash
pip install flask flask-cors
```

### 2. Iniciar o servidor
```bash
python app.py
```

### 3. Abrir no navegador
```
http://localhost:5000
```

---

## 📁 Estrutura do projeto

```
cronicas-do-destino/
├── app.py              ← Ponto de entrada Flask, registra rotas e páginas
├── config.py           ← Constantes: stats de classes, XP, dados válidos
├── requirements.txt    ← Dependências Python (flask, flask-cors)
│
├── models/             ← Lógica de negócio (backend puro)
│   ├── character.py    ← Classe Character + persistência JSON
│   ├── item.py         ← Catálogo de 20 itens + funções de filtragem
│   ├── adventure.py    ← 3 aventuras completas + sistema de sessões
│   └── dice.py         ← Motor de rolagem com histórico em memória
│
├── routes/             ← Endpoints REST da API
│   ├── characters.py   ← /api/characters (CRUD + inventário + XP)
│   ├── items.py        ← /api/items (catálogo + compra + venda)
│   ├── adventures.py   ← /api/adventures (sessões + escolhas)
│   ├── dice.py         ← /api/dice (rolagem + histórico)
│   └── profiles.py     ← /api/profiles (perfis de jogador)
│
├── templates/          ← HTML das páginas (Jinja2, herdam base.html)
│   ├── base.html       ← Layout base: sidebar + toasts + fontes
│   ├── dashboard.html  ← Página inicial com resumo
│   ├── characters.html ← Gerenciamento de personagens
│   ├── dice.html       ← Rolagem de dados com animações SVG
│   ├── items.html      ← Loja + inventário
│   ├── adventures.html ← Aventuras + sessões salvas
│   └── profiles.html   ← Perfis de jogador
│
├── static/
│   ├── css/style.css   ← Todo o CSS: cores, layout, animações
│   └── js/
│       ├── app.js       ← Utilitários globais: API fetch, toasts, formatadores
│       ├── dice.js      ← SVGs únicos por dado + animações de rolagem
│       ├── characters.js← CRUD de personagens, filtragem, level up
│       ├── items.js     ← Loja, compra, venda, inventário
│       └── adventures.js← Sistema de escolhas, sessões persistentes
│
└── data/               ← Criado automaticamente ao rodar
    ├── characters/     ← Um arquivo .json por personagem
    ├── sessions/       ← Um arquivo .json por sessão de aventura
    └── profiles/       ← Um arquivo .json por perfil de jogador
```

---

## ✨ Funcionalidades

### Personagens
- Criar personagens com nome, raça, classe e backstory
- 6 classes: Guerreiro, Mago, Ladino, Clérigo, Ranger, Paladino
- 6 raças: Humano, Elfo, Anão, Orc, Halfling, Tiefling
- Progressão de nível automática com ganho de XP
- Stats sobem ao subir de nível
- Filtros por classe, raça, perfil e nome
- Persistência em JSON (ficam salvos mesmo fechando o app)

### Dados
- d4, d6, d8, d10, d12, d20, d100
- SVGs únicos e corretos para cada poliedro
- d20 CORRIGIDO (triângulo com subdivisões de icosaedro, não d4)
- Animação de tremida ao rolar
- Brilho dourado em acerto crítico (20 natural)
- Brilho vermelho em falha crítica (1 natural)
- Modificadores (+3, -1, etc.)
- Rolagens rápidas de combate
- Histórico das últimas 50 rolagens

### Loja de Itens
- 20 itens em 5 raridades: Comum → Lendário
- Tipos: Armas, Armaduras, Feitiços, Poções, Acessórios
- Compra debita ouro do personagem
- Venda por 50% do valor original
- Equipar itens em slots (weapon, armor, accessory)
- Filtragem por tipo, raridade e busca textual

### Aventuras
- 3 aventuras completas com múltiplas rotas de decisão
- Escolhas com pré-requisito de nível
- Recompensas: XP + Ouro ao concluir
- Sessões salvas em JSON (pode sair e continuar depois)
- 3 abas: Disponíveis / Em andamento / Concluídas
- Opção de abandonar aventura

### Perfis de Jogador
- Organizar personagens por jogador ou campanha
- Avatares emoji personalizáveis
- Filtragem de personagens por perfil

---

## 🎨 Design

- **Fundo:** Preto profundo com textura de estrelas
- **Cor primária:** Roxo (#8b5cf6)
- **Destaques:** Dourado (itens), Ciano (magia), Verde (vida), Vermelho (dano), Laranja (fogo)
- **Fontes:** Cinzel (épica, títulos) + Inter (corpo de texto)
- **Animações:** Entrada suave, hover, tremida de dados, brilhos CSS

---

## ⚙️ Tecnologias

- **Backend:** Python 3.10+ · Flask 3.x · flask-cors
- **Frontend:** HTML5 · CSS3 puro · JavaScript ES2022 (sem frameworks)
- **Persistência:** JSON local (sem banco de dados externo)
- **Fontes:** Google Fonts (Cinzel + Inter)
