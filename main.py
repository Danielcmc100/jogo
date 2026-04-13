import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from bullet import draw_bullet

# =====================
# INIT
# =====================
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

glOrtho(0, 800, 0, 600, -1, 1)
glClearColor(0, 0, 0, 1)

clock = pygame.time.Clock()


player_x = 400
player_y = 50

bullets = []


# =====================
# DRAW FUNCTIONS
# =====================
def draw_player(x, y):
    glColor3f(1, 1, 1)
    glBegin(GL_QUADS)
    glVertex2f(x - 20, y)
    glVertex2f(x + 20, y)
    glVertex2f(x + 20, y + 20)
    glVertex2f(x - 20, y + 20)
    glEnd()


# =====================
# GAME LOOP
# =====================
while True:
    # -------- INPUT --------
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            quit()

        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                bullets.append([player_x, player_y])

    keys = pygame.key.get_pressed()
    if keys[K_a]:
        player_x -= 5
    if keys[K_d]:
        player_x += 5

    # -------- UPDATE --------
    for bullet in bullets:
        bullet[1] += 10  # sobe

    # -------- RENDER --------
    glClear(GL_COLOR_BUFFER_BIT)

    draw_player(player_x, player_y)

    for bullet in bullets:
        draw_bullet(bullet[0], bullet[1])

    pygame.display.flip()
    clock.tick(60)
