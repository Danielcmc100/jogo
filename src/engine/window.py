import pygame
import OpenGL.GL as gl
from .renderer import Renderer
from .shader import Shader

class Window:
    def __init__(self, title: str, window_w: int, window_h: int, logical_w: int, logical_h: int):
        pygame.init()
        pygame.display.set_mode((window_w, window_h), pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption(title)
        
        gl.glViewport(0, 0, window_w, window_h)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        
        self.width = window_w
        self.height = window_h
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0.0
        
        self.shader = Shader()
        self.renderer = Renderer(self.shader, logical_w, logical_h)
        
    def clear(self) -> None:
        gl.glClearColor(0.1, 0.1, 0.1, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        
    def swap_buffers(self) -> None:
        pygame.display.flip()
        
    def poll_events(self) -> list[pygame.event.Event]:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
        return events
        
    def tick(self, fps: int = 60) -> None:
        self.dt = self.clock.tick(fps) / 1000.0
