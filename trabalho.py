"""
Projeto de Computação Gráfica 2025/2026
DI-FCUL 2025

Cena Interativa 3D com Veículo e Garagem
- Veículo com rodas traseiras maiores que as dianteiras
- Portas que abrem/fecham (interação do utilizador)
- Volante rotativo
- Rodas giram durante movimento
- Veículo entra numa garagem com porta interativa
- Múltiplas fontes de iluminação
- Múltiplos materiais
- Controlo de câmara pelo utilizador
- Chão texturado
"""

import sys
import math
import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL import GLUT

# ========== CONFIGURAÇÕES GLOBAIS ==========
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_TITLE = "Projeto CG - Veículo e Garagem"

# Estados do veículo
class VehicleState:
    def __init__(self):
        self.x = 0.0
        self.z = 0.0
        self.angle = 180.0  # Direção do veículo
        self.speed = 0.0
        self.wheel_rotation = 0.0  # Rotação das rodas
        self.steering_angle = 0.0  # Ângulo do volante (max ±30 graus)
        self.left_door_open = 0.0  # 0 = fechada, 1 = aberta
        self.left_door_target = 0.0
        self.right_door_open = 0.0  # 0 = fechada, 1 = aberta
        self.right_door_target = 0.0

# Estados da câmara
class CameraState:
    def __init__(self):
        self.x = 0.0
        self.y = 5.0
        self.z = 15.0
        self.pitch = -20.0  # Rotação vertical
        self.yaw = 0.0      # Rotação horizontal
        self.follow_vehicle = False
        self.inside_vehicle = False

# Estados da garagem
class GarageState:
    def __init__(self):
        self.door_open = 0.0  # 0 = fechada, 1 = aberta
        self.door_target = 0.0

# Inicialização dos estados
vehicle = VehicleState()
camera = CameraState()
garage = GarageState()

# Controlo de teclado
keys_pressed = set()
special_keys_pressed = set() # Serve para as setas

# ========== MATERIAIS ==========
class Material:
    """Define materiais com propriedades de iluminação"""
    
    # Material 1: Carro (vermelho metálico)
    CAR_BODY = {
        'ambient': [0.2, 0.0, 0.0, 1.0],
        'diffuse': [0.8, 0.1, 0.1, 1.0],
        'specular': [0.9, 0.9, 0.9, 1.0],
        'shininess': [100.0]
    }
    
    CAR_ACCENT = {
        'ambient': [0.05, 0.05, 0.05, 1.0],
        'diffuse': [0.2, 0.2, 0.25, 1.0],
        'specular': [0.6, 0.6, 0.6, 1.0],
        'shininess': [60.0]
    }
    
    CAR_ROOF = {
        'ambient': [0.1, 0.1, 0.1, 1.0],
        'diffuse': [0.25, 0.25, 0.25, 1.0],
        'specular': [0.7, 0.7, 0.7, 1.0],
        'shininess': [90.0]
    }
    
    # Material 2: Vidro (portas e janelas)
    GLASS = {
        'ambient': [0.05, 0.08, 0.1, 0.15],
        'diffuse': [0.4, 0.6, 0.8, 0.2],
        'specular': [0.8, 0.9, 1.0, 0.2],
        'shininess': [76.8]
    }
    
    TINTED_GLASS = {
        'ambient': [0.0, 0.0, 0.0, 0.25],
        'diffuse': [0.05, 0.05, 0.05, 0.3],
        'specular': [0.3, 0.3, 0.3, 0.3],
        'shininess': [40.0]
    }
    
    # Material 3: Borracha (rodas)
    RUBBER = {
        'ambient': [0.05, 0.05, 0.05, 1.0],
        'diffuse': [0.2, 0.2, 0.2, 1.0],
        'specular': [0.1, 0.1, 0.1, 1.0],
        'shininess': [10.0]
    }
    
    # Material 4: Metal (volante e detalhes)
    METAL = {
        'ambient': [0.25, 0.25, 0.25, 1.0],
        'diffuse': [0.4, 0.4, 0.4, 1.0],
        'specular': [0.7, 0.7, 0.7, 1.0],
        'shininess': [76.8]
    }
    
    # Material 5: Garagem
    GARAGE_WALL = {
        'ambient': [0.15, 0.15, 0.2, 1.0],
        'diffuse': [0.4, 0.4, 0.55, 1.0],
        'specular': [0.3, 0.3, 0.4, 1.0],
        'shininess': [40.0]
    }
    
    GARAGE_DOOR = {
        'ambient': [0.2, 0.15, 0.05, 1.0],
        'diffuse': [0.6, 0.45, 0.2, 1.0],
        'specular': [0.4, 0.3, 0.2, 1.0],
        'shininess': [50.0]
    }
    
    # Material 6: Cimento (chão)
    CONCRETE = {
        'ambient': [0.4, 0.4, 0.4, 1.0],
        'diffuse': [0.6, 0.6, 0.6, 1.0],
        'specular': [0.1, 0.1, 0.1, 1.0],
        'shininess': [5.0]
    }
    
    WOOD = {
        "ambient":  (0.25, 0.17, 0.07, 1.0),
        "diffuse":  (0.40, 0.26, 0.13, 1.0),
        "specular": (0.10, 0.08, 0.04, 1.0),
        "shininess": 10.0
    }

    LEAVES = {
        "ambient":  (0.05, 0.20, 0.05, 1.0),
        "diffuse":  (0.12, 0.45, 0.12, 1.0),
        "specular": (0.01, 0.03, 0.01, 1.0),
        "shininess": 5.0
    }
    
    @staticmethod
    def apply(material_dict):
        """Aplica um material"""
        glMaterialfv(GL_FRONT, GL_AMBIENT, material_dict['ambient'])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, material_dict['diffuse'])
        glMaterialfv(GL_FRONT, GL_SPECULAR, material_dict['specular'])
        glMaterialfv(GL_FRONT, GL_SHININESS, material_dict['shininess'])

# ========== ILUMINAÇÃO ==========
def setup_lighting():
    """Configura as fontes de iluminação"""
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_NORMALIZE)
    
    # Luz 1: Luz direcional (sol)
    glLightfv(GL_LIGHT0, GL_POSITION, [10.0, 15.0, 10.0, 0.0])  # Direcional
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    
    # Luz 2: Luz pontual (interior da garagem)
    glLightfv(GL_LIGHT1, GL_POSITION, [0.0, 3.0, -12.0, 1.0])  # Pontual
    glLightfv(GL_LIGHT1, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.9, 0.9, 0.7, 1.0])
    glLightfv(GL_LIGHT1, GL_SPECULAR, [1.0, 1.0, 0.8, 1.0])
    glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 1.0)
    glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION, 0.1)
    glLightf(GL_LIGHT1, GL_QUADRATIC_ATTENUATION, 0.01)

# ========== TEXTURAS ==========
def create_checker_texture(size=32):
    """Cria uma textura de xadrez para o chão"""
    texture_data = np.zeros((size, size, 3), dtype=np.uint8)
    for i in range(size):
        for j in range(size):
            if (i // 4 + j // 4) % 2 == 0:
                texture_data[i, j] = [150, 150, 150]  # Cinza claro
            else:
                texture_data[i, j] = [100, 100, 100]  # Cinza escuro
    return texture_data

floor_texture_id = None

def init_textures():
    """Inicializa as texturas"""
    global floor_texture_id
    floor_texture_data = create_checker_texture()
    
    floor_texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, floor_texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 32, 32, 0, GL_RGB, GL_UNSIGNED_BYTE, floor_texture_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

# ========== PRIMITIVAS GEOMÉTRICAS ==========
def draw_wheel(radius, width, flip=False):
    """Desenha uma roda completa com pneu e jante
    flip: se True, roda 180° para rodas opostas"""
    
    # Pneu
    Material.apply(Material.RUBBER)
    glPushMatrix()
    glRotatef(90, 0, 1, 0)
    # pneu mais grosso
    glutSolidTorus(width * 0.6, radius, 32, 32)
    glPopMatrix()
    
    # Jante
    Material.apply(Material.METAL)
    glPushMatrix()
    glRotatef(90, 0, 1, 0)
    if flip:
        glRotatef(180, 0, 1, 0)  # roda 180° para rodas traseiras ou opostas
    
    # Disco central
    glutSolidCylinder(radius * 0.55, width * 0.8, 24, 24)
    
    # --- Dois raios perpendiculares atravessando o centro da jante ---
    for angle in [0, 90]:
        glPushMatrix()
        glRotatef(angle, 0, 0, 1)          # gira em torno do eixo Z (atravessa a jante)
        glScalef(2*radius, 0.05, 0.05) 
        
        Material.apply(Material.CAR_ACCENT)   # comprido atravessa toda a jante
        glutSolidCube(1.0)
        glPopMatrix()

    glPopMatrix()


def draw_vehicle_body():
    """Carroçaria com cockpit aberto para 2 lugares"""
    
    Material.apply(Material.CAR_BODY)

    # --- Dimensões base ---
    width = 1.5      # largura total
    height = 0.6     # altura da lateral
    length = 3.0     # comprimento
    wall = 0.08      # espessura da chapa
    cockpit_width = 1.2
    #cockpit_length = 1.6

    # --- Chão ---
    glPushMatrix()
    glTranslatef(0, 0.4, 0)
    glScalef(width, wall, length)
    glutSolidCube(1.0)
    glPopMatrix()
    door_z_front = 0.8         # onde está o hinge
    door_z_back  = door_z_front - 1.10
    # --- Laterais (esquerda e direita) ---
      # LEFT SIDE
    x_left = -(width/2 - wall/2)

    # --- Parede esquerda (frente) ---
    glPushMatrix()
    glTranslatef(x_left, 0.7, (door_z_front + (length/2)) / 2)
    front_length = (length/2 - door_z_front)
    glScalef(wall, height, front_length)
    glutSolidCube(1.0)
    glPopMatrix()

    # --- Parede esquerda (trás) ---
    glPushMatrix()
    glTranslatef(x_left, 0.7, (door_z_back + (-length/2)) / 2)
    back_length = (door_z_back - (-length/2))
    glScalef(wall, height, back_length)
    glutSolidCube(1.0)
    glPopMatrix()

    # RIGHT SIDE
    x_right = (width/2 - wall/2)

    # --- Parede direita (frente) ---
    glPushMatrix()
    glTranslatef(x_right, 0.7, (door_z_front + (length/2)) / 2)
    glScalef(wall, height, front_length)
    glutSolidCube(1.0)
    glPopMatrix()

    # --- Parede direita (trás) ---
    glPushMatrix()
    glTranslatef(x_right, 0.7, (door_z_back + (-length/2)) / 2)
    glScalef(wall, height, back_length)
    glutSolidCube(1.0)
    glPopMatrix()

    # --- Frontal ---
    glPushMatrix()
    glTranslatef(0, 0.7, 1.2)
    glScalef(cockpit_width + 0.2, height, wall + 0.5)
    glutSolidCube(1.0)
    glPopMatrix()

    # --- Traseira ---
    glPushMatrix()
    glTranslatef(0, 0.7, -0.9)
    glScalef(cockpit_width + 0.2, height, wall + 1.2)
    glutSolidCube(1.0)
    glPopMatrix()

   

    # --- Para-brisa dianteiro (mantido) ---
    Material.apply(Material.GLASS)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)
    
    glPushMatrix()
    glTranslatef(0, 1.05, 1.0)
    glRotatef(-15, 1, 0, 0)
    glScalef(1.1, 0.6, 0.05)
    glutSolidCube(1.0)
    glPopMatrix()

    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)

    # --- Para-choques ---
    Material.apply(Material.METAL)
    glPushMatrix()
    glTranslatef(0, 0.3, 1.5)
    glScalef(1.4, 0.3, 0.2)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 0.3, -1.4)
    glScalef(1.4, 0.3, 0.2)
    glutSolidCube(1.0)
    glPopMatrix()


def draw_door(side, open_amount):
    """Desenha uma porta do veículo"""
    # side: 1 = direita, -1 = esquerda

    Material.apply(Material.CAR_BODY)
    glPushMatrix()

    # --- DIMENSÕES DA PORTA ---
    door_width  = 0.05      # espessura
    door_height = 0.60     # altura
    door_length = 1.10      # comprimento da porta (Z)

    # --- ÂNGULO DE ABERTURA ---
    door_angle = open_amount * 70  # Até 70º

    # --- POSIÇÃO DO HINGE (vértice da frente) ---
    hinge_x = side * 0.75    # mesmo X das rodas dianteiras
    hinge_y = 0.60
    hinge_z = 0.8             # alinhado com a frente da cabine

    # 1. Ir para o hinge da porta
    glTranslatef(hinge_x, hinge_y, hinge_z)

    # 2. Rodar a porta a partir dos vértices da frente
    glRotatef(-door_angle * side, 0, 1, 0)

    # 3. Deslocar porta inteira para trás (porque cubo nasce no centro)
    glTranslatef(0, 0, -door_length/2)

    # 4. Deslocar ligeiramente para dentro/fora (lado)
    glTranslatef(-side * door_width/2, 0, 0)

    # ---- Corpo da porta ----
    glPushMatrix()
    glScalef(door_width, door_height, door_length)
    glutSolidCube(1.0)
    glPopMatrix()

   

    glPopMatrix()

   

def draw_steering_wheel():
    """Desenha o volante"""
    Material.apply(Material.METAL)
    
    glPushMatrix()

    # Lado esquerdo (ajustado)
    glTranslatef(0.30, 0.92, 0.9)

    # Orientação base
    glRotatef(5, 0, 1, 0)
    glRotatef(10, 1, 0, 0)

    # Rotação do volante em si
    glPushMatrix()
    glRotatef(-vehicle.steering_angle * 4, 0, 0, 1)

    # Aro (vertical)
    glPushMatrix()
    glRotatef(90, 0, 0, 1)
    glutSolidTorus(0.03, 0.22, 24, 32)
    glPopMatrix()

    # Núcleo
    glutSolidSphere(0.04, 16, 16)

    # --- Raios ---

    # Raio inferior
    glPushMatrix()
    glRotatef(270, 0, 0, 1)
    glTranslatef(0, 0.1, 0)
    glScalef(0.04, 0.25, 0.04)
    glutSolidCube(1.0)
    glPopMatrix()

    # Raio esquerdo
    glPushMatrix()
    glRotatef(150, 0, 0, 1)
    glTranslatef(0, 0.1, 0)
    glScalef(0.04, 0.25, 0.04)
    glutSolidCube(1.0)
    glPopMatrix()

    # Raio direito
    glPushMatrix()
    glRotatef(30, 0, 0, 1)
    glTranslatef(0, 0.1, 0)
    glScalef(0.04, 0.25, 0.04)
    glutSolidCube(1.0)
    glPopMatrix()


    glPopMatrix()
    glPopMatrix()

def draw_vehicle():
    """Desenha o veículo completo"""
    glPushMatrix()
    
    # Posição e orientação do veículo
    glTranslatef(vehicle.x, 0, vehicle.z)
    glRotatef(vehicle.angle, 0, 1, 0)
    
    # Corpo
    draw_vehicle_body()
    
    # Portas
    draw_door(1, vehicle.right_door_open)   # Porta direita
    draw_door(-1, vehicle.left_door_open)   # Porta esquerda
    
    # Rodas
    front_wheel_radius = 0.22
    rear_wheel_radius = 0.28  # Maiores
    
    glPushMatrix()
    glTranslatef(0.78, 0.26, 1.05)  # Roda dianteira direita
    glRotatef(vehicle.steering_angle, 0, 1, 0)
    glRotatef(vehicle.wheel_rotation, 1, 0, 0)
    draw_wheel(front_wheel_radius, 0.18, flip=True)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(-0.78, 0.26, 1.05)  # Roda dianteira esquerda
    glRotatef(vehicle.steering_angle, 0, 1, 0)
    glRotatef(vehicle.wheel_rotation, 1, 0, 0)
    draw_wheel(front_wheel_radius, 0.18, )
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0.78, 0.33, -1.05)  # Roda traseira direita
    glRotatef(vehicle.wheel_rotation * (front_wheel_radius / rear_wheel_radius), 1, 0, 0)
    draw_wheel(rear_wheel_radius, 0.22, flip=True )
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(-0.78, 0.33, -1.05)  # Roda traseira esquerda
    glRotatef(vehicle.wheel_rotation * (front_wheel_radius / rear_wheel_radius), 1, 0, 0)
    draw_wheel(rear_wheel_radius, 0.22 )
    glPopMatrix()
    
    # Volante
    draw_steering_wheel()
    
    glPopMatrix()

def draw_garage():
    """Desenha a garagem"""
    Material.apply(Material.GARAGE_WALL)
    
    glPushMatrix()
    glTranslatef(0, 2.4, -12)
    
    # Chão da garagem
    glPushMatrix()
    glTranslatef(0, -2.4, 0)
    glScalef(7.5, 0.2, 6.0)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Paredes laterais
    for side in (-1, 1):
        glPushMatrix()
        glTranslatef(side * 3.5, 0, 0)
        glScalef(0.4, 5, 6)
        glutSolidCube(1.0)
        glPopMatrix()
    
    # Parede traseira
    glPushMatrix()
    glTranslatef(0, 0, -3)
    glScalef(7.2, 5, 0.4)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Vigas frontais
    for offset in (-2.5, 2.5):
        glPushMatrix()
        glTranslatef(offset, 0, 3)
        glScalef(0.4, 5, 0.4)
        glutSolidCube(1.0)
        glPopMatrix()

    # Frente lateral (fecha as laterais do vão da porta)
    # Local z=3.2 aqui corresponde ao mundo z=-8.8 (mesmo plano da porta)
    # Segmentos preenchem entre a borda da porta (±1.75) e as paredes laterais (±3.5)
    glPushMatrix()
    glTranslatef(-2.625, 0, 3.2)
    glScalef(1.75, 5, 0.4)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(2.625, 0, 3.2)
    glScalef(1.75, 5, 0.4)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Teto
    Material.apply(Material.CAR_ACCENT)
    glPushMatrix()
    glTranslatef(0, 2.4, 0)
    glScalef(8, 0.35, 6.5)
    glutSolidCube(1.0)
    glPopMatrix()
    
    glPopMatrix()
    
    # Porta da garagem (abre de baixo para cima)
    glPushMatrix()
    glTranslatef(0, 2.3, -8.8)
    glTranslatef(0, 2.0, 0)  # mover para a aresta superior
    glRotatef(garage.door_open * -85, 1, 0, 0)
    glTranslatef(0, -2.0, 0)
    
    Material.apply(Material.GARAGE_DOOR)
    glPushMatrix()
    glScalef(3.5, 4.0, 0.3)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Detalhes em vidro
    Material.apply(Material.GLASS)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glPushMatrix()
    glTranslatef(0.5, 0.3, 0)
    glScalef(1.5, 2.5, 0.15)
    glutSolidCube(1.0)
    glPopMatrix()
    glDisable(GL_BLEND)
    
    glPopMatrix()

def draw_floor():
    """Desenha o chão texturado"""
    Material.apply(Material.CONCRETE)
    
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, floor_texture_id)
    
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    
    # Repetição da textura
    tile_size = 2.0
    tiles_x = 20
    tiles_z = 20
    
    for i in range(-tiles_x, tiles_x):
        for j in range(-tiles_z, tiles_z):
            x1 = i * tile_size
            z1 = j * tile_size
            x2 = (i + 1) * tile_size
            z2 = (j + 1) * tile_size
            
            glTexCoord2f(0, 0)
            glVertex3f(x1, 0, z1)
            
            glTexCoord2f(1, 0)
            glVertex3f(x2, 0, z1)
            
            glTexCoord2f(1, 1)
            glVertex3f(x2, 0, z2)
            
            glTexCoord2f(0, 1)
            glVertex3f(x1, 0, z2)
    
    glEnd()
    glDisable(GL_TEXTURE_2D)
def draw_tree(x, y, z):
    # tronco
    Material.apply(Material.WOOD)
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(0.2, 1.0, 0.2)
    glutSolidCube(1.0)
    glPopMatrix()

    # folhas
    Material.apply(Material.LEAVES)
    glPushMatrix()
    glTranslatef(x, y + 1.0, z)
    glutSolidSphere(0.6, 24, 24)
    glPopMatrix()


def draw_scene():
    """Desenha toda a cena"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Configurar câmara
    glLoadIdentity()
    
    if camera.inside_vehicle:
    # Direção da frente do veículo
        dx = math.sin(math.radians(vehicle.angle))
        dz = math.cos(math.radians(vehicle.angle))
        
        lateral_offset = -0.2  # quanto para a esquerda
        forward_offset = 0.1  # ligeiramente à frente
        
        cam_x = vehicle.x + dx * forward_offset - dz * lateral_offset
        cam_z = vehicle.z + dz * forward_offset + dx * lateral_offset
        cam_y = 1.3
        
        # Ponto de visão
        look_x = vehicle.x + dx * 5 - dz * lateral_offset
        look_z = vehicle.z + dz * 5 + dx * lateral_offset
        look_y = 1.3
        
        gluLookAt(cam_x, cam_y, cam_z,
                look_x, look_y, look_z,
                0, 1, 0)

    elif camera.follow_vehicle:
        # Câmara seguindo o veículo
        offset_x = math.sin(math.radians(vehicle.angle + 180)) * 8
        offset_z = math.cos(math.radians(vehicle.angle + 180)) * 8
        
        cam_x = vehicle.x + offset_x
        cam_z = vehicle.z + offset_z
        cam_y = camera.y
        
        gluLookAt(cam_x, cam_y, cam_z,
                  vehicle.x, 1.0, vehicle.z,
                  0, 1, 0)
    else:
        rad_yaw = math.radians(camera.yaw)
        rad_pitch = math.radians(camera.pitch)

        dir_x = math.cos(rad_pitch) * math.sin(rad_yaw)
        dir_y = math.sin(rad_pitch)
        dir_z = -math.cos(rad_pitch) * math.cos(rad_yaw)

        look_x = camera.x + dir_x
        look_y = camera.y + dir_y
        look_z = camera.z + dir_z

        gluLookAt(
            camera.x, camera.y, camera.z,
            look_x, look_y, look_z,
            0, 1, 0
        )
    # Desenhar elementos da cena
    draw_floor()
    draw_garage()
    draw_vehicle()
    draw_tree(4,0.5,-7)
    draw_tree(-4,0.5,-7)
    draw_hud()
    
    glutSwapBuffers()

# ========== ATUALIZAÇÃO E ANIMAÇÃO ==========
def animate_value(current, target, speed, dt):
    """Interpola um valor com velocidade constante"""
    if abs(target - current) < 1e-3:
        return target
    step = speed * dt
    delta = target - current
    if abs(delta) <= step:
        return target
    return current + math.copysign(step, delta)

def resolve_static_collisions(new_x, new_z, rad_angle):
    """Evita atravessar paredes da garagem e árvores.
    Usa AABB para paredes e cilindro para troncos.
    Mantém contacto suave pelo bumper-leading (usa forward do ângulo atual).
    """
    # Direção do veículo
    forward_x = math.sin(rad_angle)
    forward_z = math.cos(rad_angle)

    # Dimensão aproximada do carro para contacto (para-choques)
    bumper_offset = 1.5
    # Usa o para-choques da frente quando avança e o de trás quando recua
    lead_offset = bumper_offset if vehicle.speed >= 0 else -bumper_offset

    lead_x = new_x + forward_x * lead_offset
    lead_z = new_z + forward_z * lead_offset

    # ---------- Garagem ----------
    # Garagem está centrada em (0, z=-12) com piso de 7.5x6.0 e paredes desenhadas.
    # Definimos AABBs simples em coordenadas do mundo.
    garage_center_z = -12.0
    half_width = 3.5
    half_depth = 3.0
    wall_thickness = 0.35

    # Paredes laterais (esquerda e direita)
    left_wall_min = (-half_width - wall_thickness, garage_center_z - half_depth)
    left_wall_max = (-half_width + wall_thickness, garage_center_z + half_depth)

    right_wall_min = (half_width - wall_thickness, garage_center_z - half_depth)
    right_wall_max = (half_width + wall_thickness, garage_center_z + half_depth)

    # Parede traseira
    back_wall_min = (-half_width, garage_center_z - half_depth - wall_thickness)
    back_wall_max = (half_width, garage_center_z - half_depth + wall_thickness)

    # Porta (frente). Quando fechada, tratamos como uma "laje" de espessura.
    door_z = -8.8
    door_half_thickness = 0.15  # metade da espessura (malha usa 0.3 em Z)
    door_half_width = 1.75      # metade da largura (malha usa 3.5 em X)
    door_min = (-door_half_width, door_z - door_half_thickness)
    door_max = (door_half_width, door_z + door_half_thickness)

    # Segmentos frontais fixos (laterais do vão) — sempre bloqueiam
    front_half_thickness = 0.20  # corresponde à malha (glScalef .., .., 0.4)
    front_left_min = (-half_width, door_z - front_half_thickness)
    front_left_max = (-door_half_width, door_z + front_half_thickness)
    front_right_min = (door_half_width, door_z - front_half_thickness)
    front_right_max = (half_width, door_z + front_half_thickness)

    '''def clamp_against_plane(px, pz, plane_normal):
        # Reposiciona o centro do carro para que o bumper fique encostado ao plano
        nx, nz, plane_point = plane_normal
        # Projeta o bumper para o plano: center = plane_point - forward * lead_offset
        return plane_point[0] - forward_x * lead_offset, plane_point[1] - forward_z * lead_offset'''

    # Teste colisão com AABB
    def hit_aabb(aabb_min, aabb_max, lx, lz):
        return (aabb_min[0] <= lx <= aabb_max[0]) and (aabb_min[1] <= lz <= aabb_max[1])

    # Segmentos frontais laterais (sempre ativos)
    if hit_aabb(front_left_min, front_left_max, lead_x, lead_z):
        plane_z = (door_z - front_half_thickness
                   if abs(lead_z - (door_z - front_half_thickness)) < abs(lead_z - (door_z + front_half_thickness))
                   else door_z + front_half_thickness)
        return new_x, plane_z - forward_z * lead_offset

    if hit_aabb(front_right_min, front_right_max, lead_x, lead_z):
        plane_z = (door_z - front_half_thickness
                   if abs(lead_z - (door_z - front_half_thickness)) < abs(lead_z - (door_z + front_half_thickness))
                   else door_z + front_half_thickness)
        return new_x, plane_z - forward_z * lead_offset

    # Porta só bloqueia se fechada
    if garage.door_open < 0.95 and hit_aabb(door_min, door_max, lead_x, lead_z):
        # Plano frontal/traseiro da porta (dependendo de onde veio)
        plane_point = (lead_x, door_max[1]) if lead_z >= door_z else (lead_x, door_min[1])
        new_x = plane_point[0] - forward_x * lead_offset
        new_z = plane_point[1] - forward_z * lead_offset
        return new_x, new_z

    # Paredes laterais
    if hit_aabb(left_wall_min, left_wall_max, lead_x, lead_z):
        # Escolhe o plano X mais próximo
        plane_x = left_wall_min[0] if abs(lead_x - left_wall_min[0]) < abs(lead_x - left_wall_max[0]) else left_wall_max[0]
        # Encostar ao plano X
        return plane_x - forward_x * lead_offset, new_z

    if hit_aabb(right_wall_min, right_wall_max, lead_x, lead_z):
        plane_x = right_wall_min[0] if abs(lead_x - right_wall_min[0]) < abs(lead_x - right_wall_max[0]) else right_wall_max[0]
        return plane_x - forward_x * lead_offset, new_z

    # Parede traseira (plano Z)
    if hit_aabb(back_wall_min, back_wall_max, lead_x, lead_z):
        plane_z = back_wall_min[1] if abs(lead_z - back_wall_min[1]) < abs(lead_z - back_wall_max[1]) else back_wall_max[1]
        return new_x, plane_z - forward_z * lead_offset

    # ---------- Árvores ----------
    # Troncos nos mesmos locais de draw_tree: (4,-7) e (-4,-7) ao nível do chão
    # Usamos dois "círculos" para o carro (bumpers frente e trás) para evitar atravessar de lado ou a recuar.
    tree_positions = [(4.0, -7.0), (-4.0, -7.0)]
    trunk_radius = 0.18
    bumper_radius = 0.60  # ~meia largura do carro (1.5/2 = 0.75), ligeiramente menor para tolerância

    # Centros dos bumpers relativos ao centro do carro
    front_cx = new_x + forward_x * bumper_offset
    front_cz = new_z + forward_z * bumper_offset
    rear_cx  = new_x - forward_x * bumper_offset
    rear_cz  = new_z - forward_z * bumper_offset

    def resolve_bumper_vs_trunk(cx, cz, tx, tz):
        nonlocal new_x, new_z
        dx = cx - tx
        dz = cz - tz
        dist2 = dx*dx + dz*dz
        min_d = trunk_radius + bumper_radius
        if dist2 < min_d * min_d:
            dist = math.sqrt(dist2) if dist2 > 1e-8 else 1e-8
            # Direção de empurrão do tronco para o bumper
            nx = dx / dist
            nz = dz / dist
            # Quantidade para sair da interpenetração
            push = (min_d - dist)
            # Empurra o carro inteiro (centro) nessa direção
            new_x += nx * push
            new_z += nz * push

    for tx, tz in tree_positions:
        # Resolve primeiro para o bumper mais próximo do tronco, depois o outro
        d_front2 = (front_cx - tx)**2 + (front_cz - tz)**2
        d_rear2  = (rear_cx  - tx)**2 + (rear_cz  - tz)**2
        if d_front2 <= d_rear2:
            resolve_bumper_vs_trunk(front_cx, front_cz, tx, tz)
            # Atualizar centros após possível empurrão
            front_cx = new_x + forward_x * bumper_offset
            front_cz = new_z + forward_z * bumper_offset
            rear_cx  = new_x - forward_x * bumper_offset
            rear_cz  = new_z - forward_z * bumper_offset
            resolve_bumper_vs_trunk(rear_cx, rear_cz, tx, tz)
        else:
            resolve_bumper_vs_trunk(rear_cx, rear_cz, tx, tz)
            front_cx = new_x + forward_x * bumper_offset
            front_cz = new_z + forward_z * bumper_offset
            rear_cx  = new_x - forward_x * bumper_offset
            rear_cz  = new_z - forward_z * bumper_offset
            resolve_bumper_vs_trunk(front_cx, front_cz, tx, tz)

    return new_x, new_z
    
def update_camera_movement():
    """Serve apenas para a câmara livre"""
    if camera.follow_vehicle or camera.inside_vehicle:
        return

    move_speed = 0.1
    rad = math.radians(camera.yaw)

    #Moviemento Horizontal
    if GLUT_KEY_UP in special_keys_pressed:
        camera.x += math.sin(rad) * move_speed
        camera.z -= math.cos(rad) * move_speed

    if GLUT_KEY_DOWN in special_keys_pressed:
        camera.x -= math.sin(rad) * move_speed
        camera.z += math.cos(rad) * move_speed

    if GLUT_KEY_LEFT in special_keys_pressed:
        camera.x -= math.cos(rad) * move_speed
        camera.z -= math.sin(rad) * move_speed

    if GLUT_KEY_RIGHT in special_keys_pressed:
        camera.x += math.cos(rad) * move_speed
        camera.z += math.sin(rad) * move_speed
    
    #Movimento Vertical
    if 'R' in keys_pressed:
        camera.y += move_speed  # sobe
    if 'F' in keys_pressed:
        camera.y -= move_speed  # desce


def update_vehicle(dt):
    """Atualiza a posição e estado do veículo"""
    # Atualizar velocidade baseada nas teclas
    if 'w' in keys_pressed or 'W' in keys_pressed:
        vehicle.speed += 2.0 * dt
        if vehicle.speed > 8.0:
            vehicle.speed = 8.0
    elif 's' in keys_pressed or 'S' in keys_pressed:
        vehicle.speed -= 2.0 * dt
        if vehicle.speed < -4.0:
            vehicle.speed = -4.0
    else:
        # Desaceleração gradual
        vehicle.speed *= 0.9
        if abs(vehicle.speed) < 0.1:
            vehicle.speed = 0.0
    
    # Controlo do volante (a/d para virar)
    if 'a' in keys_pressed or 'A' in keys_pressed:
        vehicle.steering_angle += 60 * dt
        if vehicle.steering_angle > 30:
            vehicle.steering_angle = 30
    elif 'd' in keys_pressed or 'D' in keys_pressed:
        vehicle.steering_angle -= 60 * dt
        if vehicle.steering_angle < -30:
            vehicle.steering_angle = -30
    else:
        # Volante retorna ao centro
        vehicle.steering_angle *= 0.9
        if abs(vehicle.steering_angle) < 1.0:
            vehicle.steering_angle = 0.0
    
    # Atualizar direção do veículo baseada no volante (quando em movimento)
    if abs(vehicle.speed) > 0.1:
        turn_factor = vehicle.steering_angle / 30.0  # -1 a 1
        vehicle.angle += turn_factor * vehicle.speed * 18 * dt
    
    # Mover veículo
    if abs(vehicle.speed) > 0.1:
        rad_angle = math.radians(vehicle.angle)
        
        new_x = vehicle.x + math.sin(rad_angle) * vehicle.speed * dt
        new_z = vehicle.z + math.cos(rad_angle) * vehicle.speed * dt
        # Porta fechada é tratada em resolve_static_collisions com a espessura real da malha
            # Porta fechada é tratada em resolve_static_collisions com a espessura real da malha

        # Resolver colisões com paredes/árvores antes de aplicar posição
        new_x, new_z = resolve_static_collisions(new_x, new_z, rad_angle)

        vehicle.x = new_x
        vehicle.z = new_z

        # Rotação das rodas proporcional à velocidade
        wheel_radius_front = 0.22
        wheel_radius_rear = 0.28
        circumference_front = 2 * math.pi * wheel_radius_front
        #circumference_rear = 2 * math.pi * wheel_radius_rear
        
        # A rotação é baseada na distância percorrida
        distance = vehicle.speed * dt
        vehicle.wheel_rotation += (distance / circumference_front) * 360
        vehicle.wheel_rotation = vehicle.wheel_rotation % 360

    # Animar portas do veículo
    vehicle.left_door_open = animate_value(vehicle.left_door_open, vehicle.left_door_target, 2.5, dt)
    vehicle.right_door_open = animate_value(vehicle.right_door_open, vehicle.right_door_target, 2.5, dt)
    
    # Animar porta da garagem
    garage.door_open = animate_value(garage.door_open, garage.door_target, 1.5, dt)

def animate(timer_value):
    """Callback de animação"""
    dt = 0.016  # ~60 FPS
    
    update_vehicle(dt)
    update_camera_movement()

    
    glutPostRedisplay()
    glutTimerFunc(16, animate, 0)

# ========== CALLBACKS DE INTERAÇÃO ==========
def keyboard_down(key, x, y):
    """Callback quando uma tecla é pressionada"""
    key = key.decode('utf-8') if isinstance(key, bytes) else key
    
    if key == '\x1b':       # ESC
        try:
            glutLeaveMainLoop()
        except Exception:
            sys.exit(0)
    
    keys_pressed.add(key)
    
    # R e F para subir e descer a câmara livre
    if key == 'r' or key == 'R':
        keys_pressed.add('R')
    if key == 'f' or key == 'F':
        keys_pressed.add('F')

    
    # Controlo de portas
    if key == 'e' or key == 'E':
        vehicle.left_door_target = 1.0 - vehicle.left_door_target
    if key == 'q' or key == 'Q':
        vehicle.right_door_target = 1.0 - vehicle.right_door_target
    
    # Controlo da porta da garagem
    if key == 'g' or key == 'G':
        garage.door_target = 1.0 - garage.door_target
    
    # Controlo da câmara
    if key == 'c' or key == 'C':
        camera.follow_vehicle = not camera.follow_vehicle
        camera.inside_vehicle = False
    if key == 'v' or key == 'V':
        camera.inside_vehicle = not camera.inside_vehicle
        if camera.inside_vehicle:
            camera.follow_vehicle = False
    
    glutPostRedisplay()

def keyboard_up(key, x, y):
    """Callback quando uma tecla é libertada"""
    key = key.decode('utf-8') if isinstance(key, bytes) else key
    keys_pressed.discard(key)

    if key == 'r' or key == 'R':
        keys_pressed.discard('R')
    if key == 'f' or key == 'F':
        keys_pressed.discard('F')

def special_keys(key, x, y):
    """Controlo da câmara livre (setas movem a câmara)"""
    if camera.follow_vehicle or camera.inside_vehicle:
        return

    special_keys_pressed.add(key)
    
def special_keys_up(key, x, y):
    if key in special_keys_pressed:
        special_keys_pressed.discard(key)

def mouse_motion(x, y):
    if camera.follow_vehicle or camera.inside_vehicle:
        return

    sensitivity = 0.15

    center_x = WINDOW_WIDTH // 2
    center_y = WINDOW_HEIGHT // 2

    dx = x - center_x
    dy = y - center_y

    camera.yaw += dx * sensitivity
    camera.pitch -= dy * sensitivity

    camera.pitch = max(-89, min(89, camera.pitch))

    # Isto faz a câmara funcionar com trackpads
    if abs(dx) > 2 or abs(dy) > 2:
        glutWarpPointer(center_x, center_y)

    glutPostRedisplay()

# ========== INICIALIZAÇÃO E LOOP PRINCIPAL ==========
def init_gl():
    """Inicializa o OpenGL"""
    glClearColor(0.5, 0.7, 0.9, 1.0)  # Cor do céu
    glEnable(GL_DEPTH_TEST)
    
    # Configurar matriz de projeção
    glMatrixMode(GL_PROJECTION)
    gluPerspective(60.0, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    
    # Inicializar iluminação e texturas
    setup_lighting()
    init_textures()

def display():
    """Callback de display"""
    draw_scene()

def reshape(width, height):
    """Callback de reshape"""
    global WINDOW_WIDTH, WINDOW_HEIGHT
    WINDOW_WIDTH = width
    WINDOW_HEIGHT = height
    
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, width / height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def print_instructions():
    """Imprime instruções de controlo"""
    print("\n" + "="*60)
    print("CONTROLS - Controles da Aplicação")
    print("="*60)
    print("VEÍCULO:")
    print("  W/S          - Acelerar/Marcha Atrás")
    print("  A/D          - Virar à esquerda/direita (volante)")
    print("  Q            - Abrir/fechar porta esquerda")
    print("  E            - Abrir/fechar porta direita")
    print("\nCÂMARA:")
    print("  C            - Alternar modo seguir veículo")
    print("  V            - Alternar câmara interior do veículo")
    print("  Rato        - Rodar câmara livre")
    print("  Setas         - Controlar câmara livre")
    print("  R        - Sobe a câmara livre")
    print("  F        - Desce a câmara livre")
    print("\nGARAGEM:")
    print("  G            - Abrir/fechar porta da garagem")
    print("\nGERAL:")
    print("  ESC          - Sair")
    print("="*60 + "\n")

HUD_LINES = [
    "W/S  - Acelerar / marcha atrás",
    "A/D  - Virar volante",
    "Q/E  - Portas do carro",
    "",
    "Setas - Mover camara",
    "R/F  - Subir / descer camera",
    "Rato - Rodar câmara livre",
    "",
    "C    - Seguir veiculo",
    "V    - Câmara interior",
    "",
    "G    - Abrir/fechar portao",
    "",
    "ESC  - Sair"
]

def draw_hud():
    """Desenha texto de ajuda no canto superior direito"""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    glColor3f(1.0, 1.0, 1.0)
    start_x = WINDOW_WIDTH - 260
    start_y = WINDOW_HEIGHT - 20
    line_height = 16

    for idx, line in enumerate(HUD_LINES):
        y = start_y - idx * line_height
        glRasterPos2f(start_x, y)
        for char in line:
            glutBitmapCharacter(GLUT.GLUT_BITMAP_HELVETICA_12, ord(char))

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def main():
    """Função principal"""
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(WINDOW_TITLE.encode('utf-8'))
    glutSetCursor(GLUT_CURSOR_NONE)                      
    glutWarpPointer(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)   
    glutIgnoreKeyRepeat(1) 
    
    init_gl()
    
    print_instructions()
    
    # Registar callbacks
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard_down)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_keys)
    glutSpecialUpFunc(special_keys_up)
    glutTimerFunc(16, animate, 0)
    glutPassiveMotionFunc(mouse_motion)
    glutMotionFunc(mouse_motion)
    
    
    # Iniciar loop principal
    glutMainLoop()

if __name__ == "__main__":
    main()

