from random import randint

import pyglet
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PyQt5 import QtOpenGL
from pyglet.gl import *

from src.control.MouseAndKeyboard import MKEvent
from src.functions import flatten, cube_vertices, load_textures, load_vertex_lists
from src.game.CubeHandler import CubeHandler
from src.game.Player import Player
from src.game.WorldGeneration import WorldGeneration
from src.settings import seed, renderDistance, chunkSize, FOV


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
        gluPerspective(FOV, (self.width() / self.height()), 0.1, renderDistance)

        self.opaque = pyglet.graphics.Batch()
        self.transparent = pyglet.graphics.Batch()
        load_textures(self)
        self.cubes = CubeHandler(self.opaque, self.block, self.opaque, ('leaves_oak', 'tall_grass', 'nocolor'))
        self.player = Player(self.cubes.cubes, self)
        self.reticle = None
        load_vertex_lists(self, self.width(), self.height())

        self.world = WorldGeneration(self)

    def resizeCGL(self):
        glViewport(0, 0, self.parent.width(), self.parent.height())

    def getInventoryIdBlock(self):
        return self.parent.getInventoryIdBlock()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
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
                self.reticle.draw(GL_LINES)
                return

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
