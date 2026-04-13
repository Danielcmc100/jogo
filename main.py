import pygame
from src.engine.window import Window
from src.game.settings import SCREEN_WIDTH, SCREEN_HEIGHT, LOGICAL_WIDTH, LOGICAL_HEIGHT
from src.game.player import Player
from src.game.level import Level
from src.game.background import Background
from src.game.snake import Snake
from src.game.ui import HealthBar


def main():
    window = Window(
        "2D Platformer", SCREEN_WIDTH, SCREEN_HEIGHT, LOGICAL_WIDTH, LOGICAL_HEIGHT
    )

    # Load textures
    window.renderer.load_texture("player", "sprites/Character/char_panda.png")
    window.renderer.load_texture("tile", "sprites/Tiles/new_tle.png")
    window.renderer.load_texture("bg_2", "sprites/Background/bg_2.png")
    window.renderer.load_texture("bg_3", "sprites/Background/bg_3.png")
    window.renderer.load_texture("bg_4", "sprites/Background/bg_4.png")
    window.renderer.load_texture("snake", "sprites/NPC/Enemy/npc_snake.png")
    window.renderer.load_texture("fireball", "sprites/NPC/Enemy/npc_fire1.png")

    # UI Textures (Health Bar)
    for i in range(5):
        window.renderer.load_texture(f"ui_hp_{i}", f"sprites/UI/ui_hp_{i}.png")

    # Game objects
    player = Player(100, 100)
    level = Level()
    background = Background()
    # Duas cobras com patrulhas distintas no mapa
    snakes: list[Snake] = [
        Snake(x=320, y=288, patrol_left=288, patrol_right=448),
        Snake(x=544, y=256, patrol_left=480, patrol_right=640),
    ]
    health_bar = HealthBar(10, 10, scale=2.0)  # Top-left with some scale

    while window.running:
        # Input & Events
        window.poll_events()
        keys = pygame.key.get_pressed()

        # Test damage with 'K' key
        for event in window.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_k:
                    player.take_damage(1)
                if event.key == pygame.K_l:
                    player.heal(1)

        # Update
        player.update(window.dt, level.colliders, keys)
        player_rect = player.get_rect()
        for snake in snakes:
            hit = snake.update(
                window.dt, level.colliders, player.x, player.y, player_rect
            )
            if hit:
                # Knockback: empurra o player para longe da cobra
                snake_cx = snake.x + snake.get_rect()["w"] / 2
                player.vx = 150.0 if player.x + player.w / 2 >= snake_cx else -150.0
                player.take_damage(1)

        # Camera Follow Player
        # We want the player roughly in the center
        target_cam_x = player.x - LOGICAL_WIDTH / 2.0 + player.w / 2.0
        target_cam_y = player.y - LOGICAL_HEIGHT / 2.0 + player.h / 2.0

        # Smooth camera lerp
        window.renderer.camera_x += (
            (target_cam_x - window.renderer.camera_x) * 5.0 * window.dt
        )
        window.renderer.camera_y += (
            (target_cam_y - window.renderer.camera_y) * 5.0 * window.dt
        )

        # Render
        window.clear()

        background.render(
            window.renderer, window.renderer.camera_x, window.renderer.camera_y
        )
        level.render(window.renderer)
        for snake in snakes:
            snake.render(window.renderer)
        player.render(window.renderer)

        # UI Layer (rendered last)
        health_bar.render(window.renderer, player.hp)

        window.swap_buffers()
        window.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
