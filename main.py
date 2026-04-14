import pygame
from src.engine.window import Window
from src.game.settings import SCREEN_WIDTH, SCREEN_HEIGHT, LOGICAL_WIDTH, LOGICAL_HEIGHT
from src.game.player import Player
from src.game.level import Level
from src.game.background import Background
from src.game.snake import Snake
from src.game.ui import HealthBar, GameOverScreen

# Posição de spawn do player (acima do chão, row 14)
PLAYER_SPAWN_X = 100.0
PLAYER_SPAWN_Y = 464.0


def _make_snakes() -> list[Snake]:
    return [
        Snake(x=320, y=480, patrol_left=288,  patrol_right=480),
        Snake(x=800, y=480, patrol_left=704,  patrol_right=960),
    ]


def main() -> None:
    window = Window(
        "2D Platformer", SCREEN_WIDTH, SCREEN_HEIGHT, LOGICAL_WIDTH, LOGICAL_HEIGHT
    )

    # ── Texturas ────────────────────────────────────────────────────────
    window.renderer.load_texture("player",   "sprites/Character/char_panda.png")
    window.renderer.load_texture("tile",     "sprites/Tiles/new_tle.png")
    window.renderer.load_texture("bg_2",     "sprites/Background/bg_2.png")
    window.renderer.load_texture("bg_3",     "sprites/Background/bg_3.png")
    window.renderer.load_texture("bg_4",     "sprites/Background/bg_4.png")
    window.renderer.load_texture("snake",    "sprites/NPC/Enemy/npc_snake.png")
    window.renderer.load_texture("fireball", "sprites/NPC/Enemy/npc_fire1.png")

    # Sprites de HP — ui_hp_0 (morto) … ui_hp_5 (cheio)
    for i in range(6):
        window.renderer.load_texture(f"ui_hp_{i}", f"sprites/UI/ui_hp_{i}.png")

    # ── Objetos de jogo ─────────────────────────────────────────────────
    player     = Player(PLAYER_SPAWN_X, PLAYER_SPAWN_Y)
    level      = Level()
    background = Background()
    snakes     = _make_snakes()

    # ── UI ──────────────────────────────────────────────────────────────
    health_bar    = HealthBar(screen_x=8, screen_y=8, scale=2.0)
    game_over_scr = GameOverScreen()

    game_over = False  # flag de estado

    # ── Loop principal ──────────────────────────────────────────────────
    while window.running:
        window.poll_events()
        keys = pygame.key.get_pressed()

        # ── Eventos de teclado ─────────────────────────────────────────
        for event in window.events:
            if event.type == pygame.KEYDOWN:
                # Reiniciar (R) — funciona só em game over
                if event.key == pygame.K_r and game_over:
                    player.reset(PLAYER_SPAWN_X, PLAYER_SPAWN_Y)
                    snakes = _make_snakes()
                    window.renderer.camera_x = 0.0
                    window.renderer.camera_y = 0.0
                    game_over = False

                # Teclas de debug (K = dano, L = cura)
                if event.key == pygame.K_k:
                    player.take_damage(1)
                if event.key == pygame.K_l:
                    player.heal(1)

        # ── Update ─────────────────────────────────────────────────────
        if not game_over:
            player.update(window.dt, level.colliders, keys)
            player_rect = player.get_rect()

            for snake in snakes:
                hit = snake.update(
                    window.dt, level.colliders, player.x, player.y, player_rect
                )
                # Toque direto com a cobra
                if hit:
                    snake_cx = snake.x + snake.get_rect()["w"] / 2
                    kb = 160.0 if player.x + player.w / 2 >= snake_cx else -160.0
                    player.take_damage(1, knockback_vx=kb)

                # Colisão do player com fireballs da cobra
                for fb in snake.fireballs:
                    if fb.alive and fb.get_rect() is not None:
                        from src.engine.physics import check_collision
                        if check_collision(player_rect, fb.get_rect()):
                            fb.alive = False   # consome o projétil
                            kb = 120.0 if fb.vx > 0 else -120.0
                            player.take_damage(1, knockback_vx=kb)

            # Game over?
            if player.is_dead:
                game_over = True

            # ── Câmera — clamped nos limites do mapa ───────────────────
            target_cam_x = player.x - LOGICAL_WIDTH  / 2.0 + player.w / 2.0
            target_cam_y = player.y - LOGICAL_HEIGHT / 2.0 + player.h / 2.0

            max_cam_x = level.width_px  - LOGICAL_WIDTH
            max_cam_y = level.height_px - LOGICAL_HEIGHT
            target_cam_x = max(0.0, min(target_cam_x, max_cam_x))
            target_cam_y = max(0.0, min(target_cam_y, max_cam_y))

            window.renderer.camera_x += (target_cam_x - window.renderer.camera_x) * 5.0 * window.dt
            window.renderer.camera_y += (target_cam_y - window.renderer.camera_y) * 5.0 * window.dt

        # ── Render ─────────────────────────────────────────────────────
        window.clear()

        background.render(window.renderer, window.renderer.camera_x, window.renderer.camera_y)
        level.render(window.renderer)

        for snake in snakes:
            snake.render(window.renderer)

        player.render(window.renderer)

        # UI — fixada na tela (câmera zerada internamente)
        health_bar.render(window.renderer, player.hp)

        if game_over:
            game_over_scr.render(window.renderer)

        window.swap_buffers()
        window.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
