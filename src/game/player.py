import pygame
from src.engine.renderer import Renderer
from src.engine.physics import Rect, Collider, check_collision
from src.game.settings import (
    PLAYER_FRAME_WIDTH,
    PLAYER_FRAME_HEIGHT,
    PLAYER_SPEED,
    JUMP_FORCE,
    GRAVITY,
    PLAYER_TEX_WIDTH,
    PLAYER_TEX_HEIGHT,
    PLAYER_ANIMATIONS,
    PLAYER_MAX_HP,
    PLAYER_INVINCIBILITY_TIME,
    PLAYER_ATTACK_W,
    PLAYER_ATTACK_H,
    PLAYER_ATTACK_ACTIVE_FRAMES,
)


class Player:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        # Hitbox reduzida para o player transitar melhor por tiles menores (ex: 16x16)
        self.w = PLAYER_FRAME_WIDTH * 0.6  # pouco mais fino no eixo X
        self.h = 16.0                      # altura focada nas pernas/pés

        self.vx = 0.0
        self.vy = 0.0

        self.is_grounded = False
        self.facing_right = True

        # Animation state — valid keys match PLAYER_ANIMATIONS in settings.py
        self.state = "idle"
        self.anim_timer = 0.0
        self.current_frame = 0

        self.max_hp: int = PLAYER_MAX_HP
        self.hp: int = PLAYER_MAX_HP
        # Tempo de invencibilidade restante após tomar dano
        self._invincibility_timer: float = 0.0

        # Estado de ataque
        self._attacking: bool = False       # True enquanto a animação de ataque corre
        self._attack_pressed: bool = False  # edge-trigger: evita auto-repetição

    @property
    def is_dead(self) -> bool:
        return self.hp <= 0

    @property
    def is_invincible(self) -> bool:
        return self._invincibility_timer > 0.0

    def get_rect(self) -> Rect:
        offset_x = (PLAYER_FRAME_WIDTH - self.w) / 2
        offset_y = PLAYER_FRAME_HEIGHT - self.h  # Align to bottom
        return {"x": self.x + offset_x, "y": self.y + offset_y, "w": self.w, "h": self.h}

    def get_attack_rect(self) -> Rect | None:
        """Retorna a hitbox da espada se o frame atual for ativo, ou None."""
        if not self._attacking:
            return None
        if self.current_frame not in PLAYER_ATTACK_ACTIVE_FRAMES:
            return None
        # Hitbox à frente do player, na altura do tronco
        rect_y = self.y + (PLAYER_FRAME_HEIGHT - PLAYER_ATTACK_H) / 2
        if self.facing_right:
            rect_x = self.x + PLAYER_FRAME_WIDTH
        else:
            rect_x = self.x - PLAYER_ATTACK_W
        return {"x": rect_x, "y": rect_y, "w": float(PLAYER_ATTACK_W), "h": float(PLAYER_ATTACK_H)}

    def update(self, dt: float, tiles: list[Collider], keys: pygame.key.ScancodeWrapper) -> None:
        # --- Input ---
        # Edge-trigger para o ataque: só inicia no frame que Z é pressionado
        z_held = keys[pygame.K_z]
        if z_held and not self._attack_pressed and not self._attacking:
            self._attacking = True
            self.state = "attack"
            self.current_frame = 0
            self.anim_timer = 0.0
        self._attack_pressed = z_held

        # Movimento horizontal — bloqueado durante o ataque
        if not self._attacking:
            self.vx = 0.0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.vx = -PLAYER_SPEED
                self.facing_right = False
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vx = PLAYER_SPEED
                self.facing_right = True
        else:
            self.vx = 0.0  # congela X durante o ataque

        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.is_grounded:
            self.vy = JUMP_FORCE
            self.is_grounded = False

        # --- Physics ---
        self.vy += GRAVITY * dt

        # Decrementa invencibilidade
        if self._invincibility_timer > 0.0:
            self._invincibility_timer = max(0.0, self._invincibility_timer - dt)

        # Integration & X Collision
        self.x += self.vx * dt
        player_rect = self.get_rect()
        for tile in tiles:
            # Plataformas one-way não bloqueiam lateralmente
            if tile.get("one_way", False):
                continue
            if check_collision(player_rect, tile):
                if self.vx > 0:
                    self.x = tile["x"] - self.w - (PLAYER_FRAME_WIDTH - self.w) / 2
                elif self.vx < 0:
                    self.x = tile["x"] + tile["w"] - (PLAYER_FRAME_WIDTH - self.w) / 2
                self.vx = 0
                player_rect = self.get_rect()

        # Integration & Y Collision
        self.y += self.vy * dt
        self.is_grounded = False
        player_rect = self.get_rect()
        for tile in tiles:
            if tile.get("one_way", False):
                # One-way: só colide descendo E se o player vinha de cima
                if self.vy <= 0:
                    continue
                # O pé do player deve ter estado acima do topo do tile antes do passo
                if (player_rect["y"] + player_rect["h"] - self.vy * dt) > tile["y"]:
                    continue
            if check_collision(player_rect, tile):
                if self.vy > 0:
                    self.y = tile["y"] - PLAYER_FRAME_HEIGHT
                    self.is_grounded = True
                elif self.vy < 0:
                    self.y = tile["y"] + tile["h"] - (PLAYER_FRAME_HEIGHT - self.h)
                self.vy = 0
                player_rect = self.get_rect()

        # --- Animation State ---
        if not self._attacking:
            # Estado normal: jump > walk > idle
            new_state: str
            if not self.is_grounded:
                new_state = "jump"
            elif abs(self.vx) > 0.01:
                new_state = "walk"
            else:
                new_state = "idle"

            if new_state != self.state:
                self.state = new_state
                self.current_frame = 0
                self.anim_timer = 0.0

        # Avança animação
        _row, num_frames, fps = PLAYER_ANIMATIONS[self.state]
        frame_duration = 1.0 / fps
        self.anim_timer += dt
        if self.anim_timer >= frame_duration:
            self.anim_timer -= frame_duration
            next_frame = self.current_frame + 1
            if self._attacking and next_frame >= num_frames:
                # Animação de ataque terminou
                self._attacking = False
                self.state = "idle"
                self.current_frame = 0
                self.anim_timer = 0.0
            else:
                self.current_frame = next_frame % num_frames

    def render(self, renderer: Renderer) -> None:
        import math
        # Look up the row and total frame count from the animation definition
        row, _num_frames, _fps = PLAYER_ANIMATIONS[self.state]
        col = self.current_frame

        # Compute normalised UV rect for this frame within the sheet
        uv_w = PLAYER_FRAME_WIDTH / PLAYER_TEX_WIDTH
        uv_h = PLAYER_FRAME_HEIGHT / PLAYER_TEX_HEIGHT
        uv_x = col * uv_w
        uv_y = row * uv_h

        if not self.facing_right:
            uv_x += uv_w
            uv_w = -uv_w

        # Flash vermelho durante invencibilidade — pisca a 10 Hz
        tint: tuple[float, float, float, float] | None = None
        if self.is_invincible:
            # alterna entre flash e normal a cada 0.05s
            phase = math.fmod(self._invincibility_timer, 0.1)
            if phase < 0.05:
                tint = (1.0, 0.0, 0.0, 0.72)  # vermelho intenso

        renderer.draw_sprite(
            "player",
            self.x,
            self.y,
            PLAYER_FRAME_WIDTH,
            PLAYER_FRAME_HEIGHT,
            uv_x,
            uv_y,
            uv_w,
            uv_h,
            tint=tint,
        )

    def take_damage(self, amount: int, knockback_vx: float = 0.0) -> bool:
        """Aplica dano. Retorna True se o dano foi efetivado (não invencível)."""
        if self.is_invincible or self.is_dead:
            return False
        self.hp = max(0, self.hp - amount)
        self._invincibility_timer = PLAYER_INVINCIBILITY_TIME
        if knockback_vx != 0.0:
            self.vx = knockback_vx
            self.vy = -180.0  # pequeno salto de knockback
        return True

    def heal(self, amount: int) -> None:
        self.hp = min(self.max_hp, self.hp + amount)

    def reset(self, x: float, y: float) -> None:
        """Reinicia o player para um novo jogo."""
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = self.max_hp
        self._invincibility_timer = 0.0
        self._attacking = False
        self._attack_pressed = False
        self.state = "idle"
        self.current_frame = 0
        self.anim_timer = 0.0
