import pygame
from src.engine.renderer import Renderer
from src.engine.physics import Rect, check_collision
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
)


class Player:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        # We define a slightly smaller hitbox than the frame for better platforming
        self.w = PLAYER_FRAME_WIDTH * 0.8
        self.h = PLAYER_FRAME_HEIGHT * 0.8

        self.vx = 0.0
        self.vy = 0.0

        self.is_grounded = False
        self.facing_right = True

        # Animation state — valid keys match PLAYER_ANIMATIONS in settings.py
        self.state = "idle"
        self.anim_timer = 0.0
        self.current_frame = 0

        self.max_hp = PLAYER_MAX_HP
        self.hp = PLAYER_MAX_HP

    def get_rect(self) -> Rect:
        # Give a little offset to center the hitbox horizontally
        offset_x = (PLAYER_FRAME_WIDTH - self.w) / 2
        offset_y = PLAYER_FRAME_HEIGHT - self.h  # Align to bottom
        return {"x": self.x + offset_x, "y": self.y + offset_y, "w": self.w, "h": self.h}

    def update(self, dt: float, tiles: list[Rect], keys: pygame.key.ScancodeWrapper) -> None:
        # --- Input ---
        self.vx = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -PLAYER_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = PLAYER_SPEED
            self.facing_right = True

        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.is_grounded:
            self.vy = JUMP_FORCE
            self.is_grounded = False

        # --- Physics ---
        self.vy += GRAVITY * dt

        # Integration & X Collision
        self.x += self.vx * dt
        player_rect = self.get_rect()
        for tile in tiles:
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
            if check_collision(player_rect, tile):
                if self.vy > 0:
                    self.y = tile["y"] - PLAYER_FRAME_HEIGHT
                    self.is_grounded = True
                elif self.vy < 0:
                    self.y = tile["y"] + tile["h"] - (PLAYER_FRAME_HEIGHT - self.h)
                self.vy = 0
                player_rect = self.get_rect()

        # --- Animation State ---
        new_state: str
        if not self.is_grounded:
            new_state = "jump"
        elif abs(self.vx) > 0.01:
            new_state = "walk"
        else:
            new_state = "idle"

        # Reset frame counter when the animation state changes
        if new_state != self.state:
            self.state = new_state
            self.current_frame = 0
            self.anim_timer = 0.0

        # Advance frame based on the FPS defined in PLAYER_ANIMATIONS
        _row, num_frames, fps = PLAYER_ANIMATIONS[self.state]
        frame_duration = 1.0 / fps

        self.anim_timer += dt
        if self.anim_timer >= frame_duration:
            self.anim_timer -= frame_duration
            self.current_frame = (self.current_frame + 1) % num_frames

    def render(self, renderer: Renderer) -> None:
        # Look up the row and total frame count from the animation definition
        row, _num_frames, _fps = PLAYER_ANIMATIONS[self.state]
        col = self.current_frame

        # Compute normalised UV rect for this frame within the sheet
        uv_w = PLAYER_FRAME_WIDTH / PLAYER_TEX_WIDTH
        uv_h = PLAYER_FRAME_HEIGHT / PLAYER_TEX_HEIGHT
        uv_x = col * uv_w
        uv_y = row * uv_h

        if not self.facing_right:
            # Flip horizontally by shifting uv_x to the right edge and negating width
            uv_x += uv_w
            uv_w = -uv_w

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
        )

    def take_damage(self, amount: int) -> None:
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0
            
    def heal(self, amount: int) -> None:
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
