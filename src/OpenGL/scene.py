import random
from random import randint

import pyglet
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtOpenGL
from pyglet.gl import *

from src.control.MouseAndKeyboard import MKEvent
from src.functions import flatten, cube_vertices, load_textures, grass_verts
from src.game.CubeHandler import CubeHandler
from src.game.Perlin import Perlin
from src.game.Player import Player


class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        self.mouseDown = None
        self.mkevent = MKEvent()
        self.parent = parent
        self.pause = False

        QtOpenGL.QGLWidget.__init__(self, parent)
        self.texture, self.texture_dir, self.block, self.ids = {}, {}, {}, []

    def getFocus(self):
        return self.parent.getFocus()

    def getCenter(self):
        return [self.parent.x() + self.parent.width() // 2, self.parent.y() + self.parent.height() // 2]

    def initializeGL(self):
        glClearColor(0.5, 0.7, 1, 1)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glAlphaFunc(GL_GEQUAL, 1)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_FOG)
        glHint(GL_FOG_HINT, GL_DONT_CARE)
        glFogi(GL_FOG_MODE, GL_LINEAR)

        gluPerspective(70, (self.width() / self.height()), 0.1, 50.0)

        self.opaque = pyglet.graphics.Batch()
        self.transparent = pyglet.graphics.Batch()
        load_textures(self)
        self.cubes = CubeHandler(self.opaque, self.block, self.opaque, ('leaves_oak', 'tall_grass', 'nocolor'))
        self.player = Player(self.cubes.cubes, self)
        self.reticle = None
        self.load_vertex_lists(self.width(), self.height())

    def resizeCGL(self):
        glViewport(0, 0, self.parent.width(), self.parent.height())

    def generateWorld(self):
        perlin = Perlin(randint(10000, 100000))
        size = 40  # 100
        hSize = size * 2
        maxPos = 0
        dPos = 2 ** 31

        for x in range(size):
            for z in range(size):
                y = perlin(x, z)
                self.cubes.add((x, -y, -z), 'grass')
                if random.randint(0, 60) == 1:
                    self.spawnTree(x, y, z)
                if random.random() < 0.2:
                    self.addGrass((x, 1 - y, -z))
                if size - y > maxPos:
                    maxPos = size - y
                if hSize - y < dPos:
                    dPos = hSize - y
                for i in range(1, hSize - y):
                    if i < 10 + randint(5, 10):
                        self.cubes.add((x, -i - y, -z), 'dirt')
                    else:
                        if randint(0, 35) == 1:
                            self.cubes.remove((x, -i - y, -z))
                            self.cubes.add((x, -i - y, -z), 'iron_ore')
                        elif randint(0, 15) == 1:
                            self.cubes.remove((x, -i - y, -z))
                            self.cubes.add((x, -i - y, -z), 'coal_ore')
                        else:
                            self.cubes.add((x, -i - y, -z), 'stone')
                        self.parent.updateGeneratingWorld(x, size)
        self.player.pos = [35, 50, -25]

        diam, lap, eme, red, gold = 0, 0, 0, 0, 0
        while diam < 40 and lap < 100 and eme < 25:
            x, y, z = randint(0, size), randint(dPos + dPos - randint(0, 10), dPos + dPos) - dPos, randint(0, size)

            self.cubes.remove((x, -y, -z))
            self.cubes.add((x, -y, -z), 'diamond_ore')

            x, y, z = randint(0, size), randint(dPos + dPos - randint(0, 10), dPos + dPos) - dPos, randint(0, size)

            self.cubes.remove((x, -y, -z))
            self.cubes.add((x, -y, -z), 'emerald_ore')

            x, y, z = randint(0, size), randint(dPos + dPos - randint(0, 10), dPos + dPos) - dPos, randint(0, size)

            self.cubes.remove((x, -y, -z))
            self.cubes.add((x, -y, -z), 'lapis_ore')

            x, y, z = randint(0, size), randint(dPos + dPos - randint(0, 10), dPos + dPos) - dPos, randint(0, size)

            self.cubes.remove((x, -y, -z))
            self.cubes.add((x, -y, -z), 'gold_ore')

            x, y, z = randint(0, size), randint(dPos + dPos - randint(0, 10), dPos + dPos) - dPos, randint(0, size)

            self.cubes.remove((x, -y, -z))
            self.cubes.add((x, -y, -z), 'redstone_ore')

            diam += 1
            lap += 1
            eme += 1
            red += 1
            gold += 1

        '''for x in range(size):
            for z in range(size):
                self.cubes.remove((x, (size - maxPos), -z))
                self.cubes.add((x, (size - maxPos), -z), 'bedrock')'''

        for cube in self.cubes.cubes.values():
            self.cubes.updateCube(cube)

    def spawnTree(self, x, y, z):
        h = randint(5, 7)
        for i in range(1, h):
            self.cubes.add((x, -y + i, -z), 'log_oak')
        for i in range(round(h / 1.5), h):
            for j in range(-2, 3):
                for k in range(-2, 3):
                    if j == -2 and k == -2 or j == -2 and k == 2 or j == 2 and k == 2 or j == 2 and k == -2:
                        if randint(0, 6) != 1:
                            self.cubes.add((x + j, -y + i, -z + k), 'leaves_oak')
                    else:
                        self.cubes.add((x + j, -y + i, -z + k), 'leaves_oak')
        for i in range(h, h + 1):
            for j in range(-1, 2):
                for k in range(-1, 2):
                    self.cubes.add((x + j, -y + i, -z + k), 'leaves_oak')
        cl = 2
        for i in range(h + 1, h + 2):
            for j in range(-1, 2):
                for k in range(-1, 2):
                    if cl % 2 != 0:
                        self.cubes.add((x + j, -y + i, -z + k), 'leaves_oak')
                    cl += 1
        self.cubes.add((x, -y + h + 1, -z), 'leaves_oak')

    def addGrass(self, pos):
        # self.cubes.add(pos, 'nocolor')
        v = grass_verts(pos)
        tex = self.texture['tall_grass']
        for i in v:
            self.opaque.add(4, GL_QUADS, tex, ('v3f', i), ('t2f', (0, 0, 1, 0, 1, 1, 0, 1)))

    def load_vertex_lists(self, w, h):
        x, y = w / 2, h / 2
        m = 10
        if self.reticle: self.reticle.delete()
        self.reticle = pyglet.graphics.vertex_list(4, ('v2f', (x - m, y, x + m, y, x, y - m, x, y + m)),
                                                   ('c3f', (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)))
        self.water = pyglet.graphics.vertex_list(4, ('v2f', (0, 0, w, 0, w, h, 0, h)), ('c4f', [0.15, 0.3, 1, 0.5] * 4))

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.7, 1, 1))
        glFogf(GL_FOG_START, 60)
        glFogf(GL_FOG_END, 120)
        self.mkevent.update(self)
        if self.pause:
            return
        self.player.update()
        self.draw()

        block = self.cubes.hitTest(self.player.pos, self.player.get_sight_vector())[0]
        if block and not self.player.flying:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glColor3d(0, 0, 0)
            pyglet.graphics.draw(24, GL_QUADS, ('v3f/static', flatten(cube_vertices(block, 0.52))))
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            glColor3d(1, 1, 1)

        glPopMatrix()
        self.reticle.draw(GL_LINES)

    def draw(self):
        glEnable(GL_ALPHA_TEST)
        self.opaque.draw()
        glDisable(GL_ALPHA_TEST)
        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
        self.transparent.draw()
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        self.transparent.draw()
