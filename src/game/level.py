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

# ---------------------------------------------------------------------------
# Legenda do mapa
# ---------------------------------------------------------------------------
# '0' — vazio
# '1' — tile sólido (colisão em todos os lados)
# 'P' — plataforma one-way (colisão apenas pelo topo, ao descer)
#
# Expansão: 40 colunas × 20 linhas = 1280 × 640 px lógicos
# Com WINDOW_SCALE=3 → 3840 × 1920 px de janela (scrola via câmera)
# ---------------------------------------------------------------------------

_MAP: list[str] = [
    # col:  0         1         2         3         4
    #       0123456789012345678901234567890123456789
    "1000000000000000000000000000000000000000001",  # row  0
    "1000000000000000000000000000000000000000001",  # row  1
    "1000000000000000000000000000000000000000001",  # row  2
    "1000000000000000000000000000000000000000001",  # row  3
    "1000000000000000000000000000000000000000001",  # row  4
    "100000000000PPPPP00000000000000PPPPP00000001",  # row  5  ← plataformas
    "1000000000000000000000000000000000000000001",  # row  6
    "1000000000000000000000PPPPPPP0000000000000001",  # row  7  ← plataforma
    "1000000000000000000000000000000000000000001",  # row  8
    "100000PPPPP000000000000000000000PPPPP000000001",  # row  9  ← plataformas
    "1000000000000000000000000000000000000000001",  # row 10
    "1000000000000000000000000000000000000000001",  # row 10
    "1000000000000000000000000000000000000000001",  # row 10
    "1000000000000000000000000000000000000000001",  # row 10
    "1000000000000000000000000000000000000000001",  # row 10
    "1000000000000000000000000000000000000000001",  # row 10
    "1000000000000000000000000000000000000000001",  # row 10
    "1000000000000000000000000000000000000000001",  # row 11
    "1000000000000000000000000000000000000000001",  # row 13
    "100PPPP000000000000000PPPPPP00000000000PPPP001",  # row 12  ← plataformas
    "1000000000000000000000000000000000000000001",  # row 14
    "1111000000000000011110000000000001111000000001",  # row 15  ← degraus
    "1111111111111111111111111111111111111111111111",  # row 16  ← chão
    "1111111111111111111111111111111111111111111111",  # row 17
    "1111111111111111111111111111111111111111111111",  # row 18
    "1111111111111111111111111111111111111111111111",  # row 19
]


class Level:
    def __init__(self) -> None:
        # Normaliza largura: todas as linhas devem ter o mesmo comprimento
        max_cols = max(len(row) for row in _MAP)
        self.map_data: list[str] = [row.ljust(max_cols, "0") for row in _MAP]

        self.colliders: list[Collider] = []
        self._build_colliders()

    # ------------------------------------------------------------------
    # Construção dos colliders tipados
    # ------------------------------------------------------------------

    def _build_colliders(self) -> None:
        for row_idx, row in enumerate(self.map_data):
            for col_idx, cell in enumerate(row):
                if cell == "0":
                    continue

                one_way = cell == "P"

                self.colliders.append(
                    {
                        "x": col_idx * TILE_SIZE,
                        "y": row_idx * TILE_SIZE,
                        "w": TILE_SIZE,
                        "h": TILE_SIZE,
                        "one_way": one_way,
                    }
                )

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
                if cell == "0":
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
