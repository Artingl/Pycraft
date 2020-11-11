import os
import time

import platform
import psutil

from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPixmap, QPainter, QIcon, QBrush, QColor
from PyQt5.QtWidgets import QLabel, QPushButton, QWidget

from src.OpenGL.scene import GLWidget
from src.settings import seed, FOV, mountainsHeight, chunkSize, maxWorldHeight, maxWorldSize, renderDistance, \
    pauseButton, flyingButton, inventoryButton, selectInventoryCell9, selectInventoryCell8, selectInventoryCell7, \
    selectInventoryCell6, selectInventoryCell5, selectInventoryCell4, selectInventoryCell3, selectInventoryCell2, \
    selectInventoryCell1
from src.styles import buttonStyle, MainWindowStyle


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.pauseMenuObjs = []
        self.setGeometry(100, 100, 1280, 720)
        self.setWindowTitle('Pycraft')
        self.setStyleSheet(MainWindowStyle)
        self.setWindowIcon(QIcon("../ui/icon.jfif"))
        self.setFocus()

        self.fontDB = QtGui.QFontDatabase()
        self.fontDB.addApplicationFont("../ui/fonts/main.ttf")

        self.fps = 0
        self.maxFps = 0
        self.minFps = 2**31
        self.start_time = 0
        self.hpPixmap = None
        self.loadGame()

        self.selectedSection = 1
        self.invList = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.hp = 15

        self.genTitle = None
        self.widg = QWidget()
        self.setCentralWidget(self.widg)

        self.initMenu()

        self.specialPressed = []

        self.info = QLabel(self)
        self.info.setFont(QtGui.QFont("Minecraft Rus", 12))
        self.info.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.info.move(10, 10)

    def getInventoryIdBlock(self):
        return self.invList[self.selectedSection - 1]

    def updateGeneratingWorld(self, t):
        proc = round(t[0] * 100 / t[1])
        if t[2]:
            res = f"Generating world... ({proc}% of 100%)"
        else:
            res = f"Loading terrain... ({proc}% of 100%)"
            # if proc > 97:
            #    self.widg.children().remove(self.genTitle)
            #     self.genTitle = None

        # print(res)
        if self.genTitle:
            self.genTitle.setText(res)
        self.repaint()

    def keyPressEvent(self, event):
        if event.key() == pauseButton:
            self.setPause()
        if event.key() == flyingButton:
            self.glWidget.player.flying = not self.glWidget.player.flying
            self.glWidget.player.dy = 0
        if event.key() == inventoryButton:
            self.showInventory()
        if event.key() == selectInventoryCell1:
            self.selectedSection = 1
        if event.key() == selectInventoryCell2:
            self.selectedSection = 2
        if event.key() == selectInventoryCell3:
            self.selectedSection = 3
        if event.key() == selectInventoryCell4:
            self.selectedSection = 4
        if event.key() == selectInventoryCell5:
            self.selectedSection = 5
        if event.key() == selectInventoryCell6:
            self.selectedSection = 6
        if event.key() == selectInventoryCell7:
            self.selectedSection = 7
        if event.key() == selectInventoryCell8:
            self.selectedSection = 8
        if event.key() == selectInventoryCell9:
            self.selectedSection = 9

    def update(self):
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
            self.btnTex.move(self.width() // 2 - (self.btnTex.width() // 2),
                             self.height() // 2 - (self.btnTex.height() // 2) + 60)
            self.logo.move(self.width() // 2 - 381 // 2, self.height() // 9)
            if self.genTitle:
                self.genTitle.setGeometry(self.width() // 2 - 200, self.height() // 2 - 50, 400, 100)

        # Game
        if not self.glWidget.gameStarted:
            return
        self.start_time = time.time()
        self.glWidget.updateGL()

        pPos = list(self.glWidget.player.pos)
        pPos[0] = round(pPos[0], 3)
        pPos[1] = round(pPos[1], 3)
        pPos[2] = round(pPos[2], 3)

        pid = os.getpid()
        py = psutil.Process(pid)
        memoryUse = py.memory_info()[0] / 2. ** 30

        self.info.setText(f"FPS: {self.fps} (Max FPS: {self.maxFps}, Min FPS: {self.minFps}, "
                          f"loaded chunks: {self.glWidget.chunksLoaded}, "
                          f"loaded blocks: {self.glWidget.blocksLoaded})\n"
                          
                          f"X Y Z: {pPos[0]}  {pPos[1]}  {pPos[2]}, "
                          f"(Flying mode: {'yes' if self.glWidget.player.flying else 'no'})\n "
                          
                          f"World seed: {seed}, FOV: {FOV}\n"
                          
                          f"Mountains height: {mountainsHeight}, Chunk size: {chunkSize}\n"
                          
                          f"Max world height: {maxWorldHeight}, Max World size: {maxWorldSize}\n"
                          
                          f"Render distance: {renderDistance}\n\n"
                          
                          f"OS: {platform.uname().system} {platform.uname().release} {platform.architecture()[0]}\n"
                          
                          f"Usage CPU: {psutil.cpu_percent()} ({platform.uname().machine})\n"
                          
                          f"Usage RAM: {round(memoryUse * 1024, 1)} MB ({psutil.virtual_memory().percent}%/100%)\n")
        self.info.raise_()
        self.info.setStyleSheet("background-color: black; color: white;")
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

        try:
            self.fps = round(1.0 / (time.time() - self.start_time))
            if self.fps > self.maxFps:
                self.maxFps = self.fps
            if self.fps < self.minFps:
                self.minFps = self.fps
        except ZeroDivisionError or ValueError:
            pass

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
        self.hidePauseMenu()
        self.glWidget.gameStarted = False
        self.glWidget.pause = True
        self.hideOrShowMainMenu(True)

    def showPauseMenu(self):
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

    def hideOrShowMainMenu(self, t):
        self.btnGen.setVisible(t)
        self.logo.setVisible(t)

    def initWorldGen(self):
        self.hideOrShowMainMenu(False)

        self.genTitle = QLabel(self.widg)
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

        self.btnTex = QPushButton(self.widg)
        self.btnTex.setText("Texture packs")
        self.btnTex.setFont(QtGui.QFont("Minecraft Rus", 12))
        self.btnTex.resize(400, 40)
        self.btnTex.setStyleSheet(buttonStyle)
        self.btnTex.setVisible(False)

    def gen(self):
        self.initWorldGen()
        self.glWidget.pause = False
        self.glWidget.gameStarted = True
        self.widg.setVisible(False)
        self.setFocus()
