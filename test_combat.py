import pygame
pygame.init()
from src.game.settings import PLAYER_ANIMATIONS, SNAKE_MAX_HP
from src.game.player import Player
from src.game.snake import Snake

assert "attack" in PLAYER_ANIMATIONS
row, frames, fps = PLAYER_ANIMATIONS["attack"]
assert row == 5 and frames == 3
print(f"attack OK: row={row} frames={frames} fps={fps}")

p = Player(100.0, 100.0)
p._attacking = True
p.state = "attack"
p.current_frame = 1
p.facing_right = True
r = p.get_attack_rect()
assert r is not None and r["x"] >= p.x + 32
print(f"hitbox espada OK: x={r['x']:.0f}")
p.current_frame = 0
assert p.get_attack_rect() is None
print("frame 0 sem hitbox OK")

s = Snake(x=150.0, y=270.0, patrol_left=100.0, patrol_right=300.0)
assert s.hp == 2
s.take_hit(1)
assert s.hp == 1 and s.alive
print("1 hit OK")
s._hit_timer = 0.0
s.take_hit(1)
assert s.hp == 0 and not s.alive
print("2 hits morta OK")

print("Todos os asserts passaram.")
pygame.quit()
