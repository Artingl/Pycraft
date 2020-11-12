import time
from random import randint

import pyglet
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PyQt5 import QtOpenGL
from pyglet.gl import *

from src.control.MouseAndKeyboard import MKEvent
from src.functions import flatten, cube_vertices, load_textures, roundPos
from src.game.CubeHandler import CubeHandler
from src.game.Player import Player
from src.game.WorldGeneration import WorldGeneration
from src.settings import seed, renderDistance, chunkSize, FOV, maxWorldSize


class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        self.mouseDown = None
        self.mkevent = MKEvent()
        self.parent = parent
        self.pause = False
        self.gameStarted = False
        self.genTimer = 1
        self.chunksLoaded = 0
        self.blocksLoaded = 0

        QtOpenGL.QGLWidget.__init__(self, parent)
        self.texture, self.texture_dir, self.block, self.ids, self.QTInventoryTextures = {}, {}, {}, [], {}
        self.cubes, self.player, self.transparent, self.opaque, self.world, self.reticle, self.drawFluid = \
            None, None, None, None, None, None, None

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

        glReadBuffer(GL_FRONT)
        gluPerspective(FOV, (self.width() / self.height()), 0.1, renderDistance * 10)

        load_textures(self)
        self.transparent = pyglet.graphics.Batch()
        self.opaque = pyglet.graphics.Batch()
        self.cubes = CubeHandler(self.opaque, self.block, self.opaque, ('leaves_taiga', 'leaves_oak', 'tall_grass', 'nocolor'), self)
        self.player = Player(self.cubes.cubes, self)
        self.world = WorldGeneration(self)

    def vertexList(self):
        x, y, w, h = self.width() / 2, self.height() / 2, self.width(), self.height()
        self.reticle = pyglet.graphics.vertex_list(4, ('v2f', (x - 10, y, x + 10, y, x, y - 10, x, y + 10)),
                                                   ('c3f', (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)))
        self.drawFluid = pyglet.graphics.vertex_list(4, ('v2f', (0, 0, w, 0, w, h, 0, h)), ('c4f', [0.15, 0.3, 1, 0.5] * 4))

    def resizeCGL(self):
        self.vertexList()
        glViewport(0, 0, self.parent.width(), self.parent.height())

    def getInventoryIdBlock(self):
        return self.parent.getInventoryIdBlock()

    def paintGL(self):
        self.cubes.water.update(0.01)
        self.cubes.lava.update(0.01)

        cubes = self.cubes.cubes
        pos = roundPos(self.player.pos)
        self.player.swim = pos in cubes and (cubes[pos].name == 'water' or cubes[pos].name == 'lava')

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if self.player.swim:
            glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0, 0, 0, 1))
            glFogf(GL_FOG_START, 10)
            glFogf(GL_FOG_END, 35)
        else:
            glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.7, 1, 1))
            glFogf(GL_FOG_START, 60)
            glFogf(GL_FOG_END, 120)
        if self.gameStarted:
            self.world.generateChunk()
            self.genTimer += 1

            self.mkevent.update(self)
            self.player.update()
            self.draw()
            if self.pause:
                glPopMatrix()
                return

            block = self.cubes.hitTest(self.player.pos, self.player.get_sight_vector())[0]
            if block and (cubes[block].name != 'water' or cubes[block].name != 'lava'):
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                glColor3d(0, 0, 0)
                pyglet.graphics.draw(24, GL_QUADS, ('v3f/static', flatten(cube_vertices(block, 0.50))))
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                glColor3d(1, 1, 1)

            glPopMatrix()

            self.reticle.draw(GL_LINES)
            if self.player.swim:
                self.drawFluid.draw(GL_POLYGON)

    def draw(self):
        glEnable(GL_ALPHA_TEST)
        self.opaque.draw()
        glDisable(GL_ALPHA_TEST)
        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
        self.transparent.draw()
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        self.transparent.draw()
