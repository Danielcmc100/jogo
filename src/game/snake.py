import math
from src.engine.renderer import Renderer
from src.engine.physics import Rect, Collider, check_collision
from src.game.fireball import Fireball
from src.game.settings import (
    GRAVITY,
    SNAKE_FRAME_WIDTH,
    SNAKE_FRAME_HEIGHT,
    SNAKE_TEX_WIDTH,
    SNAKE_TEX_HEIGHT,
    SNAKE_ANIMATIONS,
    SNAKE_SPEED,
    SNAKE_DETECTION_RANGE,
    SNAKE_ATTACK_RANGE,
    SNAKE_ATTACK_COOLDOWN,
    FIRE_FRAME_WIDTH,
)


class Snake:
    """Inimigo cobra.

    Comportamento
    -------------
    - Respeita gravidade e colide com tiles (anda sobre plataformas).
    - Patrulha um trecho do mapa (patrol_left … patrol_right).
    - Ao detectar o player (SNAKE_DETECTION_RANGE), persegue horizontalmente.
    - Ao entrar em SNAKE_ATTACK_RANGE dispara uma ``Fireball`` (cooldown).
    - Durante o ataque permanece parada mas continua sujeita à física.
    - Colide fisicamente com o player: retorna True em ``update`` quando há
      sobreposição, permitindo que o chamador aplique knockback/dano.

    Nota sobre o sprite atlas
    -------------------------
    npc_snake.png — 72×48, frame 24×24, 3 cols × 2 linhas:
      Linha 0: walk   — cols 0-2  (3 frames)
      Linha 1: attack — cols 0-1  (2 frames)  ← col 2 (canto inf. dir.) ignorada
    """

    def __init__(
        self,
        x: float,
        y: float,
        patrol_left: float,
        patrol_right: float,
    ) -> None:
        self.x = x
        self.y = y
        self.patrol_left = patrol_left
        self.patrol_right = patrol_right

        self.vx: float = SNAKE_SPEED   # começa indo para a direita
        self.vy: float = 0.0
        self.is_grounded = False
        self.facing_right = True

        # Máquina de estados: "walk" | "attack"
        self.state = "walk"
        self.anim_timer = 0.0
        self.current_frame = 0

        # Controle de ataque
        self.attack_cooldown: float = 0.0
        self._attack_fired = False

        # Projéteis vivos
        self.fireballs: list[Fireball] = []

    # ------------------------------------------------------------------
    # Hitbox
    # ------------------------------------------------------------------

    def get_rect(self) -> Rect:
        return {
            "x": self.x,
            "y": self.y,
            "w": float(SNAKE_FRAME_WIDTH),
            "h": float(SNAKE_FRAME_HEIGHT),
        }

    # ------------------------------------------------------------------
    # Helpers de animação / estado
    # ------------------------------------------------------------------

    def _distance_to_player(self, px: float, py: float) -> float:
        cx = self.x + SNAKE_FRAME_WIDTH / 2
        cy = self.y + SNAKE_FRAME_HEIGHT / 2
        return math.hypot(px - cx, py - cy)

    def _set_state(self, new_state: str) -> None:
        if self.state != new_state:
            self.state = new_state
            self.current_frame = 0
            self.anim_timer = 0.0
            if new_state == "attack":
                self._attack_fired = False

    def _advance_animation(self, dt: float) -> None:
        _row, num_frames, fps = SNAKE_ANIMATIONS[self.state]
        self.anim_timer += dt
        frame_duration = 1.0 / fps
        if self.anim_timer >= frame_duration:
            self.anim_timer -= frame_duration
            self.current_frame = (self.current_frame + 1) % num_frames

    # ------------------------------------------------------------------
    # Física — colisão contra tiles no eixo X e Y separadamente,
    # espelhando a lógica do Player para comportamento idêntico.
    # ------------------------------------------------------------------

    def _resolve_x_collision(self, tiles: list[Collider]) -> None:
        snake_rect = self.get_rect()
        for tile in tiles:
            # Plataformas one-way não bloqueiam lateralmente
            if tile.get("one_way", False):
                continue
            if check_collision(snake_rect, tile):
                if self.vx > 0:
                    self.x = tile["x"] - SNAKE_FRAME_WIDTH
                    self.vx = -abs(self.vx)
                elif self.vx < 0:
                    self.x = tile["x"] + tile["w"]
                    self.vx = abs(self.vx)
                snake_rect = self.get_rect()

    def _resolve_y_collision(self, tiles: list[Collider]) -> None:
        self.is_grounded = False
        snake_rect = self.get_rect()
        for tile in tiles:
            if tile.get("one_way", False):
                # One-way: só colide descendo
                if self.vy <= 0:
                    continue
                if (snake_rect["y"] + snake_rect["h"] - self.vy * 0.016) > tile["y"]:
                    continue
            if check_collision(snake_rect, tile):
                if self.vy > 0:
                    self.y = tile["y"] - SNAKE_FRAME_HEIGHT
                    self.is_grounded = True
                elif self.vy < 0:
                    self.y = tile["y"] + tile["h"]
                self.vy = 0.0
                snake_rect = self.get_rect()

    def _edge_ray(self, tiles: list[Collider]) -> bool:
        """Raycast vertical disparado 1px abaixo dos pés, na borda dianteira.

        Retorna True se há chão à frente (ray colidiu com um tile).
        Retorna False se há vazio → borda detectada.

        Geometria do raio
        -----------------
        Origem : (foot_x, self.y + SNAKE_FRAME_HEIGHT + 1)
        Comprimento: RAY_LEN pixels para baixo
        Largura : 1px (representado como rect de 1×RAY_LEN)

        O foot_x é a borda dianteira do sprite:
          • andando para a direita → x + SNAKE_FRAME_WIDTH
          • andando para a esquerda → x - 1
        """
        RAY_LEN = 8.0  # pixels — mantém robusto a pequenas irregularidades

        foot_x: float
        if self.vx >= 0:
            foot_x = self.x + SNAKE_FRAME_WIDTH  # borda direita
        else:
            foot_x = self.x - 1.0                # borda esquerda

        ray: Rect = {
            "x": foot_x,
            "y": self.y + SNAKE_FRAME_HEIGHT + 1.0,
            "w": 1.0,
            "h": RAY_LEN,
        }

        for tile in tiles:
            if check_collision(ray, tile):
                return True   # há chão
        return False          # vazio — borda!

    # ------------------------------------------------------------------
    # Update principal
    # ------------------------------------------------------------------

    def update(
        self,
        dt: float,
        tiles: list[Collider],
        player_x: float,
        player_y: float,
        player_rect: Rect,
    ) -> bool:
        """Atualiza a cobra e retorna True se colidiu com o player."""

        # ── Cooldown de ataque ─────────────────────────────────────────
        if self.attack_cooldown > 0.0:
            self.attack_cooldown -= dt

        # ── Atualiza projéteis ─────────────────────────────────────────
        for fb in self.fireballs:
            fb.update(dt, tiles)
        self.fireballs = [fb for fb in self.fireballs if fb.alive]

        # ── Gravidade (sempre, inclusive durante ataque) ───────────────
        self.vy += GRAVITY * dt

        dist = self._distance_to_player(player_x, player_y)

        # ── Decisão de estado ──────────────────────────────────────────
        if dist <= SNAKE_ATTACK_RANGE and self.attack_cooldown <= 0.0:
            self._set_state("attack")

        # ── Lógica de movimento horizontal ────────────────────────────
        if self.state == "attack":
            # Parada durante o ataque; apenas física vertical
            self.vx = 0.0

            # Dispara a bola de fogo no frame 1 — apenas uma vez por ataque
            if self.current_frame == 1 and not self._attack_fired:
                self._attack_fired = True
                direction = 1.0 if self.facing_right else -1.0
                spawn_x = (
                    self.x + SNAKE_FRAME_WIDTH
                    if self.facing_right
                    else self.x - FIRE_FRAME_WIDTH
                )
                spawn_y = self.y + SNAKE_FRAME_HEIGHT // 4
                self.fireballs.append(Fireball(spawn_x, spawn_y, direction))
                self.attack_cooldown = SNAKE_ATTACK_COOLDOWN

            self._advance_animation(dt)

            # Após completar os 2 frames de ataque → volta a andar
            if self.current_frame == 0 and self._attack_fired:
                self._set_state("walk")

        else:
            # ── Walk: patrulha ou perseguição ──────────────────────────
            snake_cx = self.x + SNAKE_FRAME_WIDTH / 2
            player_cx = player_x + SNAKE_FRAME_WIDTH / 2  # estimativa razoável

            if dist <= SNAKE_DETECTION_RANGE:
                # Perseguição: define vx em direção ao player cada frame
                self.vx = SNAKE_SPEED if player_cx > snake_cx else -SNAKE_SPEED
            else:
                # Patrulha: inverte nos extremos do patrol_left/right
                if self.x <= self.patrol_left:
                    self.vx = SNAKE_SPEED
                elif self.x + SNAKE_FRAME_WIDTH >= self.patrol_right:
                    self.vx = -SNAKE_SPEED

            # ── Raycast de borda ───────────────────────────────────────
            # Verifica se há chão logo abaixo da borda dianteira dos pés.
            # Só aplica quando a cobra já está em solo (evita falsas inversões
            # no ar durante um pulo ou queda inicial).
            if self.is_grounded and not self._edge_ray(tiles):
                self.vx = -self.vx   # dá meia-volta antes de cair

            self.facing_right = self.vx >= 0
            self._advance_animation(dt)

        # ── Integração X + colisão ─────────────────────────────────────
        self.x += self.vx * dt
        self._resolve_x_collision(tiles)

        # ── Integração Y + colisão ─────────────────────────────────────
        self.y += self.vy * dt
        self._resolve_y_collision(tiles)

        # Atualiza facing depois das colisões (vx pode ter invertido)
        if self.state != "attack" and self.vx != 0.0:
            self.facing_right = self.vx > 0

        # ── Colisão com o player ───────────────────────────────────────
        return check_collision(self.get_rect(), player_rect)

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self, renderer: Renderer) -> None:
        row, _num_frames, _fps = SNAKE_ANIMATIONS[self.state]
        col = self.current_frame

        uv_w = SNAKE_FRAME_WIDTH / SNAKE_TEX_WIDTH
        uv_h = SNAKE_FRAME_HEIGHT / SNAKE_TEX_HEIGHT
        uv_x = col * uv_w
        uv_y = row * uv_h

        if not self.facing_right:
            uv_x += uv_w
            uv_w = -uv_w

        renderer.draw_sprite(
            "snake",
            self.x,
            self.y,
            SNAKE_FRAME_WIDTH,
            SNAKE_FRAME_HEIGHT,
            uv_x,
            uv_y,
            uv_w,
            uv_h,
        )

        for fb in self.fireballs:
            fb.render(renderer)
