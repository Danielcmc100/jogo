LOGICAL_WIDTH = 320
LOGICAL_HEIGHT = 180
WINDOW_SCALE = 3
SCREEN_WIDTH = LOGICAL_WIDTH * WINDOW_SCALE
SCREEN_HEIGHT = LOGICAL_HEIGHT * WINDOW_SCALE

# Physics
GRAVITY = 900.0
PLAYER_SPEED = 200.0
JUMP_FORCE = -400.0

# Tile Sizes
TILE_SIZE = 32

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
    "idle": (0, 4, 8.0),   # linha 0, 4 frames, 8 fps
    "walk": (1, 6, 10.0),  # linha 1, 6 frames, 10 fps
    "jump": (2, 2, 6.0),   # linha 2, 2 frames, 6 fps
}

# ---------------------------------------------------------------------------
# new_tle.png — 128x128, frames de 32x32 (4 colunas × 4 linhas)
# Layout da spritesheet:
#   Bloco de terra sólida: coluna 0, linha 0
# ---------------------------------------------------------------------------
TILE_FRAME_WIDTH: int = 32
TILE_FRAME_HEIGHT: int = 32
TILE_TEX_WIDTH: float = 128.0
TILE_TEX_HEIGHT: float = 128.0

# Coordenadas do tile sólido (coluna, linha) dentro da sheet
SOLID_TILE_COL: int = 0
SOLID_TILE_ROW: int = 0
