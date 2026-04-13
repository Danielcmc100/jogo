# Jogo de Plataforma 2D (Pygame + OpenGL)

## 📝 Descrição do Projeto
Este projeto é um motor de jogo de plataforma 2D desenvolvido em Python, focado em performance e estética retro. Ele utiliza o **Pygame** para gerenciamento de janelas e eventos, mas delega toda a renderização para a GPU através do **PyOpenGL**, utilizando shaders modernos (GLSL).

O jogo apresenta um panda como protagonista, sistemas de colisão AABB, terreno baseado em tiles e um sistema de fundo com efeito parallax, tudo renderizado com precisão de pixels (**Pixel Perfect**).

---

## 🛠️ Stack Tecnológica
- **Linguagem:** Python 3.12+
- **Renderização:** PyOpenGL (Modern OpenGL com Shaders)
- **Engine Base:** Pygame (Janelamento e Input)
- **Gerenciador de Pacotes:** `uv`
- **Qualidade de Código:** `ruff` (Linter/Formatter) e `basedpyright` (Tipagem Estática)

---

## 🚀 Boas Práticas Aplicadas

### 1. Arquitetura Modular
O projeto foi dividido em camadas claras de responsabilidade:
- `src/engine/`: Abstrações de baixo nível para OpenGL (Shaders, Renderer, Window) e utilitários de física.
- `src/game/`: Lógica de alto nível, entidades (Player, Level, Background) e configurações.

### 2. Tipagem Estática (Static Typing)
Uso extensivo de *Type Hints* em todas as funções e classes para garantir a integridade dos dados, facilitar o refactoring e permitir que ferramentas como o `basedpyright` detectem erros antes da execução.

### 3. Renderização Pixel Perfect
- **Logical Resolution:** O jogo processa a lógica em uma resolução baixa fixa (ex: 320x180) e escala para a janela usando multiplicadores inteiros.
- **Sub-pixel Snapping:** Todas as coordenadas de desenho e de câmera são arredondadas (`round()`) antes de serem enviadas para as matrizes de modelo/visão, evitando artefatos de interpolação e garantindo nitidez máxima nos sprites.

### 4. Gerenciamento de Assets
- Separação entre ativos em uso (`sprites/`) e ativos descartados ou ignorados (`sprites_ignored/`).
- Uso de `gitignore` local para manter o repositório limpo de arquivos temporários ou metadados de outras engines (como arquivos `.meta`).

### 5. Ciclo de Vida do Motor (Engine Loop)
- Implementação de **Delta Time (dt)** para garantir que a velocidade do jogo seja independente da taxa de quadros (framerate).
- Separação clara entre as fases de `poll_events`, `update` e `render`.

---

## ⚡ Como Executar
```powershell
uv run python main.py
```

---
*Documentação gerada automaticamente para referência de desenvolvimento.*
