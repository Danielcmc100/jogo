import pygame
from src.engine.window import Window
from src.game.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from src.game.player import Player
from src.game.level import Level
from src.game.background import Background

def main():
    window = Window("2D Platformer", SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Load textures
    window.renderer.load_texture("player", "sprites/Character/char_panda.png")
    window.renderer.load_texture("tile", "sprites/Tiles/new_tle.png")
    window.renderer.load_texture("bg_2", "sprites/Background/bg_2.png")
    window.renderer.load_texture("bg_3", "sprites/Background/bg_3.png")
    window.renderer.load_texture("bg_4", "sprites/Background/bg_4.png")
    
    # Game objects
    player = Player(100, 100)
    level = Level()
    background = Background()
    
    while window.running:
        # Input & Events
        window.poll_events()
        keys = pygame.key.get_pressed()
        
        # Update
        player.update(window.dt, level.colliders, keys)
        
        # Camera Follow Player
        # We want the player roughly in the center
        target_cam_x = player.x - SCREEN_WIDTH / 2.0 + player.w / 2.0
        target_cam_y = player.y - SCREEN_HEIGHT / 2.0 + player.h / 2.0
        
        # Smooth camera lerp
        window.renderer.camera_x += (target_cam_x - window.renderer.camera_x) * 5.0 * window.dt
        window.renderer.camera_y += (target_cam_y - window.renderer.camera_y) * 5.0 * window.dt
        
        # Render
        window.clear()
        
        background.render(window.renderer, window.renderer.camera_x, window.renderer.camera_y)
        level.render(window.renderer)
        player.render(window.renderer)
        
        window.swap_buffers()
        window.tick(60)
        
    pygame.quit()

if __name__ == "__main__":
    main()
