from src.engine.renderer import Renderer
from src.game.settings import LOGICAL_WIDTH, LOGICAL_HEIGHT

class Background:
    def __init__(self):
        # We assume the background textures are as big as screen for simplicity, 
        # but bg_2, bg_3, bg_4 are 256x144, so we'll scale them up to fit.
        # Parallax config: (texture_name, scroll_factor)
        self.layers = [
            ("bg_2", 0.2), # Furthest layer (scrolls slow)
            ("bg_3", 0.5), # Middle layer
            ("bg_4", 0.8)  # Closest layer (scrolls fast)
        ]

    def render(self, renderer: Renderer, cam_x: float, cam_y: float) -> None:
        for tex_name, scroll_factor in self.layers:
            # We want to scroll the UV coordinates or draw repeating tiles to create 
            # a continuous scrolling effect, but since we use simple quad rendering,
            # drawing two quads side by side will simulate scrolling easily.
            
            # Simple offset calculation based on camera
            offset_x = (cam_x * scroll_factor) % LOGICAL_WIDTH
            
            # Keeping Y locked to screen for now or simple scroll
            
            # Draw first quad
            renderer.draw_sprite(
                tex_name, 
                cam_x - offset_x, cam_y, 
                LOGICAL_WIDTH, LOGICAL_HEIGHT
            )
            # Draw second quad for wrap around
            renderer.draw_sprite(
                tex_name, 
                cam_x - offset_x + LOGICAL_WIDTH, cam_y, 
                LOGICAL_WIDTH, LOGICAL_HEIGHT
            )
