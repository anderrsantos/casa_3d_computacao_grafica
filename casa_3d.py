import ctypes
import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
from PIL import Image


# SHADERS com suporte a textura
VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec3 aPos;     // Porta 0: Geometria (X, Y, Z)
layout (location = 1) in vec2 aTexCord; // Porta 1: Mapeamento (U, V)

out vec2 TexCord;
uniform mat4 MVP;

void main() {
    gl_Position = MVP * vec4(aPos, 1.0);
    TexCord = aTexCord;
}
"""

FRAGMENT_SHADER = """
#version 330 core
in vec2 TexCord;
out vec4 FragColor;

uniform sampler2D textura_bloco;

void main() {
    FragColor = texture(textura_bloco, TexCord);
}
"""


def carregar_textura_do_disco(caminho_arquivo):
    print(f"[*] Tentando ler a imagem: {caminho_arquivo}...")

    try:
        imagem = Image.open(caminho_arquivo)
        imagem = imagem.transpose(Image.FLIP_TOP_BOTTOM)
        imagem_dados = imagem.convert("RGBA").tobytes()
        largura, altura = imagem.size
        print(f"    [+] Sucesso! Resolução: {largura}x{altura}")

    except FileNotFoundError:
        print(f"    [!] Arquivo '{caminho_arquivo}' não encontrado. Usando xadrez rosa/preto.")
        largura, altura = 2, 2
        imagem_dados = np.array([
            255, 0, 255, 255,   0, 0, 0, 255,
            0, 0, 0, 255,       255, 0, 255, 255
        ], dtype=np.uint8).tobytes()

    textura_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, textura_id)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, largura, altura, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, imagem_dados)

    glBindTexture(GL_TEXTURE_2D, 0)
    return textura_id


def matriz_translacao(x, y, z):
    return np.array([[1,0,0,x], [0,1,0,y], [0,0,1,z], [0,0,0,1]], dtype=np.float32)

def matriz_rotacao_x(g):
    c, s = np.cos(np.radians(g)), np.sin(np.radians(g))
    return np.array([[1,0,0,0], [0,c,-s,0], [0,s,c,0], [0,0,0,1]], dtype=np.float32)

def matriz_rotacao_y(g):
    c, s = np.cos(np.radians(g)), np.sin(np.radians(g))
    return np.array([[c,0,s,0], [0,1,0,0], [-s,0,c,0], [0,0,0,1]], dtype=np.float32)

def matriz_rotacao_z(g):
    c, s = np.cos(np.radians(g)), np.sin(np.radians(g))
    return np.array([[c,-s,0,0], [s,c,0,0], [0,0,1,0], [0,0,0,1]], dtype=np.float32)

def matriz_perspectiva(fov, aspecto, near, far):
    f = 1.0 / np.tan(np.radians(fov) / 2.0)
    return np.array([
        [f / aspecto, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
        [0, 0, -1, 0]
    ], dtype=np.float32)


def paredes_da_casa():
    vertices = np.array([
        # Face Frontal
        -1, -1,  1,   0.0, 0.0,
         1, -1,  1,   1.0, 0.0,
         1,  1,  1,   1.0, 1.0,
        -1,  1,  1,   0.0, 1.0,

        # Face Traseira (Z = -1)
        -1, -1, -1,   1.0, 0.0,
         1, -1, -1,   0.0, 0.0,
         1,  1, -1,   0.0, 1.0,
        -1,  1, -1,   1.0, 1.0,

        # Face Esquerda (X = -1)
        -1, -1, -1,   0.0, 0.0,
        -1, -1,  1,   1.0, 0.0,
        -1,  1,  1,   1.0, 1.0,
        -1,  1, -1,   0.0, 1.0,

        # Face Direita (X = 1)
         1, -1, -1,   1.0, 0.0,
         1, -1,  1,   0.0, 0.0,
         1,  1,  1,   0.0, 1.0,
         1,  1, -1,   1.0, 1.0,

        # Face Superior (Y = 1)
        -1,  1, -1,   0.0, 1.0,
         1,  1, -1,   1.0, 1.0,
         1,  1,  1,   1.0, 0.0,
        -1,  1,  1,   0.0, 0.0,

        # Face Inferior (Y = -1)
        -1, -1, -1,   0.0, 0.0,
         1, -1, -1,   1.0, 0.0,
         1, -1,  1,   1.0, 1.0,
        -1, -1,  1,   0.0, 1.0,
    ], dtype=np.float32)

    indices = np.array([
        0, 1, 2,  2, 3, 0,
        4, 5, 6,  6, 7, 4,
        8, 9, 10, 10, 11, 8,
        12, 13, 14, 14, 15, 12,
        16, 17, 18, 18, 19, 16,
        20, 21, 22, 22, 23, 20
    ], dtype=np.uint32)

    return vertices, indices


def telhado_da_casa():
    
    vertices = np.array([
        # Face Frontal
        -1, 1,  1,   0.0, 0.0,
         1, 1,  1,   1.0, 0.0,
         0, 2,  0,   0.5, 1.0,

        # Face Traseira
        -1, 1, -1,   1.0, 0.0,
         1, 1, -1,   0.0, 0.0,
         0, 2,  0,   0.5, 1.0,

        # Face Esquerda
        -1, 1, -1,   0.0, 0.0,
        -1, 1,  1,   1.0, 0.0,
         0, 2,  0,   0.5, 1.0,

        # Face Direita
         1, 1, -1,   1.0, 0.0,
         1, 1,  1,   0.0, 0.0,
         0, 2,  0,   0.5, 1.0,
    ], dtype=np.float32)

    return vertices

def grama_da_casa():
    vertices = np.array([
        # Face Superior (Y = -1)
        -3, -1.001, -3,   0.0, 0.0,
         3, -1.001, -3,   1.0, 0.0,
         3, -1.001,  3,   1.0, 1.0,
        -3, -1.001,  3,   0.0, 1.0,
        
        
    ], dtype=np.float32)

    indices = np.array([
        0, 1, 2,
        2, 3, 0
    ], dtype=np.uint32)

    return vertices, indices

def porta_da_casa():
    vertices = np.array([
        # Face Frontal (Z = 1.1)  -> índices 0 a 3
        -0.3, -1,  1.1,   0.0, 0.0,
         0.3, -1,  1.1,   1.0, 0.0,
         0.3,  0,  1.1,   1.0, 1.0,
        -0.3,  0,  1.1,   0.0, 1.0,

        # Face Esquerda (X = -0.3)  -> índices 4 a 7
        -0.3, -1,  1.0,   0.0, 0.0,
        -0.3, -1,  1.1,   1.0, 0.0,
        -0.3,  0,  1.1,   1.0, 1.0,
        -0.3,  0,  1.0,   0.0, 1.0,

        # Face Direita (X = 0.3)  -> índices 8 a 11
         0.3, -1,  1.0,   0.0, 0.0,
         0.3, -1,  1.1,   1.0, 0.0,
         0.3,  0,  1.1,   1.0, 1.0,
         0.3,  0,  1.0,   0.0, 1.0,

        # Face Superior (Y = 0)  -> índices 12 a 15
        -0.3,  0,  1.0,   0.0, 0.0,
         0.3,  0,  1.0,   1.0, 0.0,
         0.3,  0,  1.1,   1.0, 1.0,
        -0.3,  0,  1.1,   0.0, 1.0,
    ], dtype=np.float32)

    indices = np.array([
        0, 1, 2,    2, 3, 0,      # Frontal
        4, 5, 6,    6, 7, 4,      # Esquerda
        8, 9, 10,   10, 11, 8,    # Direita
        12, 13, 14, 14, 15, 12,   # Superior
    ], dtype=np.uint32)

    return vertices, indices

def criar_vao(vertices, indices=None):
    vao = glGenVertexArrays(1) 
    vbo = glGenBuffers(1)
    glBindVertexArray(vao)

    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    if indices is not None:
        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    passo = 5 * vertices.itemsize
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, passo, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, passo, ctypes.c_void_p(3 * vertices.itemsize))
    glEnableVertexAttribArray(1)

    glBindVertexArray(0)
    return vao


def main():
    if not glfw.init():
        return
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)  # necessário no macOS

    janela = glfw.create_window(1000, 800, "Casa 3D: Textura de Arquivo e Teclado", None, None)
    if not janela:
        glfw.terminate()
        return

    glfw.make_context_current(janela)
    glfw.swap_interval(1)
    glEnable(GL_DEPTH_TEST)

    shader = OpenGL.GL.shaders.compileProgram(
        OpenGL.GL.shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
        OpenGL.GL.shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
    )

    # Geometria: paredes (com índices) e telhado (sem índices)
    parede_vertices, parede_indices = paredes_da_casa()
    telhado_vertices = telhado_da_casa()
    grama_vertices, grama_indices = grama_da_casa()
    porta_vertices, porta_indices = porta_da_casa()

    vao_parede = criar_vao(parede_vertices, parede_indices)
    vao_telhado = criar_vao(telhado_vertices)
    vao_grama = criar_vao(grama_vertices, grama_indices)
    vao_porta = criar_vao(porta_vertices, porta_indices)

    matriz_proj = matriz_perspectiva(45.0, 1000 / 800, 0.1, 100.0)
    matriz_view = matriz_translacao(0, 0, -10.0)
    # A casa vai de y=-1 até y=2; centraliza em y=0.5 para girar no meio
    matriz_centro = matriz_translacao(0, -0.5, 0)

    # Texturas
    tex_parede = carregar_textura_do_disco("textura da parede.jpg")
    tex_telhado = carregar_textura_do_disco("telhado_casa.jpg")
    tex_grama = carregar_textura_do_disco("grama.jpg")
    tex_porta = carregar_textura_do_disco("porta.jpg")

    loc_mvp = glGetUniformLocation(shader, "MVP")
    loc_tex = glGetUniformLocation(shader, "textura_bloco")

    rot_x, rot_y = 25.0, -30.0
    velocidade = 2.0

    print("[*] Tudo pronto. Use as Setas do Teclado para explorar a casa 3D.")

    while not glfw.window_should_close(janela):
        glfw.poll_events()

        if glfw.get_key(janela, glfw.KEY_RIGHT) == glfw.PRESS: rot_y += velocidade
        if glfw.get_key(janela, glfw.KEY_LEFT) == glfw.PRESS:  rot_y -= velocidade
        if glfw.get_key(janela, glfw.KEY_DOWN) == glfw.PRESS:  rot_x += velocidade
        if glfw.get_key(janela, glfw.KEY_UP) == glfw.PRESS:    rot_x -= velocidade

        glClearColor(0.5, 0.8, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(shader)

        matriz_model = matriz_rotacao_x(rot_x) @ matriz_rotacao_y(rot_y) @ matriz_centro
        MVP = matriz_proj @ matriz_view @ matriz_model
        glUniformMatrix4fv(loc_mvp, 1, GL_FALSE, np.ascontiguousarray(MVP.T, dtype=np.float32))

        glActiveTexture(GL_TEXTURE0)
        glUniform1i(loc_tex, 0)

        # Paredes 
        glBindTexture(GL_TEXTURE_2D, tex_parede)
        glBindVertexArray(vao_parede)
        glDrawElements(GL_TRIANGLES, len(parede_indices), GL_UNSIGNED_INT, None)

        #  Telhado 
        glBindTexture(GL_TEXTURE_2D, tex_telhado)
        glBindVertexArray(vao_telhado)
        glDrawArrays(GL_TRIANGLES, 0, 12)
        
        # Grama
        glBindTexture(GL_TEXTURE_2D, tex_grama)
        glBindVertexArray(vao_grama)
        glDrawElements(GL_TRIANGLES, len(grama_indices), GL_UNSIGNED_INT, None)
        
        # Porta
        glBindTexture(GL_TEXTURE_2D, tex_porta)
        glBindVertexArray(vao_porta)
        glDrawElements(GL_TRIANGLES, len(porta_indices), GL_UNSIGNED_INT, None)

        glfw.swap_buffers(janela)

    glfw.terminate()


if __name__ == "__main__":
    main()