from src.engine.renderer import Renderer

class HealthBar:
    def __init__(self, x: float, y: float, scale: float = 1.0):
        self.x = x
        self.y = y
        self.scale = scale
        
    def render(self, renderer: Renderer, hp: int) -> None:
        # Texture name mapping: ui_hp_0, ui_hp_1, etc.
        hp_clamped = max(0, min(4, int(hp)))
        texture_name = f"ui_hp_{hp_clamped}"
        
        # Get texture dimensions for scaling
        if texture_name in renderer.textures:
            tex = renderer.textures[texture_name]
            # Ensure integer dimensions for pixel perfection
            scale_int = int(self.scale)
            w = int(tex["width"] * scale_int)
            h = int(tex["height"] * scale_int)
            
            renderer.draw_ui_sprite(
                texture_name,
                int(self.x),
                int(self.y),
                w,
                h
            )
