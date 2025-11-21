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

# ========== CONFIGURAÇÕES GLOBAIS ==========
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_TITLE = "Projeto CG - Veículo e Garagem"

# Estados do veículo
class VehicleState:
    def __init__(self):
        self.x = 0.0
        self.z = 0.0
        self.angle = 0.0  # Direção do veículo
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
    cockpit_length = 1.6

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
    tiles_x = 10
    tiles_z = 10
    
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
        # Câmara livre (controlada pelo utilizador)
        glRotatef(camera.pitch, 1, 0, 0)
        glRotatef(camera.yaw, 0, 1, 0)
        glTranslatef(-camera.x, -camera.y, -camera.z)
    
    # Desenhar elementos da cena
    draw_floor()
    draw_garage()
    draw_vehicle()
    
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

        gate_half_width = 1.7      # adjust to match your gate mesh
        gate_z = -8.8
        gate_depth = 1.8

        if garage.door_open < 0.95:
            within_gate_width = abs(new_x) < gate_half_width
            crossing_gate_plane = gate_z - gate_depth <= new_z <= gate_z + gate_depth
            if within_gate_width and crossing_gate_plane and vehicle.speed > 0:
                new_z = gate_z + gate_depth
                vehicle.speed = 0.0

        vehicle.x = new_x
        vehicle.z = new_z

        # Rotação das rodas proporcional à velocidade
        wheel_radius_front = 0.22
        wheel_radius_rear = 0.28
        circumference_front = 2 * math.pi * wheel_radius_front
        circumference_rear = 2 * math.pi * wheel_radius_rear
        
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

def special_keys(key, x, y):
    """Callback para teclas especiais (setas)"""
    # Controlo da câmara livre
    if not camera.follow_vehicle and not camera.inside_vehicle:
        if key == GLUT_KEY_UP:
            camera.pitch -= 5
        elif key == GLUT_KEY_DOWN:
            camera.pitch += 5
        elif key == GLUT_KEY_LEFT:
            camera.yaw -= 5
        elif key == GLUT_KEY_RIGHT:
            camera.yaw += 5
    
    # Limitar pitch
    if camera.pitch > 90:
        camera.pitch = 90
    if camera.pitch < -90:
        camera.pitch = -90
    
    glutPostRedisplay()

def mouse_motion(x, y):
    """Callback para movimento do rato (controlo da câmara)"""
    if not camera.follow_vehicle and not camera.inside_vehicle:
        # Sensibilidade ajustável
        sensitivity = 0.5
        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2
        
        dx = (x - center_x) * sensitivity
        dy = (y - center_y) * sensitivity
        
        camera.yaw += dx
        camera.pitch -= dy
        
        # Limitar pitch
        if camera.pitch > 90:
            camera.pitch = 90
        if camera.pitch < -90:
            camera.pitch = -90
        
        # Resetar posição do rato para o centro (opcional)
        # glutWarpPointer(center_x, center_y)
    
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
    print("  W/S          - Acelerar/Desacelerar")
    print("  A/D          - Virar à esquerda/direita (volante)")
    print("  Q            - Abrir/fechar porta esquerda")
    print("  E            - Abrir/fechar porta direita")
    print("\nCÂMARA:")
    print("  C            - Alternar modo seguir veículo")
    print("  V            - Alternar câmara interior do veículo")
    print("  Setas        - Rotar câmara livre")
    print("  Rato         - Controlar câmara livre")
    print("\nGARAGEM:")
    print("  G            - Abrir/fechar porta da garagem")
    print("\nGERAL:")
    print("  ESC          - Sair")
    print("="*60 + "\n")

def main():
    """Função principal"""
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(WINDOW_TITLE.encode('utf-8'))
    
    init_gl()
    
    print_instructions()
    
    # Registar callbacks
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard_down)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_keys)
    glutTimerFunc(16, animate, 0)
    
    # Iniciar loop principal
    glutMainLoop()

if __name__ == "__main__":
    main()

