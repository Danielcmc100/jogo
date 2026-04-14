import pygame
from src.engine.window import Window
from src.game.settings import SCREEN_WIDTH, SCREEN_HEIGHT, LOGICAL_WIDTH, LOGICAL_HEIGHT
from src.game.player import Player
from src.game.level import Level, LEVELS
from src.game.background import Background
from src.game.snake import Snake
from src.game.ui import HealthBar, GameOverScreen, HudInfo, LevelTransitionScreen

def load_stage(level_idx: int) -> tuple[Level, list[Snake], Player]:
    level = Level(level_idx)
    snakes = level.snakes
    # Certifique-se de não referenciar os mesmos objetos antigos
    player = Player(level.spawn_x, level.spawn_y)
    return level, snakes, player

def main() -> None:
    window = Window(
        "2D Platformer", SCREEN_WIDTH, SCREEN_HEIGHT, LOGICAL_WIDTH, LOGICAL_HEIGHT
    )

    # ── Texturas ────────────────────────────────────────────────────────
    window.renderer.load_texture("player", "sprites/Character/char_panda.png")
    window.renderer.load_texture("tile", "sprites/Tiles/new_tle.png")
    window.renderer.load_texture("bg_2", "sprites/Background/bg_2.png")
    window.renderer.load_texture("bg_3", "sprites/Background/bg_3.png")
    window.renderer.load_texture("bg_4", "sprites/Background/bg_4.png")
    window.renderer.load_texture("snake", "sprites/NPC/Enemy/npc_snake.png")
    window.renderer.load_texture("fireball", "sprites/NPC/Enemy/npc_fire1.png")

    # Sprites de HP
    for i in range(6):
        window.renderer.load_texture(f"ui_hp_{i}", f"sprites/UI/ui_hp_{i}.png")

    # ── Estado do Jogo ──────────────────────────────────────────────────
    score = 0
    current_level_idx = 0
    game_over = False

    level, snakes, player = load_stage(current_level_idx)
    background = Background()

    # ── UI ──────────────────────────────────────────────────────────────
    health_bar = HealthBar(screen_x=8, screen_y=8, scale=2.0)
    game_over_scr = GameOverScreen()
    hud_info = HudInfo()
    transition_scr = LevelTransitionScreen()

    is_transitioning = False
    transition_timer = 0.0

    # ── Loop principal ──────────────────────────────────────────────────
    while window.running:
        window.poll_events()
        keys = pygame.key.get_pressed()

        # ── Eventos de teclado ─────────────────────────────────────────
        for event in window.events:
            if event.type == pygame.KEYDOWN:
                # Reiniciar (R) — funciona só em game over
                if event.key == pygame.K_r and game_over:
                    score = 0
                    current_level_idx = 0
                    level, snakes, player = load_stage(current_level_idx)
                    window.renderer.camera_x = 0.0
                    window.renderer.camera_y = 0.0
                    game_over = False

                # Teclas de debug
                if event.key == pygame.K_k:
                    player.take_damage(1)
                if event.key == pygame.K_l:
                    player.heal(1)
                # Skip level para debug
                if event.key == pygame.K_n:
                    player.x = level.width_px + 10

        # ── Update ─────────────────────────────────────────────────────
        if is_transitioning:
            transition_timer -= window.dt
            if transition_timer <= 0.0:
                current_level_idx += 1
                if current_level_idx >= len(LEVELS):
                    current_level_idx = 0
                
                level, snakes, new_player = load_stage(current_level_idx)
                new_player.hp = player.hp # mantém hp do player
                player = new_player
                is_transitioning = False
                
                window.renderer.camera_x = 0.0
                window.renderer.camera_y = 0.0

        elif not game_over:
            player.update(window.dt, level.colliders, keys)
            player_rect = player.get_rect()
            attack_rect = player.get_attack_rect()

            for snake in snakes:
                hit = snake.update(
                    window.dt, level.colliders, player.x, player.y, player_rect
                )
                
                # Toque direto com a cobra
                if hit:
                    snake_cx = snake.x + snake.get_rect()["w"] / 2
                    kb = 160.0 if player.x + player.w / 2 >= snake_cx else -160.0
                    player.take_damage(1, knockback_vx=kb)

                # Colisão com fireballs da cobra
                for fb in snake.fireballs:
                    if fb.alive:
                        from src.engine.physics import check_collision
                        if check_collision(player_rect, fb.get_rect()):
                            fb.alive = False
                            kb = 120.0 if fb.vx > 0 else -120.0
                            player.take_damage(1, knockback_vx=kb)

                # Espada do player acertou a cobra?
                if attack_rect is not None:
                    from src.engine.physics import check_collision
                    if check_collision(attack_rect, snake.get_rect()):
                        if snake.take_hit(1):
                            # Se o hit matou a cobra (tava viva e agora hp <= 0)
                            if not snake.alive:
                                score += 100

            # Remove cobras mortas
            snakes = [s for s in snakes if s.alive]

            # Fim do jogo?
            if player.is_dead:
                game_over = True

            # Condição de passar de fase: todos os inimigos da tela mortos
            # Para evitar que fases sem cobra passem automaticamente e se limitem à ação do player,
            # Se não quiser que fases sem cobra passem imediatamente, precisaria checar len(level.snakes) > 0 também.
            if len(snakes) == 0 and not is_transitioning:
                is_transitioning = True
                transition_timer = 2.0  # Mensagem de 2 segundos
                 
            # ── Câmera — clamped nos limites do mapa ───────────────────
            target_cam_x = player.x - LOGICAL_WIDTH / 2.0 + player.w / 2.0
            target_cam_y = player.y - LOGICAL_HEIGHT / 2.0 + player.h / 2.0

            max_cam_x = max(0.0, float(level.width_px - LOGICAL_WIDTH))
            max_cam_y = max(0.0, float(level.height_px - LOGICAL_HEIGHT))
            
            target_cam_x = max(0.0, min(target_cam_x, max_cam_x))
            target_cam_y = max(0.0, min(target_cam_y, max_cam_y))

            window.renderer.camera_x += (
                (target_cam_x - window.renderer.camera_x) * 5.0 * window.dt
            )
            window.renderer.camera_y += (
                (target_cam_y - window.renderer.camera_y) * 5.0 * window.dt
            )

        # ── Render ─────────────────────────────────────────────────────
        window.clear()

        background.render(
            window.renderer, window.renderer.camera_x, window.renderer.camera_y
        )
        level.render(window.renderer)

        for snake in snakes:
            snake.render(window.renderer)

        player.render(window.renderer)

        # UI — fixada na tela
        health_bar.render(window.renderer, player.hp)
        hud_info.render(window.renderer, score, current_level_idx)

        if is_transitioning:
            transition_scr.render(window.renderer, current_level_idx + 1 if current_level_idx + 1 < len(LEVELS) else 0)

        if game_over:
            game_over_scr.render(window.renderer)

        window.swap_buffers()
        window.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
