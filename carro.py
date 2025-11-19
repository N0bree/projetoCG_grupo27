from OpenGL.GL import *
from OpenGL.GLU import *
import math

class EstadoCarro:

    def __init__(self):
        self.x = 0.0
        self.z = 0.0
        self.veloc = 0.0
        self.ang_rodas = 0.0
        self.ang_volante = 0.0
        self.porta_esq = 0.0
        self.porta_dir = 0.0
        self._left_target = 0.0
        self._right_target = 0.0

    def atuaizar(self, dt):
        self.z += self.veloc * dt
        circulo = 2 * math.pi * 0.40            #   raio roda 0.40

        if circulo > 1e-6:                      #   evitar /0
            self.ang_rodas = (self.ang_rodas + (self.veloc * dt) / circulo * 360.0) % 360