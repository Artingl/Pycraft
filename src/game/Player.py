import math

import keyboard
from OpenGL.GL import *

from src.functions import roundPos


class Player:
    def __init__(self, bl, gl, pos=(0, 0, 0), rot=(0, 0)):
        self.pos, self.rot = list(pos), list(rot)
        self.speed = gl.parent.settings.playerMovingSpeed
        self.flyingSpeed = gl.parent.settings.playerFlyingSpeed
        self.flying = False
        self.gravity = gl.parent.settings.playerGravity
        self.jSpeed = gl.parent.settings.playerJumpSpeed
        self.tVel = 50
        self.blocks = bl
        self.dy = 0
        self.gl = gl
        self.swim = False

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
        if self.flying:
            s = dt * self.flyingSpeed
        else:
            s = dt * self.speed
        rotY = self.rot[1] / 180 * math.pi
        dx, dz = s * math.sin(rotY), s * math.cos(rotY)

        if keyboard.is_pressed("shift"):
            DY -= s
        if keyboard.is_pressed("space"):
            if not self.flying:
                if roundPos(self.pos) in self.gl.cubes.fluids:
                    self.dy = self.gl.parent.settings.playerJumpSpeed / 2
                else:
                    self.jump()
            else:
                DY += s
        if keyboard.is_pressed("w"):
            DX += dx
            DZ -= dz
        if keyboard.is_pressed("ctrl"):
            self.speed = self.gl.parent.settings.playerMovingSpeed + 0.5
        else:
            self.speed = self.gl.parent.settings.playerMovingSpeed / 1.5
        if keyboard.is_pressed("s"):
            DX -= dx
            DZ += dz
        if keyboard.is_pressed("r"):
            self.pos = self.gl.world.playerPos
            self.dy = 0
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

            if self.dy > 9.8:
                self.dy = 9.8

        x, y, z = self.pos
        self.pos = self.collide((x + dx, y + dy, z + dz))

    def collide(self, pos):
        if pos[1] < -80:
            self.dy = 0
            return self.gl.world.playerPos

        if self.flying:
            return pos

        p = list(pos)
        np = roundPos(pos)
        for face in ((-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)):
            for i in (0, 1, 2):
                if not face[i]:
                    continue
                d = (p[i] - np[i]) * face[i]
                pad = 0 if i == 1 and face[i] < 0 else 0.25
                if d < pad:
                    continue
                for dy in (0, 1):
                    op = list(np)
                    op[1] -= dy
                    op[i] += face[i]
                    if tuple(op) in self.gl.cubes.collidable:
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
