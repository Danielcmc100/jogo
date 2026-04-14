"""UI — barra de vida e tela de Game Over.

Sprites de HP
-------------
ui_hp_0.png … ui_hp_5.png — cada arquivo é 32×16 px (sprite único, sem atlas).
O número no nome corresponde diretamente ao valor de hp:
  hp=5 → ui_hp_5  (vida cheia)
  hp=0 → ui_hp_0  (morto)

GameOverScreen / HudInfo
--------------
Renderiza texturas geradas dinamicamente via Pygame.
"""
from __future__ import annotations

import pygame
import OpenGL.GL as gl

from src.engine.renderer import Renderer
from src.game.settings import LOGICAL_WIDTH, LOGICAL_HEIGHT, PLAYER_MAX_HP

# Tamanho real de cada sprite de HP (pixels lógicos)
HP_SPRITE_W = 32
HP_SPRITE_H = 16


class HealthBar:
    """Exibe o sprite de vida correspondente ao HP atual do player.

    Parâmetros
    ----------
    screen_x, screen_y:
        Posição fixa na tela lógica (não afetada pela câmera).
    scale:
        Multiplicador de escala de exibição (default 2 → 64×32 px).
    """

    def __init__(self, screen_x: int, screen_y: int, scale: float = 2.0) -> None:
        self.screen_x = screen_x
        self.screen_y = screen_y
        self.scale = scale

    def render(self, renderer: Renderer, hp: int) -> None:
        hp_clamped = max(0, min(PLAYER_MAX_HP, hp))
        tex_name = f"ui_hp_{hp_clamped}"

        w = HP_SPRITE_W * self.scale
        h = HP_SPRITE_H * self.scale

        # Renderiza em coordenada de tela fixa (camera zerada temporariamente)
        cam_x_bkp = renderer.camera_x
        cam_y_bkp = renderer.camera_y
        renderer.camera_x = 0.0
        renderer.camera_y = 0.0

        renderer.draw_sprite(tex_name, self.screen_x, self.screen_y, w, h)

        renderer.camera_x = cam_x_bkp
        renderer.camera_y = cam_y_bkp


class GameOverScreen:
    """Sobreposição de Game Over renderizada sobre o jogo.

    Gera uma textura com o texto via Pygame Surface e a envia ao renderer
    OpenGL na primeira chamada. Reutilizada nos frames seguintes.
    """

    _TEX_NAME = "_game_over_overlay"

    def __init__(self) -> None:
        self._built = False

    def _build(self, renderer: Renderer) -> None:
        """Gera o overlay como textura OpenGL via Pygame."""
        w = LOGICAL_WIDTH
        h = LOGICAL_HEIGHT

        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 180))  # fundo escuro semi-transparente

        try:
            font_big   = pygame.font.SysFont("Arial", 18, bold=True)
            font_small = pygame.font.SysFont("Arial", 9)
        except Exception:
            font_big   = pygame.font.Font(None, 18)
            font_small = pygame.font.Font(None, 9)

        lbl_over    = font_big.render("GAME OVER", True, (230, 60, 60))
        lbl_restart = font_small.render("Aperte  R  para reiniciar", True, (220, 220, 220))

        cx, cy = w // 2, h // 2
        surf.blit(lbl_over,    lbl_over.get_rect(center=(cx, cy - 16)))
        surf.blit(lbl_restart, lbl_restart.get_rect(center=(cx, cy + 10)))

        img_data = pygame.image.tostring(surf, "RGBA", True)
        tex_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexImage2D(
            gl.GL_TEXTURE_2D, 0, gl.GL_RGBA,
            w, h, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, img_data,
        )

        renderer.textures[self._TEX_NAME] = {"id": tex_id, "width": w, "height": h}
        self._built = True

    def render(self, renderer: Renderer) -> None:
        if not self._built:
            self._build(renderer)

        cam_x_bkp = renderer.camera_x
        cam_y_bkp = renderer.camera_y
        renderer.camera_x = 0.0
        renderer.camera_y = 0.0

        renderer.draw_sprite(
            self._TEX_NAME,
            0.0, 0.0,
            float(LOGICAL_WIDTH),
            float(LOGICAL_HEIGHT),
        )

        renderer.camera_x = cam_x_bkp
        renderer.camera_y = cam_y_bkp

class HudInfo:
    """Renderiza a pontuação e a fase atual na tela.
    Gera as texturas apenas quando seus valores mudam para otimizar.
    """
    _TEX_NAME = "_hud_info_overlay"

    def __init__(self) -> None:
        self.last_score = -1
        self.last_level = -1
        
    def render(self, renderer: Renderer, score: int, level: int) -> None:
        if score != self.last_score or level != self.last_level:
            self._build(renderer, score, level)
            self.last_score = score
            self.last_level = level

        cam_x_bkp = renderer.camera_x
        cam_y_bkp = renderer.camera_y
        renderer.camera_x = 0.0
        renderer.camera_y = 0.0

        renderer.draw_sprite(
            self._TEX_NAME,
            0.0, 0.0,
            float(LOGICAL_WIDTH),
            float(LOGICAL_HEIGHT),
        )

        renderer.camera_x = cam_x_bkp
        renderer.camera_y = cam_y_bkp

    def _build(self, renderer: Renderer, score: int, level: int) -> None:
        w = LOGICAL_WIDTH
        h = LOGICAL_HEIGHT
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        try:
            font = pygame.font.SysFont("Arial", 12, bold=True)
        except Exception:
            font = pygame.font.Font(None, 12)

        lbl_score = font.render(f"Pontos: {score}", True, (255, 255, 0))
        lbl_level = font.render(f"Fase: {level + 1}", True, (255, 255, 255))

        # Posiciona no canto superior direito
        surf.blit(lbl_score, (w - lbl_score.get_width() - 10, 10))
        surf.blit(lbl_level, (w - lbl_level.get_width() - 10, 25))

        img_data = pygame.image.tostring(surf, "RGBA", True)
        
        # Reaproveita ID ou gera novo
        if self._TEX_NAME in renderer.textures:
            tex_id = renderer.textures[self._TEX_NAME]["id"]
            gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
            gl.glTexImage2D(
                gl.GL_TEXTURE_2D, 0, gl.GL_RGBA,
                w, h, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, img_data,
            )
        else:
            tex_id = gl.glGenTextures(1)
            gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
            gl.glTexImage2D(
                gl.GL_TEXTURE_2D, 0, gl.GL_RGBA,
                w, h, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, img_data,
            )
            renderer.textures[self._TEX_NAME] = {"id": tex_id, "width": w, "height": h}
