import os
import platform
import time
from random import randint

import psutil
from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPixmap, QPainter, QIcon, QBrush, QColor
from PyQt5.QtWidgets import QLabel, QPushButton, QWidget, QTextEdit
from src.OpenGL.scene import GLWidget
from src.functions import translateSeed
from src.game.Biomes import getBiomeByTemp
from src.settings import Settings
from src.styles import buttonStyle, MainWindowStyle, textAreaStyle


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.pauseMenuObjs = []
        self.setGeometry(100, 100, 1280, 720)
        self.setWindowTitle('Pycraft')
        self.setStyleSheet(MainWindowStyle)
        self.setWindowIcon(QIcon("../ui/icon.jfif"))
        self.setFocus()

        self.settings = Settings()
        self.dbFileName = "../settings.db"
        self.fontDB = QtGui.QFontDatabase()
        self.fontDB.addApplicationFont("../ui/fonts/main.ttf")

        if not os.path.isfile(self.dbFileName):
            self.settings.saveAllSettings(self.dbFileName)

        self.settings.load(self.dbFileName)
        self.settings.update("playerName", "Player")
        self.blockLook = "Air"

        self.fps = 0
        self.maxFps = 0
        self.minFps = 2 ** 31
        self.start_time = 0
        self.hpPixmap = None
        self.canUpdate = False
        self.invList = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.loadGame()
        self.canUpdate = True

        self.selectedSection = 1
        self.hp = 15

        self.genTitle = None
        self.widg = QWidget()
        self.setCentralWidget(self.widg)

        self.initMenu()

        self.specialPressed = []
        self.hideItems = []
        self.itemsPos = []

        self.info = QLabel(self)
        self.info.setFont(QtGui.QFont("Minecraft Rus", 12))
        self.info.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.info.move(10, 10)
        self.info.setVisible(False)

        self.showInfo = False

    def getInventoryIdBlock(self):
        return self.invList[self.selectedSection - 1]

    def updateGeneratingWorld(self, t):
        proc = round(t[0] * 100 / t[1])
        if t[2]:
            res = f"Generating world... ({proc}% of 100%)"
        else:
            res = f"Loading terrain... ({proc}% of 100%)"

        if self.genTitle:
            self.genTitle.setText(res)
        self.repaint()

    def hideActiveWidget(self):
        if self.hideItems:
            for i in self.hideItems:
                if i:
                    i.destroy()
            self.hideItems = []
            self.itemsPos = []

        self.ShowMainMenu(True)

    def keyPressEvent(self, event):
        if event.key() == self.settings.pauseButton:
            if self.glWidget.gameStarted:
                self.setPause()
            else:
                self.hideActiveWidget()
        if event.key() == self.settings.flyingButton:
            self.glWidget.player.flying = not self.glWidget.player.flying
            self.glWidget.player.dy = 0
        if event.key() == self.settings.showInfo:
            self.showInfo = not self.showInfo
        if event.key() == self.settings.inventoryButton:
            self.showInventory()
        if event.key() == self.settings.selectInventoryCell1:
            self.selectedSection = 1
        if event.key() == self.settings.selectInventoryCell2:
            self.selectedSection = 2
        if event.key() == self.settings.selectInventoryCell3:
            self.selectedSection = 3
        if event.key() == self.settings.selectInventoryCell4:
            self.selectedSection = 4
        if event.key() == self.settings.selectInventoryCell5:
            self.selectedSection = 5
        if event.key() == self.settings.selectInventoryCell6:
            self.selectedSection = 6
        if event.key() == self.settings.selectInventoryCell7:
            self.selectedSection = 7
        if event.key() == self.settings.selectInventoryCell8:
            self.selectedSection = 8
        if event.key() == self.settings.selectInventoryCell9:
            self.selectedSection = 9

    def update(self):
        if not self.canUpdate:
            return
        self.start_time = time.time()

        # Menu
        self.glWidget.setGeometry(0, 0, self.width(), self.height())
        self.glWidget.resizeCGL()
        if self.glWidget.pause:
            if self.pauseMenuObjs:
                self.pauseMenuObjs[1].move(self.width() // 2 - self.pauseMenuObjs[1].width() // 2, self.height() // 9)
                self.pauseMenuObjs[2].move(self.width() // 2 - (self.pauseMenuObjs[2].width() // 2),
                                           self.height() // 2 - (self.pauseMenuObjs[2].height() // 2) - 60)
                self.pauseMenuObjs[3].move(self.pauseMenuObjs[2].x(),
                                           self.pauseMenuObjs[2].y() + 60)

            self.bg.resize(self.width(), self.height())
            self.btnGen.move(self.width() // 2 - (self.btnGen.width() // 2),
                             self.height() // 2 - (self.btnGen.height() // 2))
            self.btnSet.move(self.width() // 2 - (self.btnSet.width() // 2),
                             self.height() // 2 - (self.btnSet.height() // 2) + 60)
            self.logo.move(self.width() // 2 - 381 // 2, self.height() // 9)
            if self.genTitle:
                self.genTitle.setGeometry(self.width() // 2 - 200, self.height() // 2 - 50, 400, 100)

        if self.itemsPos:
            for i in self.itemsPos:
                obj, pos = i
                if pos[0]:
                    eval(pos[0])
                obj.setGeometry(eval(pos[1]), eval(pos[2]), eval(pos[3]), eval(pos[4]))

        # Game
        if not self.glWidget.gameStarted:
            return
        self.glWidget.updateGL()

        self.info.setVisible(self.showInfo)
        if self.showInfo:
            pPos = list(self.glWidget.player.pos)
            pPos[0] = round(pPos[0], 3)
            pPos[1] = round(pPos[1], 3)
            pPos[2] = round(pPos[2], 3)

            pid = os.getpid()
            py = psutil.Process(pid)
            memoryUse = py.memory_info()[0] / 2. ** 30

            biome = getBiomeByTemp(self.glWidget.world.perlinBiomes(pPos[0], pPos[2]) * 3)
            proc = round(self.glWidget.chunksLoaded * 100 / self.glWidget.world.qLen)
            msg = (f"\n\nThe world is now being generated ({proc}% of 100%)! The game may freeze"
                   if not self.glWidget.world.stopThisShit else "")

            self.info.setText(f"FPS: {self.fps} (Max FPS: {self.maxFps}, Min FPS: {self.minFps}, "
                              f"loaded chunks: {self.glWidget.chunksLoaded}, "
                              f"loaded blocks: {self.glWidget.blocksLoaded})\n"
                              f"Biome: {biome}\n"
                              f"Looking at: {self.blockLook}\n"

                              f"X Y Z: {pPos[0]}  {pPos[1]}  {pPos[2]}, "
                              f"(Flying mode: {'on' if self.glWidget.player.flying else 'off'})\n"

                              f"World seed: {self.settings.seed}, FOV: {self.settings.FOV}\n"

                              f"Mountains height: {self.settings.mountainsHeight}, Chunk size: "
                              f"{self.settings.chunkSize}\n"

                              f"Max world height: {self.settings.maxWorldHeight}, Max World size: "
                              f"{self.settings.maxWorldSize}\n"

                              f"Render distance: {self.settings.renderDistance}\n\n"

                              f"OS: {platform.uname().system} {platform.uname().release} {platform.architecture()[0]}\n"

                              f"Usage CPU: {psutil.cpu_percent()} ({platform.uname().machine})\n"

                              f"Usage RAM: {round(memoryUse * 1024, 1)} MB ({psutil.virtual_memory().percent}%/100%)\n"
                              f"{msg}")
            self.info.raise_()
            self.info.setStyleSheet("background-color: black; color: white; text-shadow: 3px 3px #3F3F3F;")
            self.info.adjustSize()
        if self.glWidget.pause:
            if self.pauseMenuObjs:
                self.glWidget.setVisible(True)
                pm = QPixmap(self.glWidget.grabFrameBuffer())
                painter = QPainter(pm)
                painter.fillRect(QRect(0, 0, pm.width(), pm.height()), QBrush(QColor(0, 0, 0, 200)))
                painter.end()
                self.pauseMenuObjs[0].resize(self.width(), self.height())
                self.pauseMenuObjs[0].setPixmap(pm)

        try:
            self.fps = round(1.0 / (time.time() - self.start_time))
            if self.fps > self.maxFps:
                self.maxFps = self.fps
            if self.fps < self.minFps:
                self.minFps = self.fps
        except ZeroDivisionError or ValueError:
            pass

        if self.glWidget.pause:
            self.inventory.move(-100, -100)
            self.inventorySel.move(-100, -100)
            self.glWidget.setCursor(Qt.ArrowCursor)
        else:
            self.SetPixmapInventory()
            self.updateHp()
            self.inventory.setGeometry(self.width() // 2 - 182, self.height() - 50, 364, 44)
            self.inventorySel.setGeometry(self.width() // 2 - 182 + (40 * (self.selectedSection - 1) + 2),
                                          self.height() - 48, 40, 40)
            self.glWidget.setCursor(Qt.BlankCursor)

    def showInventory(self):
        pass  # print(self.glWidget.QTInventoryTextures)

    def updateHp(self):
        if not self.hpPixmap:
            return

        curr = 0
        for i in range(self.hp):
            if i % 2 == 0:
                curr += 1
                self.hpPixmap[curr].setPixmap(QPixmap("../ui/textures/hp.png"))
            else:
                self.hpPixmap[curr].setPixmap(QPixmap("../ui/textures/halfhp.png"))

    def SetPixmapInventory(self):
        px = self.invPixmap
        painter = QPainter(px)
        for i in self.invList:
            if i in self.glWidget.QTInventoryTextures:
                painter.drawPixmap(44 // 2 - 8 + (40 * (i - 1) + 2),
                                   44 // 2 - 8, 16, 16,
                                   self.glWidget.QTInventoryTextures[i])
        painter.end()
        self.inventory.setPixmap(px)

    def loadGame(self):
        self.glWidget = GLWidget(self)
        self.glWidget.setGeometry(0, 0, self.width(), self.height())
        self.glWidget.pause = True

        self.invPixmap = QPixmap("../ui/textures/inventory.png")
        self.inventory = QLabel(self)
        self.inventory.setPixmap(self.invPixmap)
        self.inventory.move(-100, -100)

        self.inventorySel = QLabel(self)
        self.inventorySel.setPixmap(QPixmap("../ui/textures/inventorySel.png"))
        self.inventorySel.move(-100, -100)

        self.hpPixmap = []
        for i in range(10):
            lbl = QLabel()
            lbl.setPixmap(QPixmap("../ui/textures/hp.png"))
            lbl.setGeometry(self.width() // 2 - 182 + (i * 16), self.height() - 70, 12, 12)

            self.hpPixmap.append(lbl)

        QtGui.QCursor.setPos(self.x() + self.width() // 2, self.y() + self.height() // 2)
        self.initGlTimer()

    def initGlTimer(self):
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update)
        self.timer.start()

    def mousePressEvent(self, event):
        self.glWidget.mouseDown = event.button()

    def getFocus(self):
        return self.hasFocus()

    def setPause(self):
        self.glWidget.pause = not self.glWidget.pause
        if self.glWidget.pause:
            self.showPauseMenu()
        else:
            self.hidePauseMenu()

    def quitToTitle(self):
        self.canUpdate = False
        self.hidePauseMenu()
        self.glWidget.gameStarted = False
        self.glWidget.pause = True
        self.glWidget.setVisible(False)
        self.timer.deleteLater()
        self.glWidget.dels()
        self.glWidget.initializeGL(t=True)
        self.initGlTimer()
        self.widg.setVisible(True)
        self.ShowMainMenu(True)
        self.canUpdate = True

    def showPauseMenu(self):
        if not self.glWidget.gameStarted:
            return

        data = self.glWidget.grabFrameBuffer()
        self.glWidget.setVisible(False)
        self.pauseMenuObjs = []

        pm = QPixmap(data)
        painter = QPainter(pm)
        painter.fillRect(QRect(0, 0, pm.width(), pm.height()), QBrush(QColor(0, 0, 0, 200)))
        painter.end()

        bg = QLabel(self)
        bg.setPixmap(pm)
        bg.resize(self.width(), self.height())
        bg.show()

        titleLbl = QLabel(self)
        titleLbl.setFont(QtGui.QFont("Minecraft Rus", 12))
        titleLbl.setText("Game menu")
        titleLbl.setStyleSheet("color: #f2f2f2;")
        titleLbl.setAlignment(Qt.AlignCenter)
        titleLbl.resize(400, 48)
        titleLbl.move(self.width() // 2 - titleLbl.width() // 2, self.height() // 9)
        titleLbl.show()

        btnTex = QPushButton(self)
        btnTex.setText("Back to game")
        btnTex.setFont(QtGui.QFont("Minecraft Rus", 12))
        btnTex.resize(400, 40)
        btnTex.setStyleSheet(buttonStyle)
        btnTex.clicked.connect(self.setPause)
        btnTex.move(self.width() // 2 - (btnTex.width() // 2),
                    self.height() // 2 - (btnTex.height() // 2) - 60)
        btnTex.show()

        btnQ = QPushButton(self)
        btnQ.setText("Quit to title")
        btnQ.setFont(QtGui.QFont("Minecraft Rus", 12))
        btnQ.resize(400, 40)
        btnQ.setStyleSheet(buttonStyle)
        btnQ.clicked.connect(self.quitToTitle)
        btnQ.move(btnTex.x(), btnTex.y() + 60)
        btnQ.show()

        self.pauseMenuObjs.append(bg)
        self.pauseMenuObjs.append(titleLbl)
        self.pauseMenuObjs.append(btnTex)
        self.pauseMenuObjs.append(btnQ)
        self.repaint()

    def hidePauseMenu(self):
        for i in self.pauseMenuObjs:
            if i:
                i.destroy()

        self.setFocus()
        self.glWidget.setVisible(True)

    def ShowMainMenu(self, t):
        self.btnGen.setVisible(t)
        self.btnSet.setVisible(t)
        self.logo.setVisible(t)

    def initWorldGen(self):
        self.ShowMainMenu(False)

        self.genTitle = QLabel(self)
        self.genTitle.setText("Generating world... (0% of 100%)")
        self.genTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.genTitle.setFont(QtGui.QFont("Minecraft Rus", 14))
        self.genTitle.setStyleSheet("color: white")
        self.genTitle.setGeometry(self.width() // 2 - 300, self.height() // 2 - 50, 600, 100)
        self.genTitle.setVisible(True)

    def initMenu(self):
        self.bg = QLabel(self.widg)
        self.bg.resize(self.width(), self.height())
        self.bg.setStyleSheet("background: url('../ui/textures/bg.png') repeat;")

        self.logo = QLabel(self.widg)
        self.logo.setPixmap(QPixmap("../ui/textures/logo.png"))
        self.logo.move(self.width() // 2 - 381 // 2, self.height() // 9)

        self.btnGen = QPushButton(self.widg)
        self.btnGen.setText("Create new world")
        self.btnGen.setFont(QtGui.QFont("Minecraft Rus", 12))
        self.btnGen.resize(400, 40)
        self.btnGen.clicked.connect(self.gen)
        self.btnGen.setStyleSheet(buttonStyle)

        self.btnSet = QPushButton(self.widg)
        self.btnSet.setText("Settings")
        self.btnSet.setFont(QtGui.QFont("Minecraft Rus", 12))
        self.btnSet.resize(400, 40)
        self.btnSet.setStyleSheet(buttonStyle)
        self.btnSet.clicked.connect(self.showSettings)

    def addRenderDistance(self):
        if self.settings.renderDistance < 96:
            self.settings.update("renderDistance", self.settings.renderDistance + 8)
        else:
            self.settings.update("renderDistance", 8)

    def addFOV(self):
        if self.settings.FOV < 120:
            self.settings.update("FOV", self.settings.FOV + 10)
        else:
            self.settings.update("FOV", 30)

    def setSeed(self, obj):
        self.settings.update("seed", translateSeed(obj.toPlainText()))

    def showSettings(self):
        self.ShowMainMenu(False)

        btnRndr = QPushButton(self)
        btnRndr.setText("Render distance: 32")
        btnRndr.setFont(QtGui.QFont("Minecraft Rus", 12))
        btnRndr.setStyleSheet(buttonStyle)
        btnRndr.clicked.connect(self.addRenderDistance)
        self.itemsPos.append((btnRndr, ["obj.setText(f\"Render distance: {self.settings.renderDistance}\")",

                                        "(self.width() // 2) - 400",
                                        "(self.height() // 2) - 200",
                                        "400",
                                        "40",
                                        ]))
        btnRndr.show()

        btnFOV = QPushButton(self)
        btnFOV.setText("FOV: 32")
        btnFOV.setFont(QtGui.QFont("Minecraft Rus", 12))
        btnFOV.setStyleSheet(buttonStyle)
        btnFOV.clicked.connect(self.addFOV)
        self.itemsPos.append((btnFOV, ["obj.setText(f\"FOV: {self.settings.FOV}\")",

                                       "(self.width() // 2) - 400",
                                       "(self.height() // 2) - 120",
                                       "400",
                                       "40",
                                       ]))
        btnFOV.show()

        lblWrldSeed = QLabel(self)
        lblWrldSeed.setText("Seed for the world generator")
        lblWrldSeed.setFont(QtGui.QFont("Minecraft Rus", 12))
        lblWrldSeed.setStyleSheet("color: #cccccc;")
        self.itemsPos.append((lblWrldSeed, ["",

                                            "(self.width() // 2) + 40",
                                            "(self.height() // 2) - 234",
                                            "400",
                                            "40",
                                            ]))
        lblWrldSeed.show()

        wrldSeed = QTextEdit(self)
        wrldSeed.setPlainText(str(translateSeed(str(self.settings.seed))))
        wrldSeed.setFont(QtGui.QFont("Minecraft Rus", 12))
        wrldSeed.setStyleSheet(textAreaStyle)
        self.itemsPos.append((wrldSeed, ['self.setSeed(obj)'
                                         '',

                                         "(self.width() // 2) + 40",
                                         "(self.height() // 2) - 200",
                                         "400",
                                         "40",
                                         ]))
        wrldSeed.show()

        self.hideItems.append(btnRndr)
        self.hideItems.append(btnFOV)
        self.hideItems.append(lblWrldSeed)
        self.hideItems.append(wrldSeed)
        self.repaint()

    def gen(self):
        self.initWorldGen()
        self.glWidget.pause = False
        self.glWidget.gameStarted = True
        self.widg.setVisible(False)
        self.glWidget.setVisible(True)
        self.genTitle.destroy()
        self.setFocus()
