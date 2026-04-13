from src.engine.renderer import Renderer
from src.engine.physics import Rect
from src.game.settings import (
    TILE_SIZE,
    TILE_FRAME_WIDTH,
    TILE_FRAME_HEIGHT,
    TILE_TEX_WIDTH,
    TILE_TEX_HEIGHT,
)

class Level:
    def __init__(self):
        # 1 = solid ground, 0 = empty
        # A simple level layout
        self.map_data = [
            "0000000000000000000000000",
            "0000000000000000000000000",
            "0000000000000000000000000",
            "0000000000000000000000000",
            "0000000000000000000000000",
            "0000000000000000000000000",
            "0000000000111111000000000",
            "0000000000000000000000000",
            "0000011100000000001111000",
            "0000000000000000000000000",
            "0111000000011000000000000",
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
        # For new_tle.png, we just use a small portion of it (e.g. top-left tile at 0,0)
        uv_w = TILE_FRAME_WIDTH / TILE_TEX_WIDTH
        uv_h = TILE_FRAME_HEIGHT / TILE_TEX_HEIGHT
        
        uv_x = 0.0
        uv_y = 0.0
        
        for y, row in enumerate(self.map_data):
            for x, cell in enumerate(row):
                if cell == '1':
                    renderer.draw_sprite(
                        "tile", 
                        x * TILE_SIZE, y * TILE_SIZE, 
                        TILE_SIZE, TILE_SIZE,
                        uv_x, uv_y, uv_w, uv_h
                    )
