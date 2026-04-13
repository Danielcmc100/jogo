from src.engine.renderer import Renderer
from src.engine.physics import Rect
from src.game.settings import (
    TILE_SIZE,
    TILE_FRAME_WIDTH,
    TILE_FRAME_HEIGHT,
    TILE_TEX_WIDTH,
    TILE_TEX_HEIGHT,
    SOLID_TILE_COL,
    SOLID_TILE_ROW,
)

class Level:
    def __init__(self):
        # 1 = solid ground, 0 = empty
        # A simple level layout
        self.map_data = [
            "1000000000000000000000001",
            "1000000000000000000000001",
            "1000000000000000000000001",
            "1000000000000000000000001",
            "1000000000000000000000001",
            "1000000000000000000000001",
            "1000000000111111000000001",
            "1000000000000000000000001",
            "1000011100000000001111001",
            "1000000000000000000000001",
            "1111000000011000000000001",
            "1111111111111111111111111",
            "1111111111111111111111111",
            "1111111111111111111111111",
            "1111111111111111111111111",
        ]
        
        self.colliders: list[Rect] = []
        self._build_colliders()
        
    def _build_colliders(self) -> None:
        for y, row in enumerate(self.map_data):
            for x, cell in enumerate(row):
                if cell == '1':
                    self.colliders.append({
                        'x': x * TILE_SIZE,
                        'y': y * TILE_SIZE,
                        'w': TILE_SIZE,
                        'h': TILE_SIZE
                    })
                    
    def render(self, renderer: Renderer) -> None:
        # Compute UV rect for the solid tile defined in settings.py
        uv_w = TILE_FRAME_WIDTH / TILE_TEX_WIDTH
        uv_h = TILE_FRAME_HEIGHT / TILE_TEX_HEIGHT
        uv_x = SOLID_TILE_COL * uv_w
        uv_y = SOLID_TILE_ROW * uv_h

        for row_idx, row in enumerate(self.map_data):
            for col_idx, cell in enumerate(row):
                if cell == "1":
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
