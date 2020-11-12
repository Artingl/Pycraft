import pyglet
from OpenGL.GL import *


class Water:
    def __init__(self, cubeHandler):
        self.transparent = cubeHandler.transparent
        self.time = {'still': TimeLoop(32), 'flow': TimeLoop(32)}
        self.coords = {'still': [], 'flow': []}
        self.still_faces = {}
        self.flow_faces = {}
        for i in range(32 - 1, -1, -1):
            y0 = i / 16
            y1 = (i + 1) / 16
            self.coords['still'] += [[0, y0, 1, y0, 1, y1, 0, y1]]
            y0 = i / 32
            y1 = (i + 1) / 32
            self.coords['flow'] += [[0, y0, 1, y0, 1, y1, 0, y1]]
        a, b = self.time['still'], self.time['flow']
        self.t = b, b, a, a, b, b
        a, b = self.coords['still'], self.coords['flow']
        self.c = b, b, a, a, b, b

    def update(self, dt):
        if self.time['still'].update(dt * 0.5):
            for face, i in self.still_faces.items():
                face.tex_coords = self.c[i][self.t[i].int]
        if self.time['flow'].update(dt):
            for face, i in self.flow_faces.items():
                face.tex_coords = self.c[i][self.t[i].int]

    def show(self, v, t, i):
        face = self.transparent.add(4, GL_QUADS, t, ('v3f', v), ('t2f', self.c[i][0]))
        faces = self.still_faces if i == 2 or i == 3 else self.flow_faces
        faces[face] = i
        return face


class TimeLoop:
    def __init__(self, duration):
        self.unit = 0
        self.int = 0
        self.duration = duration
        self.prev = 0

    def update(self, dt):
        self.unit += dt
        self.unit -= int(self.unit)
        self.int = int(self.unit * self.duration)
        if self.prev != self.int:
            self.prev = self.int
            return True
