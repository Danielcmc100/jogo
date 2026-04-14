import OpenGL.GL as gl
import pygame
from typing import TypedDict, Any
import ctypes

class TextureData(TypedDict):
    id: int
    width: int
    height: int

class Renderer:
    def __init__(self, shader: Any, screen_width: float, screen_height: float):
        self.shader = shader
        self.textures: dict[str, TextureData] = {}
        self.screen_width = screen_width
        self.screen_height = screen_height
        self._init_render_data()
        
        self.camera_x = 0.0
        self.camera_y = 0.0

    def _init_render_data(self) -> None:
        # Vertex data: pos (x,y), tex (u,v)
        vertices = [
             0.0,  1.0,   0.0, 1.0,
             1.0,  0.0,   1.0, 0.0,
             0.0,  0.0,   0.0, 0.0,

             0.0,  1.0,   0.0, 1.0,
             1.0,  1.0,   1.0, 1.0,
             1.0,  0.0,   1.0, 0.0
        ]
        
        vertex_data = (ctypes.c_float * len(vertices))(*vertices)
        
        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)
        
        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, len(vertices) * 4, vertex_data, gl.GL_STATIC_DRAW)
        
        # Position
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 4 * 4, ctypes.c_void_p(0))
        # TexCoord
        gl.glEnableVertexAttribArray(1)
        gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 4 * 4, ctypes.c_void_p(2 * 4))
        
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)

    def load_texture(self, name: str, path: str) -> None:
        try:
            image = pygame.image.load(path).convert_alpha()
        except pygame.error as e:
            print(f"Failed to load image at {path}: {e}")
            return
            
        img_data = pygame.image.tostring(image, "RGBA", True)
        width = image.get_width()
        height = image.get_height()
        
        tex_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
        
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, img_data)
        
        self.textures[name] = {"id": tex_id, "width": width, "height": height}
    
    def _get_ortho(self, left: float, right: float, bottom: float, top: float) -> list[float]:
        z_near = -1.0
        z_far = 1.0
        return [
            2.0 / (right - left), 0.0, 0.0, 0.0,
            0.0, 2.0 / (top - bottom), 0.0, 0.0,
            0.0, 0.0, -2.0 / (z_far - z_near), 0.0,
            -(right + left) / (right - left), -(top + bottom) / (top - bottom), -(z_far + z_near) / (z_far - z_near), 1.0
        ]

    def _get_model_matrix(self, x: float, y: float, w: float, h: float) -> list[float]:
        return [
            w,   0.0, 0.0, 0.0,
            0.0, h,   0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            x,   y,   0.0, 1.0
        ]
        
    def _get_view_matrix(self) -> list[float]:
        # Simple translation for the camera
        return [
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            -round(self.camera_x), -round(self.camera_y), 0.0, 1.0
        ]

    def draw_sprite(self, texture_name: str, x: float, y: float, w: float, h: float,
                    uv_x: float = 0.0, uv_y: float = 0.0, uv_w: float = 1.0, uv_h: float = 1.0,
                    tint: tuple[float, float, float, float] | None = None) -> None:
        """Renderiza um sprite.

        Parâmetro ``tint``
        ------------------
        Tupla ``(r, g, b, strength)`` onde:
          - r, g, b ∈ [0.0, 1.0]  — cor do flash
          - strength ∈ [0.0, 1.0] — 0 = sem efeito, 1 = cor pura
        ``None`` → sem flash (comportamento padrão).
        """
        self.shader.use()

        projection = self._get_ortho(0.0, self.screen_width, self.screen_height, 0.0)
        view = self._get_view_matrix()
        model = self._get_model_matrix(round(x), round(y), round(w), round(h))

        self.shader.set_mat4("projection", (ctypes.c_float * 16)(*projection))
        self.shader.set_mat4("view", (ctypes.c_float * 16)(*view))
        self.shader.set_mat4("model", (ctypes.c_float * 16)(*model))

        # ── Tint (flash) ──────────────────────────────────────────────
        if tint is not None:
            r, g, b, strength = tint
            self.shader.set_vec3("u_tint_color", r, g, b)
            self.shader.set_float("u_tint_strength", strength)
        else:
            self.shader.set_vec3("u_tint_color", 0.0, 0.0, 0.0)
            self.shader.set_float("u_tint_strength", 0.0)

        vertices = [
             0.0,  1.0,   uv_x, uv_y,
             1.0,  0.0,   uv_x + uv_w, uv_y + uv_h,
             0.0,  0.0,   uv_x, uv_y + uv_h,

             0.0,  1.0,   uv_x, uv_y,
             1.0,  1.0,   uv_x + uv_w, uv_y,
             1.0,  0.0,   uv_x + uv_w, uv_y + uv_h
        ]

        vertex_data = (ctypes.c_float * len(vertices))(*vertices)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, len(vertices) * 4, vertex_data)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        gl.glActiveTexture(gl.GL_TEXTURE0)
        if texture_name in self.textures:
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.textures[texture_name]["id"])

        gl.glBindVertexArray(self.vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
        gl.glBindVertexArray(0)

    def draw_ui_sprite(self, texture_name: str, x: float, y: float, w: float, h: float, 
                        uv_x: float = 0.0, uv_y: float = 0.0, uv_w: float = 1.0, uv_h: float = 1.0) -> None:
        """Draws a sprite without camera transformation (UI layer)."""
        self.shader.use()
        
        projection = self._get_ortho(0.0, self.screen_width, self.screen_height, 0.0)
        # Identity view matrix for UI
        view = [
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0
        ]
        model = self._get_model_matrix(round(x), round(y), round(w), round(h))
        
        self.shader.set_mat4("projection", (ctypes.c_float * 16)(*projection))
        self.shader.set_mat4("view", (ctypes.c_float * 16)(*view))
        self.shader.set_mat4("model", (ctypes.c_float * 16)(*model))
        
        vertices = [
             0.0,  1.0,   uv_x, uv_y,
             1.0,  0.0,   uv_x + uv_w, uv_y + uv_h,
             0.0,  0.0,   uv_x, uv_y + uv_h,
             
             0.0,  1.0,   uv_x, uv_y,
             1.0,  1.0,   uv_x + uv_w, uv_y,
             1.0,  0.0,   uv_x + uv_w, uv_y + uv_h
        ]
        
        vertex_data = (ctypes.c_float * len(vertices))(*vertices)
        
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, len(vertices) * 4, vertex_data)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        
        gl.glActiveTexture(gl.GL_TEXTURE0)
        if texture_name in self.textures:
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.textures[texture_name]["id"])
        
        gl.glBindVertexArray(self.vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
        gl.glBindVertexArray(0)

