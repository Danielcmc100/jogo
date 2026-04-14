from src.engine.renderer import Renderer
from src.engine.physics import Collider
from src.game.settings import (
    TILE_SIZE,
    TILE_FRAME_WIDTH,
    TILE_FRAME_HEIGHT,
    TILE_TEX_WIDTH,
    TILE_TEX_HEIGHT,
    SOLID_TILE_COL,
    SOLID_TILE_ROW,
)
from src.game.snake import Snake

# ---------------------------------------------------------------------------
# Legenda do mapa
# ---------------------------------------------------------------------------
# '0' — vazio
# '1' — tile sólido (colisão em todos os lados)
# 'P' — plataforma one-way (colisão apenas pelo topo, ao descer)
# 'E' — inimigo cobra
# 'S' — spawn do player
# ---------------------------------------------------------------------------

MAP_1 = [
    "1000000000000000000000000000000000000000001",
    "1000000000000000000000000000000000000000001",
    "1000000000000000000000000000000000000000001",
    "10000S00000000000E0000000000000000E00000001",
    "100000000000PPPPP00000000000000PPPPP0000001",
    "1000000000000000000000000000000000000000001",
    "100000E000000000000000PPPPPPP0000000000E001",
    "1000000000000000000000000000000000000000001",
    "100000PPPPP00000000000000E000000PPPPP000001",
    "1000000000000000000000000000000000000000001",
    "1000000000000000000000000000000000000000001",
    "100PPPP000000000000000PPPPPP00000000000PPP1",
    "100000000000000000E00000000000000000000E001",
    "1111000000000000111100000000000011110000001",
    "1111111111111111111111111111111111111111111",
    "1111111111111111111111111111111111111111111",
]

MAP_2 = [
    "1111111111111111111111111111111111111111111",
    "1000000000000000000000000000000000000000001",
    "10S00000000000E000000000000000E000000000001",
    "1000PPPPPPP0000000000000PPPPPPP000000000001",
    "1000000000000000000E00000000000000000000E01",
    "10000000000000PPPPPPP00000000000PPPPPPPP111",
    "100000000E000000000000000000000000000000111",
    "10PPPPPPP000000000000000PPPPPPPP00000000111",
    "100000000000000EE00000000000000000000000111",
    "1111111111111111111000000000001111111111111",
    "11111111111111111110E0000000001111111111111",
    "11111111111111111111111P00P1111111111111111",
    "1111111111111111111111100001111111111111111",
    "1111111111111111111111111111111111111111111",
]

MAP_3 = [
    "1111111111111111111111111111111111111111111",
    "1000000000000000000000000000000000000000001",
    "10S000000P0000E0000P00E000P0000E000P000E001",
    "111111P00P00P111100P001100P00111100P00P1111",
    "1000000000000000000000000000000000000000001",
    "100111111111P000P111111111P0000P11111111111",
    "1000000000000E0000000E000000E0000000E00001",
    "100PPPPPPPP000PPPPPPP0000PPPPPPPP000PPPPPP1",
    "1000000000000000000000000000000000000000001",
    "1111111111111111111111111111111111111111111",
]

LEVELS = [MAP_1, MAP_2, MAP_3]

class Level:
    def __init__(self, level_index: int = 0) -> None:
        self.level_index = level_index % len(LEVELS)
        raw_map = LEVELS[self.level_index]
        
        # Normaliza largura: todas as linhas devem ter o mesmo comprimento
        max_cols = max(len(row) for row in raw_map)
        self.map_data: list[str] = [row.ljust(max_cols, "0") for row in raw_map]

        self.colliders: list[Collider] = []
        self.snakes: list[Snake] = []
        self.spawn_x: float = 100.0
        self.spawn_y: float = 100.0
        
        self._build_colliders()

    # ------------------------------------------------------------------
    # Construção dos colliders tipados e spawns
    # ------------------------------------------------------------------

    def _build_colliders(self) -> None:
        for row_idx, row in enumerate(self.map_data):
            for col_idx, cell in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                
                if cell == "1":
                    self.colliders.append({"x": x, "y": y, "w": TILE_SIZE, "h": TILE_SIZE, "one_way": False})
                elif cell == "P":
                    self.colliders.append({"x": x, "y": y, "w": TILE_SIZE, "h": TILE_SIZE, "one_way": True})
                elif cell == "S":
                    self.spawn_x = x
                    self.spawn_y = y
                elif cell == "E":
                    # Definir a área de patrulha para a cobra (algum espaço em volta)
                    # Coloca no chão do tile. 'y' é o topo do tile, a cobra fica acima
                    patrol_left = max(0, x - 50)
                    patrol_right = x + 50
                    self.snakes.append(Snake(x, y, patrol_left, patrol_right))

    # ------------------------------------------------------------------
    # Dimensões do mapa em pixels (útil para câmera / limites)
    # ------------------------------------------------------------------

    @property
    def width_px(self) -> int:
        return len(self.map_data[0]) * TILE_SIZE if self.map_data else 0

    @property
    def height_px(self) -> int:
        return len(self.map_data) * TILE_SIZE

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self, renderer: Renderer) -> None:
        uv_w = TILE_FRAME_WIDTH / TILE_TEX_WIDTH
        uv_h = TILE_FRAME_HEIGHT / TILE_TEX_HEIGHT
        uv_x = SOLID_TILE_COL * uv_w
        uv_y = SOLID_TILE_ROW * uv_h

        for row_idx, row in enumerate(self.map_data):
            for col_idx, cell in enumerate(row):
                if cell not in ("1", "P"):
                    continue

                renderer.draw_sprite(
                    "tile",
                    col_idx * TILE_SIZE,
                    row_idx * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE,
                    uv_x,
                    uv_y,
                    uv_w,
                    uv_h,
                )
