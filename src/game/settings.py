LOGICAL_WIDTH = 320
LOGICAL_HEIGHT = 180
WINDOW_SCALE = 3
SCREEN_WIDTH = LOGICAL_WIDTH * WINDOW_SCALE
SCREEN_HEIGHT = LOGICAL_HEIGHT * WINDOW_SCALE

# Physics
GRAVITY = 900.0
PLAYER_SPEED = 200.0
JUMP_FORCE = -400.0
PLAYER_MAX_HP: int = 5  # vida cheia = sprite ui_hp_5
PLAYER_INVINCIBILITY_TIME: float = 1.0  # segundos de invencibilidade após dano


# Tile Sizes
TILE_SIZE = 16

# ---------------------------------------------------------------------------
# char_panda.png — 256x256, frames de 32x32 (8 colunas × 8 linhas)
# Layout da spritesheet:
#   Linha 0: Idle   — 4 frames (col 0-3)
#   Linha 1: Walk   — 6 frames (col 0-5)
#   Linha 5: Run    — 8 frames (col 0-7)
#   Linha 2: Jump   — 2 frames (col 0-1)
# ---------------------------------------------------------------------------
PLAYER_FRAME_WIDTH: int = 32
PLAYER_FRAME_HEIGHT: int = 32
PLAYER_TEX_WIDTH: float = 256.0
PLAYER_TEX_HEIGHT: float = 256.0

# Definição de animações do player:
# chave -> (linha_na_sheet, num_frames, fps_da_animacao)
PLAYER_ANIMATIONS: dict[str, tuple[int, int, float]] = {
    "idle": (7, 4, 8.0),  # linha 7, 4 frames, 8 fps
    "walk": (6, 5, 10.0),  # linha 6, 5 frames, 10 fps
    "jump": (3, 1, 6.0),  # linha 3, 1 frame,  6 fps
    "attack": (5, 3, 12.0),  # linha 5, cols 0-2, 3 frames, 12 fps  ← ESPADA
}

# Hitbox da espada (extende à frente do player)
PLAYER_ATTACK_W: int = 22  # largura do alcance da espada (px)
PLAYER_ATTACK_H: int = 18  # altura da hitbox (px)
# A hitbox fica ativa apenas nos frames 1 e 2 do ataque
PLAYER_ATTACK_ACTIVE_FRAMES: tuple[int, ...] = (1, 2)

# ---------------------------------------------------------------------------
# new_tle.png — 128x128, frames de 32x32 (4 colunas × 4 linhas)
# Layout da spritesheet:
#   Bloco de terra sólida: coluna 0, linha 0
# ---------------------------------------------------------------------------
TILE_FRAME_WIDTH: int = 16
TILE_FRAME_HEIGHT: int = 16
TILE_TEX_WIDTH: float = 128.0
TILE_TEX_HEIGHT: float = 128.0

# Coordenadas do tile sólido (coluna, linha) dentro da sheet
SOLID_TILE_COL: int = 1
SOLID_TILE_ROW: int = 7

# ---------------------------------------------------------------------------
# npc_snake.png — 72x48, frames de 24x24 (3 colunas × 2 linhas)
# Layout da spritesheet:
#   Linha 0 (row 0): Walk  — 3 frames (cols 0-2)
#   Linha 1 (row 1): Attack — 2 frames (cols 0-1) — cobra cospe fogo
# ---------------------------------------------------------------------------
SNAKE_FRAME_WIDTH: int = 24
SNAKE_FRAME_HEIGHT: int = 24
SNAKE_TEX_WIDTH: float = 72.0
SNAKE_TEX_HEIGHT: float = 48.0

# chave -> (linha_na_sheet, num_frames, fps_da_animacao)
SNAKE_ANIMATIONS: dict[str, tuple[int, int, float]] = {
    "walk": (1, 3, 8.0),  # linha 0, 3 frames, 8 fps
    "attack": (0, 2, 6.0),  # linha 1, 2 frames, 6 fps
}

# Comportamento da cobra
SNAKE_SPEED: float = 30.0  # px/s de movimento horizontal
SNAKE_DETECTION_RANGE: float = 60.0  # distância pra detectar o player
SNAKE_ATTACK_RANGE: float = 80.0  # distância pra disparar a bola de fogo
SNAKE_ATTACK_COOLDOWN: float = 4.0  # segundos entre ataques
SNAKE_MAX_HP: int = 2  # hits para matar a cobra
SNAKE_HIT_INVINCIBILITY: float = 0.1  # segundos de invencibilidade pós-hit

# ---------------------------------------------------------------------------
# npc_fire1.png — 32x16, frames de 8x16 (4 colunas × 1 linha)
# 4 frames em loop horizontal representando a bola de fogo em movimento
# ---------------------------------------------------------------------------
FIRE_FRAME_WIDTH: int = 8
FIRE_FRAME_HEIGHT: int = 16
FIRE_TEX_WIDTH: float = 16
FIRE_TEX_HEIGHT: float = 32

# chave -> (linha_na_sheet, num_frames, fps_da_animacao)
FIRE_ANIMATIONS: dict[str, tuple[int, int, float]] = {
    "fly": (0, 4, 12.0),  # linha 0, 4 frames, 12 fps
}

FIREBALL_SPEED: float = 180.0  # px/s
