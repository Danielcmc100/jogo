from src.engine.renderer import Renderer
from src.engine.physics import Rect, check_collision
from src.game.settings import (
    FIRE_FRAME_WIDTH,
    FIRE_FRAME_HEIGHT,
    FIRE_TEX_WIDTH,
    FIRE_TEX_HEIGHT,
    FIRE_ANIMATIONS,
    FIREBALL_SPEED,
    LOGICAL_WIDTH,
    LOGICAL_HEIGHT,
)


class Fireball:
    """Bola de fogo cuspida pela cobra.

    Parâmetros
    ----------
    x, y:
        Posição inicial (canto superior-esquerdo do sprite).
    direction:
        +1.0 voa para a direita, -1.0 voa para a esquerda.
    """

    def __init__(self, x: float, y: float, direction: float) -> None:
        self.x = x
        self.y = y
        self.vx = FIREBALL_SPEED * direction
        self.direction = direction
        self.alive = True

        # Animação
        _row, _num_frames, fps = FIRE_ANIMATIONS["fly"]
        self._frame_duration = 1.0 / fps
        self.anim_timer = 0.0
        self.current_frame = 0

    def get_rect(self) -> Rect:
        return {
            "x": self.x,
            "y": self.y,
            "w": float(FIRE_FRAME_WIDTH),
            "h": float(FIRE_FRAME_HEIGHT),
        }

    def update(self, dt: float, tiles: list[Rect]) -> None:
        if not self.alive:
            return

        # Movimento
        self.x += self.vx * dt

        # Colisão com tiles → destruir
        fb_rect = self.get_rect()
        for tile in tiles:
            if check_collision(fb_rect, tile):
                self.alive = False
                return

        # Sair da área visível → destruir
        if self.x + FIRE_FRAME_WIDTH < 0 or self.x > LOGICAL_WIDTH * 4:
            self.alive = False
            return

        # Avança animação em loop
        row, num_frames, _fps = FIRE_ANIMATIONS["fly"]
        self.anim_timer += dt
        if self.anim_timer >= self._frame_duration:
            self.anim_timer -= self._frame_duration
            self.current_frame = (self.current_frame + 1) % num_frames

    def render(self, renderer: Renderer) -> None:
        if not self.alive:
            return

        row, num_frames, _fps = FIRE_ANIMATIONS["fly"]
        col = self.current_frame

        uv_w = FIRE_FRAME_WIDTH / FIRE_TEX_WIDTH
        uv_h = FIRE_FRAME_HEIGHT / FIRE_TEX_HEIGHT
        uv_x = col * uv_w
        uv_y = row * uv_h

        # Espelha o sprite se estiver indo para a esquerda
        if self.direction < 0:
            uv_x += uv_w
            uv_w = -uv_w

        renderer.draw_sprite(
            "fireball",
            self.x,
            self.y,
            FIRE_FRAME_WIDTH,
            FIRE_FRAME_HEIGHT,
            uv_x,
            uv_y,
            uv_w,
            uv_h,
        )
