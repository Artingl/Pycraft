import math

import keyboard
from OpenGL.GL import *

from src.functions import normalize


class Player:
    def __init__(self, bl, gl, pos=(0, 0, 0), rot=(0, 0)):
        self.pos, self.rot = list(pos), list(rot)
        self.speed = 1.3
        self.flying = False
        self.gravity = 1.8
        self.jSpeed = (4 * self.gravity) ** .5
        self.tVel = 50
        self.blocks = bl
        self.dy = 0
        self.gl = gl

    def updatePlayer(self):
        glPushMatrix()
        glRotatef(self.rot[0], 1, 0, 0)
        glRotatef(self.rot[1], 0, 1, 0)
        glTranslatef(-self.pos[0],
                     -self.pos[1],
                     -self.pos[2])

    def jump(self):
        if not self.dy:
            self.dy = self.jSpeed * 0.9

    def updatePos(self, dt):
        DX, DY, DZ = 0, 0, 0
        s = dt * self.speed
        rotY = self.rot[1] / 180 * math.pi
        dx, dz = s * math.sin(rotY), s * math.cos(rotY)

        if keyboard.is_pressed("shift"):
            DY -= s
        if keyboard.is_pressed("space"):
            if not self.flying:
                self.jump()
            else:
                DY += s
        if keyboard.is_pressed("w"):
            DX += dx
            DZ -= dz
        if keyboard.is_pressed("s"):
            DX -= dx
            DZ += dz
        if keyboard.is_pressed("r"):
            self.pos = (35, 50, -25)
            return
        if keyboard.is_pressed("a"):
            DX -= dz
            DZ -= dx
        if keyboard.is_pressed("d"):
            DX += dz
            DZ += dx

        if dt < 0.2:
            dt /= 10
            DX /= 10
            DY /= 10
            DZ /= 10
            for i in range(10):
                self.move(dt, DX, DY, DZ)

    def move(self, dt, dx, dy, dz):
        if not self.flying:
            self.dy -= dt * self.gravity
            self.dy = max(self.dy, -self.tVel)
            dy += self.dy * dt

        x, y, z = self.pos
        self.pos = self.collide((x + dx, y + dy, z + dz))

    def collide(self, pos):
        if self.flying:
            return pos
        pad = 0.25
        p = list(pos)
        np = normalize(pos)
        for face in ((-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)):
            for i in (0, 1, 2):
                if not face[i]:
                    continue
                d = (p[i] - np[i]) * face[i]
                if d < pad:
                    continue
                for dy in (0, 1):
                    op = list(np)
                    op[1] -= dy
                    op[i] += face[i]
                    if tuple(op) in self.blocks:
                        p[i] -= (d - pad) * face[i]
                        if face[1]:
                            self.dy = 0
                        break
        return tuple(p)

    def mouse_motion(self, dx, dy):
        dx /= 8
        dy /= 8
        self.rot[0] += dy
        self.rot[1] += dx
        if self.rot[0] > 90:
            self.rot[0] = 90
        elif self.rot[0] < -90:
            self.rot[0] = -90

    def get_sight_vector(self):
        rotX, rotY = -self.rot[0] / 180 * math.pi, self.rot[1] / 180 * math.pi
        dx, dz = math.sin(rotY), -math.cos(rotY)
        dy, m = math.sin(rotX), math.cos(rotX)
        return dx * m, dy, dz * m

    def update(self):
        self.updatePlayer()
