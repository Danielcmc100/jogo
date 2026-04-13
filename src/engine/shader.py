import OpenGL.GL as gl
from OpenGL.GL.shaders import compileProgram, compileShader
from typing import Any

VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec2 aPos;
layout (location = 1) in vec2 aTexCoord;

out vec2 TexCoord;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

void main()
{
    gl_Position = projection * view * model * vec4(aPos, 0.0, 1.0);
    TexCoord = aTexCoord;
}
"""

FRAGMENT_SHADER = """
#version 330 core
out vec4 FragColor;

in vec2 TexCoord;

uniform sampler2D ourTexture;

void main()
{
    vec4 texColor = texture(ourTexture, TexCoord);
    if(texColor.a < 0.1)
        discard;
    FragColor = texColor;
}
"""

class Shader:
    def __init__(self) -> None:
        self.program: Any = compileProgram(
            compileShader(VERTEX_SHADER, gl.GL_VERTEX_SHADER),
            compileShader(FRAGMENT_SHADER, gl.GL_FRAGMENT_SHADER)
        )

    def use(self) -> None:
        gl.glUseProgram(self.program)

    def set_int(self, name: str, value: int) -> None:
        location = gl.glGetUniformLocation(self.program, name)
        gl.glUniform1i(location, value)

    def set_mat4(self, name: str, value: Any) -> None:
        location = gl.glGetUniformLocation(self.program, name)
        gl.glUniformMatrix4fv(location, 1, gl.GL_FALSE, value)
