from OpenGL.GL import *

def draw_bullet(x, y):
    glBegin(GL_QUADS)
    glVertex2f(x-5, y)
    glVertex2f(x+5, y)
    glVertex2f(x+5, y+10)
    glVertex2f(x-5, y+10)
    glEnd()

